"""
API FastAPI para Vigilancia Epidemiológica — Brote Sarampión 2026
IGSS — Departamento de Medicina Preventiva — Sección de Epidemiología

Endpoints:
  POST /api/registro              → Guardar nuevo registro (público, desde formulario)
  GET  /api/registro/{id}         → Obtener registro individual (requiere API key)
  PUT  /api/registro/{id}         → Editar registro existente (requiere API key)
  GET  /api/registro/{id}/audit   → Historial de cambios (requiere API key)
  GET  /api/registros             → Listar registros (requiere API key)
  GET  /api/registros/count       → Contar registros
  POST /api/registros/upload      → Carga masiva desde Excel (requiere API key)
  GET  /api/export/excel          → Descargar como Excel (requiere API key)
  GET  /api/export/csv            → Descargar como CSV (requiere API key)
  GET  /api/health                → Health check
"""
import io
import csv
import re
import time
import hmac
import logging
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Query, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse

from config import ALLOWED_ORIGINS, API_SECRET_KEY, PORT, RATE_LIMIT_SECONDS, MAX_UPLOAD_SIZE_MB
from database import (
    init_db, insert_registro, get_registros, get_count, check_duplicate,
    get_registro_by_id, update_registro, delete_registro, bulk_insert_registros,
    init_audit_table, log_changes, get_audit_trail, search_registros,
    COLUMNS, EDITABLE_COLUMNS,
)
from mspas_queue import (
    init_mspas_tables, save_credentials, get_credentials,
    enqueue_record, enqueue_all_pending, get_queue, get_queue_counts,
    approve_records, update_estado, get_approved_for_submission,
    mark_sent, mark_error, mark_duplicate, mark_possible_duplicate,
    try_claim_for_submission, recover_stuck_submissions, get_status_by_id,
)

logger = logging.getLogger(__name__)

# ─── App ──────────────────────────────────────────────────
app = FastAPI(
    title="Vigilancia Sarampión - IGSS API",
    description="API de registro de casos sospechosos de sarampión",
    version="2.0.0",
    docs_url=None,   # Disable Swagger in production
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting por IP (en memoria — single worker)
_rate_limiter: dict[str, float] = {}
_RATE_LIMIT_CLEANUP_INTERVAL = 300  # Limpiar cada 5 min
_last_cleanup = time.time()


def _cleanup_rate_limiter():
    """Elimina entradas viejas del rate limiter para evitar memory leak."""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < _RATE_LIMIT_CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    cutoff = now - 60
    keys_to_remove = [k for k, v in _rate_limiter.items() if v < cutoff]
    for k in keys_to_remove:
        del _rate_limiter[k]


# ─── Validación de datos ──────────────────────────────────
VALID_CLASIFICACIONES = {"SOSPECHOSO", "CONFIRMADO", "DESCARTADO", "SUSPENDIDO", "CLÍNICO", "FALSO", "ERROR DIAGNÓSTICO"}
VALID_SEXO = {"M", "F", ""}
VALID_SI_NO = {"SI", "NO", "N/A", "N/S", ""}
MAX_FIELD_LENGTH = 500


def sanitize_value(val):
    """Sanitiza un valor de entrada."""
    if val is None:
        return ""
    s = str(val).strip()
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
    if len(s) > MAX_FIELD_LENGTH:
        s = s[:MAX_FIELD_LENGTH]
    return s


def validate_registro(data: dict) -> list[str]:
    """Valida los datos del registro. Retorna lista de errores."""
    errors = []

    if not data.get("registro_id"):
        errors.append("registro_id es requerido")

    clasif = data.get("clasificacion_caso", "")
    if clasif and clasif not in VALID_CLASIFICACIONES:
        errors.append(f"clasificacion_caso inválida: {clasif}")

    sexo = data.get("sexo", "")
    if sexo and sexo not in VALID_SEXO:
        errors.append(f"sexo inválido: {sexo}")

    semana = data.get("semana_epidemiologica", "")
    if semana:
        try:
            s = int(semana)
            if s < 1 or s > 53:
                errors.append(f"semana_epidemiologica fuera de rango: {s}")
        except ValueError:
            errors.append(f"semana_epidemiologica no es número: {semana}")

    for field in ("edad_anios", "edad_meses"):
        val = data.get(field, "")
        if val:
            try:
                n = int(val)
                if n < 0 or n > 150:
                    errors.append(f"{field} fuera de rango: {n}")
            except ValueError:
                errors.append(f"{field} no es número: {val}")

    return errors


def validate_registro_update(data: dict) -> list[str]:
    """Valida campos para actualización parcial (todos opcionales)."""
    errors = []

    clasif = data.get("clasificacion_caso", "")
    if clasif and clasif not in VALID_CLASIFICACIONES:
        errors.append(f"clasificacion_caso inválida: {clasif}")

    sexo = data.get("sexo", "")
    if sexo and sexo not in VALID_SEXO:
        errors.append(f"sexo inválido: {sexo}")

    semana = data.get("semana_epidemiologica", "")
    if semana:
        try:
            s = int(semana)
            if s < 1 or s > 53:
                errors.append(f"semana_epidemiologica fuera de rango: {s}")
        except ValueError:
            errors.append(f"semana_epidemiologica no es número: {semana}")

    for field in ("edad_anios", "edad_meses"):
        val = data.get(field, "")
        if val:
            try:
                n = int(val)
                if n < 0 or n > 150:
                    errors.append(f"{field} fuera de rango: {n}")
            except ValueError:
                errors.append(f"{field} no es número: {val}")

    return errors


# ─── Init DB ──────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    init_audit_table()
    init_mspas_tables()
    # Auto-recover records stuck in 'enviando' state (e.g. from crashed processes)
    recovered = recover_stuck_submissions()
    if recovered:
        logger.info(f"Recovered {recovered} stuck MSPAS submissions")
    print(f"Vigilancia Sarampión API v2.0 iniciada en puerto {PORT}")


# ─── Helpers ──────────────────────────────────────────────
def verify_api_key(x_api_key: str = Header(None)):
    """Verifica la API key con comparación timing-safe."""
    if not x_api_key or not hmac.compare_digest(x_api_key, API_SECRET_KEY):
        raise HTTPException(status_code=401, detail="API key inválida")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ─── Endpoints ────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "vigilancia-sarampion-igss",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "total_registros": get_count(),
    }


@app.post("/api/registro")
async def crear_registro(request: Request):
    """Recibe datos del formulario y los guarda en la DB."""
    ip = get_client_ip(request)

    _cleanup_rate_limiter()
    now = time.time()
    last = _rate_limiter.get(ip, 0)
    if now - last < RATE_LIMIT_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Debe esperar {RATE_LIMIT_SECONDS} segundos entre envíos",
        )

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    validation_errors = validate_registro(data)
    if validation_errors:
        raise HTTPException(status_code=400, detail="; ".join(validation_errors))

    afiliacion = sanitize_value(data.get("afiliacion", ""))
    fecha = sanitize_value(data.get("fecha_notificacion", ""))
    if afiliacion and fecha and check_duplicate(afiliacion, fecha):
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un registro para afiliación {afiliacion} con fecha {fecha}",
        )

    clean = {}
    for col in COLUMNS:
        clean[col] = sanitize_value(data.get(col, ""))

    try:
        registro_id = insert_registro(clean, ip=ip)
    except Exception:
        raise HTTPException(status_code=500, detail="Error al guardar el registro")

    _rate_limiter[ip] = now

    return {
        "success": True,
        "registro_id": registro_id,
        "message": "Registro guardado correctamente",
    }


# ─── Nuevos endpoints: Registro individual ────────────────

@app.get("/api/registro/{registro_id}")
def obtener_registro(registro_id: str, x_api_key: str = Header(None)):
    """Obtiene un registro individual por su ID. Requiere API key."""
    verify_api_key(x_api_key)

    reg = get_registro_by_id(registro_id)
    if not reg:
        raise HTTPException(status_code=404, detail=f"Registro {registro_id} no encontrado")

    return {"data": reg}


@app.put("/api/registro/{registro_id}")
async def actualizar_registro(registro_id: str, request: Request, x_api_key: str = Header(None)):
    """Edita un registro existente. Requiere API key.
    Solo enviar los campos que cambiaron.
    """
    verify_api_key(x_api_key)

    # Verificar que existe
    existing = get_registro_by_id(registro_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Registro {registro_id} no encontrado")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    if not data:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")

    # Validar campos
    validation_errors = validate_registro_update(data)
    if validation_errors:
        raise HTTPException(status_code=400, detail="; ".join(validation_errors))

    # Sanitizar solo campos editables
    clean = {}
    for col in data:
        if col in EDITABLE_COLUMNS:
            clean[col] = sanitize_value(data[col])

    if not clean:
        raise HTTPException(status_code=400, detail="Ningún campo editable proporcionado")

    # Audit trail
    ip = get_client_ip(request)
    log_changes(registro_id, existing, clean, usuario="portal", ip=ip)

    # Actualizar
    success = update_registro(registro_id, clean)
    if not success:
        raise HTTPException(status_code=500, detail="Error actualizando registro")

    return {
        "success": True,
        "registro_id": registro_id,
        "fields_updated": list(clean.keys()),
        "message": "Registro actualizado correctamente",
    }


@app.get("/api/registro/{registro_id}/audit")
def obtener_audit_trail(registro_id: str, x_api_key: str = Header(None)):
    """Obtiene el historial de cambios de un registro. Requiere API key."""
    verify_api_key(x_api_key)

    reg = get_registro_by_id(registro_id)
    if not reg:
        raise HTTPException(status_code=404, detail=f"Registro {registro_id} no encontrado")

    trail = get_audit_trail(registro_id)
    return {"registro_id": registro_id, "total": len(trail), "data": trail}


@app.delete("/api/registro/{registro_id}")
def eliminar_registro(registro_id: str, request: Request, x_api_key: str = Header(None)):
    """Elimina un registro. Guarda snapshot en audit_log para restauración. Requiere API key."""
    verify_api_key(x_api_key)

    reg = get_registro_by_id(registro_id)
    if not reg:
        raise HTTPException(status_code=404, detail=f"Registro {registro_id} no encontrado")

    ip = get_client_ip(request)
    success = delete_registro(registro_id, usuario="portal", ip=ip)
    if not success:
        raise HTTPException(status_code=500, detail="Error eliminando registro")

    return {"success": True, "registro_id": registro_id, "message": "Registro eliminado (snapshot guardado en auditoría)"}


# ─── Nuevo endpoint: Carga masiva ─────────────────────────

@app.post("/api/registros/upload")
async def upload_registros(request: Request, x_api_key: str = Header(None)):
    """Carga masiva de registros desde archivo Excel (.xlsx).
    Requiere API key. Enviar como multipart/form-data con campo 'file'.
    """
    verify_api_key(x_api_key)

    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(status_code=400, detail="No se proporcionó archivo. Use campo 'file'.")

    # Leer contenido
    contents = await file.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo muy grande ({len(contents) // 1024 // 1024}MB). Máximo: {MAX_UPLOAD_SIZE_MB}MB",
        )

    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(contents), read_only=True, data_only=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo archivo Excel: {e}")

    ws = wb.active
    if ws is None:
        raise HTTPException(status_code=400, detail="El archivo Excel no tiene hojas")

    # Leer headers de la primera fila
    header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
    if not header_row:
        raise HTTPException(status_code=400, detail="El archivo Excel no tiene encabezados")

    headers = [str(h or "").strip().lower().replace(" ", "_") for h in header_row]

    # Mapeo flexible: header Excel → columna DB
    # Acepta tanto nombres internos (afiliacion) como labels (Afiliación)
    HEADER_ALIASES = {
        "no._registro": "registro_id",
        "no_registro": "registro_id",
        "fecha/hora_envío": "timestamp_envio",
        "fecha_hora_envio": "timestamp_envio",
        "diagnóstico_registrado": "diagnostico_registrado",
        "código_cie-10": "codigo_cie10",
        "codigo_cie-10": "codigo_cie10",
        "código_cie10": "codigo_cie10",
        "fecha_notificación": "fecha_notificacion",
        "semana_epidemiológica": "semana_epidemiologica",
        "enviaron_ficha": "envio_ficha",
        "afiliación": "afiliacion",
        "número_de_afiliación": "afiliacion",
        "nombre_y_apellido": "nombre_apellido",
        "edad_(años)": "edad_anios",
        "edad_(meses)": "edad_meses",
        "departamento": "departamento_residencia",
        "municipio": "municipio_residencia",
        "dirección": "direccion_exacta",
        "embarazada": "esta_embarazada",
        "fiebre": "signo_fiebre",
        "exantema": "signo_exantema",
        "manchas_koplik": "signo_manchas_koplik",
        "tos": "signo_tos",
        "conjuntivitis": "signo_conjuntivitis",
        "artralgia": "signo_artralgia",
        "coriza": "signo_coriza",
        "adenopatías": "signo_adenopatias",
        "adenopatias": "signo_adenopatias",
        "dosis_spr/sr": "numero_dosis_spr",
        "dosis_spr_sr": "numero_dosis_spr",
        "fecha_última_dosis": "fecha_ultima_dosis",
        "condición_egreso": "condicion_egreso",
        "fecha_defunción": "fecha_defuncion",
        "igg_cualitativo": "resultado_igg_cualitativo",
        "igm_cualitativo": "resultado_igm_cualitativo",
        "rt-pcr_orina": "resultado_pcr_orina",
        "rt-pcr_hisopado": "resultado_pcr_hisopado",
        "clasificación": "clasificacion_caso",
        "clasificacion": "clasificacion_caso",
    }

    # Resolver mapeo de columnas
    col_map = {}  # index -> db_column
    for i, h in enumerate(headers):
        if h in COLUMNS:
            col_map[i] = h
        elif h in HEADER_ALIASES:
            col_map[i] = HEADER_ALIASES[h]

    if not col_map:
        raise HTTPException(
            status_code=400,
            detail=f"No se reconocieron columnas. Headers encontrados: {headers[:10]}",
        )

    # Leer filas de datos
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_data = {}
        for i, val in enumerate(row):
            if i in col_map:
                row_data[col_map[i]] = sanitize_value(val)
        # Skip filas completamente vacías
        if any(v for v in row_data.values()):
            # Generar registro_id si no viene
            if not row_data.get("registro_id"):
                from datetime import datetime as dt
                import random
                import string
                ts = int((dt.now() - dt(dt.now().year, 1, 1)).total_seconds())
                code = ''.join(random.choices(
                    [c for c in string.ascii_uppercase + string.digits if c not in 'IO01'], k=4
                ))
                row_data["registro_id"] = f"IGSS-SAR-{dt.now().year}-{ts:07d}-{code}"
            if not row_data.get("timestamp_envio"):
                row_data["timestamp_envio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows.append(row_data)

    wb.close()

    if not rows:
        raise HTTPException(status_code=400, detail="El archivo no contiene filas de datos")

    # Insertar
    ip = get_client_ip(request)
    result = bulk_insert_registros(rows, ip=ip)

    return {
        "success": True,
        "total_rows": len(rows),
        "inserted": result["inserted"],
        "duplicates": result["duplicates"],
        "errors": result["errors"][:50],
        "columns_mapped": {v: headers[k] for k, v in col_map.items()},
        "message": f"Carga completada: {result['inserted']} insertados, {result['duplicates']} duplicados",
    }


# ─── Endpoints existentes ─────────────────────────────────

@app.get("/api/registros")
def listar_registros(
    x_api_key: str = Header(None),
    limit: int = Query(100, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    clasificacion: str = Query(None),
    departamento: str = Query(None),
    semana: str = Query(None),
):
    """Lista registros con paginación y filtros. Requiere API key."""
    verify_api_key(x_api_key)

    filters = {}
    if clasificacion:
        filters["clasificacion_caso"] = clasificacion
    if departamento:
        filters["departamento_residencia"] = departamento
    if semana:
        filters["semana_epidemiologica"] = semana

    registros = get_registros(limit=limit, offset=offset, filters=filters)
    total = get_count(filters=filters)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": registros,
    }


@app.get("/api/registros/search")
def api_search_registros(
    q: str = Query("", description="Texto a buscar"),
    limit: int = Query(20, ge=1, le=100),
    x_api_key: str = Header(None),
):
    """Buscar registros por afiliación, nombre o ID."""
    verify_api_key(x_api_key)
    if not q or len(q) < 2:
        raise HTTPException(400, "La búsqueda debe tener al menos 2 caracteres")
    results = search_registros(q, limit)
    return {"data": results, "total": len(results), "query": q}


@app.get("/api/registros/count")
def contar_registros(
    x_api_key: str = Header(None),
    clasificacion: str = Query(None),
):
    """Cuenta total de registros. Requiere API key."""
    verify_api_key(x_api_key)

    filters = {}
    if clasificacion:
        filters["clasificacion_caso"] = clasificacion

    return {"total": get_count(filters=filters)}


@app.get("/api/export/excel")
def export_excel(x_api_key: str = Header(None)):
    """Exporta registros como Excel con formato IGSS oficial.
    3 hojas (SOSPECHOSOS, CONFIRMADOS, SUSPENDIDOS), 2 filas header (categorías + columnas).
    """
    verify_api_key(x_api_key)

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    registros = get_registros(limit=50000)

    # Separar por clasificación
    sheets_data = {"SOSPECHOSOS": [], "CONFIRMADOS": [], "SUSPENDIDOS": []}
    for r in registros:
        clasif = (r.get("clasificacion_caso") or "").upper()
        if clasif in ("CONFIRMADO",):
            sheets_data["CONFIRMADOS"].append(r)
        elif clasif in ("SUSPENDIDO",):
            sheets_data["SUSPENDIDOS"].append(r)
        else:
            sheets_data["SOSPECHOSOS"].append(r)

    # Columnas en orden del Excel — compatible MSPAS + IGSS
    EXPORT_COLS = [
        # Datos Generales (1-13)
        "diagnostico_registrado", "codigo_cie10", "unidad_medica", "unidad_medica_otra",
        "centro_externo",
        "fecha_registro_diagnostico", "fecha_notificacion", "semana_epidemiologica",
        "servicio_reporta", "nom_responsable", "cargo_responsable", "telefono_responsable",
        "envio_ficha",
        # Datos del Paciente (14-31)
        "afiliacion", "nombres", "apellidos", "sexo", "fecha_nacimiento",
        "edad_anios", "edad_meses", "edad_dias", "pueblo_etnia", "comunidad_linguistica",
        "ocupacion", "escolaridad",
        "departamento_residencia", "municipio_residencia", "poblado",
        "direccion_exacta", "nombre_encargado", "telefono_encargado",
        # Embarazo (32-37)
        "esta_embarazada", "lactando", "semanas_embarazo", "fecha_probable_parto",
        "vacuna_embarazada", "fecha_vacunacion_embarazada",
        # Información Clínica (38-65)
        "fecha_inicio_sintomas", "fecha_captacion", "fuente_notificacion",
        "fuente_notificacion_otra",
        "fecha_visita_domiciliaria", "fecha_inicio_investigacion", "busqueda_activa",
        "busqueda_activa_otra",
        "fecha_inicio_erupcion", "sitio_inicio_erupcion", "sitio_inicio_erupcion_otro",
        "fecha_inicio_fiebre", "temperatura_celsius",
        "signo_fiebre", "signo_exantema", "signo_manchas_koplik",
        "signo_tos", "signo_conjuntivitis", "signo_artralgia",
        "signo_coriza", "signo_adenopatias", "asintomatico",
        "vacunado", "fuente_info_vacuna", "tipo_vacuna", "numero_dosis_spr",
        "fecha_ultima_dosis", "observaciones_vacuna",
        # Hospitalización (66-77)
        "hospitalizado", "hosp_nombre", "hosp_fecha", "no_registro_medico",
        "complicaciones", "complicaciones_otra", "diagnostico_otro",
        "condicion_egreso", "fecha_egreso", "fecha_defuncion",
        "medico_certifica_defuncion", "motivo_consulta",
        # Factores de Riesgo (78-83)
        "contacto_sospechoso_7_23", "caso_sospechoso_comunidad_3m",
        "viajo_7_23_previo", "destino_viaje",
        "contacto_enfermo_catarro", "contacto_embarazada",
        # Laboratorio (84-105)
        "recolecto_muestra", "motivo_no_recoleccion", "muestra_suero", "muestra_suero_fecha",
        "muestra_hisopado", "muestra_hisopado_fecha",
        "muestra_orina", "muestra_orina_fecha",
        "muestra_otra", "muestra_otra_descripcion", "muestra_otra_fecha",
        "antigeno_prueba", "antigeno_otro", "resultado_prueba",
        "resultado_igg_cualitativo", "resultado_igm_cualitativo",
        "resultado_pcr_orina", "resultado_pcr_hisopado",
        "fecha_recepcion_laboratorio", "fecha_resultado_laboratorio",
        "resultado_igg_numerico", "resultado_igm_numerico",
        # Contactos y IGSS (106-113)
        "contactos_directos", "clasificacion_caso", "fecha_clasificacion_final",
        "responsable_clasificacion", "observaciones",
        "es_empleado_igss", "unidad_medica_trabaja", "puesto_desempena",
        "subgerencia_igss", "subgerencia_igss_otra",
        "direccion_igss", "direccion_igss_otra",
        "departamento_igss", "departamento_igss_otro",
        "seccion_igss", "seccion_igss_otra",
    ]

    COL_HEADERS = [
        # Datos Generales
        "Diagnóstico", "CIE-10", "Unidad Médica", "Unidad Médica Otra",
        "Centro Externo",
        "Fecha Registro", "Fecha Notificación", "Semana Epi.",
        "Servicio", "Responsable", "Cargo", "Teléfono Resp.",
        "Enviaron Ficha",
        # Datos del Paciente
        "Afiliación", "Nombres", "Apellidos", "Sexo", "Fecha Nac.",
        "Edad Años", "Edad Meses", "Edad Días", "Pueblo/Etnia", "Comunidad Ling.",
        "Ocupación", "Escolaridad",
        "Departamento", "Municipio", "Poblado",
        "Dirección", "Encargado", "Tel. Encargado",
        # Embarazo
        "Embarazada", "Lactando", "Sem. Embarazo", "Fecha Prob. Parto",
        "Vacuna Emb.", "Fecha Vac. Emb.",
        # Información Clínica
        "Fecha Inicio Síntomas", "Fecha Captación", "Fuente Notif.",
        "Fuente Notif. Otra",
        "Fecha Visita Dom.", "Fecha Inicio Invest.", "Búsq. Activa",
        "Búsq. Activa Otra",
        "Fecha Inicio Erupción", "Sitio Erupción", "Otro Sitio Erupción",
        "Fecha Inicio Fiebre", "Temp. °C",
        "Fiebre", "Exantema", "Koplik",
        "Tos", "Conjuntivitis", "Artralgia",
        "Coriza", "Adenopatías", "Asintomático",
        "Vacunado", "Fuente Info Vacuna", "Tipo Vacuna", "No. Dosis",
        "Fecha Últ. Dosis", "Obs. Vacunación",
        # Hospitalización
        "Hospitalizado", "Hospital", "Fecha Hosp.", "Reg. Médico",
        "Complicaciones", "Complicaciones (otra)", "Diagnóstico (otro)",
        "Condición Egreso", "Fecha Egreso", "Fecha Defunción",
        "Médico Defunción", "Motivo Consulta",
        # Factores de Riesgo
        "Contacto Sosp. 7-23d", "Caso Sosp. Comunidad 3m",
        "Viajó 7-23d", "Destino Viaje",
        "Contacto Enfermo", "Contacto Embarazada",
        # Laboratorio
        "Recolectó Muestra", "Motivo No Recolección", "Suero", "Fecha Suero",
        "Hisopado", "Fecha Hisopado",
        "Orina", "Fecha Orina",
        "Otra Muestra", "Desc. Otra Muestra", "Fecha Otra Muestra",
        "Antígeno", "Otro Antígeno", "Resultado Prueba",
        "IgG Cual.", "IgM Cual.",
        "PCR Orina", "PCR Hisopado",
        "Fecha Recep. Lab", "Fecha Result. Lab",
        "IgG Num.", "IgM Num.",
        # Contactos y IGSS
        "Contactos Directos", "Clasificación", "Fecha Clasif. Final",
        "Resp. Clasificación", "Observaciones",
        "Empleado IGSS", "Unidad Trabaja", "Puesto",
        "Subgerencia IGSS", "Subgerencia Otra",
        "Dirección IGSS", "Dirección Otra",
        "Depto. IGSS", "Depto. Otro",
        "Sección IGSS", "Sección Otra",
    ]

    # Category headers (row 1) — (start_col, end_col, label)  1-indexed within EXPORT_COLS
    CATEGORIES = [
        (1, 13, "DATOS GENERALES"),
        (14, 31, "DATOS DEL PACIENTE"),
        (32, 37, "EMBARAZO"),
        (38, 65, "INFORMACIÓN CLÍNICA"),
        (66, 77, "HOSPITALIZACIÓN"),
        (78, 83, "FACTORES DE RIESGO"),
        (84, 105, "LABORATORIO"),
        (106, 121, "CONTACTOS Y DATOS IGSS"),
    ]

    # Styles
    cat_fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
    cat_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    hdr_fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid")
    hdr_font = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
    border_thin = Border(
        bottom=Side(style="thin"), right=Side(style="thin", color="CCCCCC"),
    )
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    wb = openpyxl.Workbook()
    first = True

    for sheet_name, data in sheets_data.items():
        if first:
            ws = wb.active
            ws.title = sheet_name
            first = False
        else:
            ws = wb.create_sheet(sheet_name)

        # Add "No. caso" as first column
        total_cols = len(EXPORT_COLS) + 1  # +1 for No. caso

        # Row 1: Category headers (merged)
        ws.cell(row=1, column=1, value="No.").fill = cat_fill
        ws.cell(row=1, column=1).font = cat_font
        ws.cell(row=1, column=1).alignment = center_align

        for start, end, label in CATEGORIES:
            s = start + 1  # offset for No. caso column
            e = end + 1
            cell = ws.cell(row=1, column=s, value=label)
            cell.fill = cat_fill
            cell.font = cat_font
            cell.alignment = center_align
            if s != e:
                ws.merge_cells(start_row=1, start_column=s, end_row=1, end_column=e)

        # Row 2: Column headers
        ws.cell(row=2, column=1, value="No. caso").fill = hdr_fill
        ws.cell(row=2, column=1).font = hdr_font
        ws.cell(row=2, column=1).alignment = center_align
        ws.cell(row=2, column=1).border = border_thin

        for i, header in enumerate(COL_HEADERS):
            cell = ws.cell(row=2, column=i + 2, value=header)
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = center_align
            cell.border = border_thin

        # Data rows
        for row_idx, reg in enumerate(data, 3):
            ws.cell(row=row_idx, column=1, value=row_idx - 2)  # No. caso
            for col_idx, col_key in enumerate(EXPORT_COLS, 2):
                ws.cell(row=row_idx, column=col_idx, value=reg.get(col_key, ""))

        # Column widths
        ws.column_dimensions["A"].width = 6
        for i, col_key in enumerate(EXPORT_COLS, 2):
            letter = get_column_letter(i)
            ws.column_dimensions[letter].width = min(max(len(COL_HEADERS[i-2]), 10) + 2, 28)

        ws.freeze_panes = "A3"  # Freeze first 2 rows

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"BASE_DATOS_VIGILANCIA_SARAMPION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/api/export/csv")
def export_csv(x_api_key: str = Header(None)):
    """Exporta todos los registros como CSV. Requiere API key."""
    verify_api_key(x_api_key)

    registros = get_registros(limit=50000)
    export_cols = [c for c in COLUMNS if c not in ("ip_origen", "created_at")]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=export_cols, extrasaction="ignore")
    writer.writeheader()
    for reg in registros:
        writer.writerow({k: reg.get(k, "") for k in export_cols})

    output.seek(0)
    filename = f"vigilancia_sarampion_igss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ─── PDF Ficha Export ─────────────────────────────────────
@app.get("/api/export/ficha/{registro_id}")
def export_ficha_pdf(registro_id: str, x_api_key: str = Header(None)):
    """Genera PDF de ficha epidemiológica para un registro individual."""
    verify_api_key(x_api_key)
    reg = get_registro_by_id(registro_id)
    if not reg:
        raise HTTPException(status_code=404, detail=f"Registro {registro_id} no encontrado")

    from pdf_ficha import generar_ficha_pdf
    pdf_bytes = generar_ficha_pdf(reg)

    filename = f"ficha_{registro_id.replace('/', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/api/export/fichas")
async def export_fichas_bulk(request: Request, x_api_key: str = Header(None)):
    """Genera PDFs para múltiples registros.
    Body: {"ids": ["IGSS-SAR-...", ...], "format": "merged"|"zip"}
    """
    verify_api_key(x_api_key)
    data = await request.json()
    ids = data.get("ids", [])
    fmt = data.get("format", "merged")

    if not ids or len(ids) > 500:
        raise HTTPException(status_code=400, detail="Proporcione entre 1 y 500 IDs")

    records = []
    for rid in ids:
        reg = get_registro_by_id(rid)
        if reg:
            records.append(reg)

    if not records:
        raise HTTPException(status_code=404, detail="Ningún registro encontrado")

    from pdf_ficha import generar_fichas_bulk
    merge = (fmt == "merged")
    result_bytes = generar_fichas_bulk(records, merge=merge)

    if merge:
        filename = f"fichas_sarampion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    else:
        filename = f"fichas_sarampion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )


@app.get("/api/ficha-publica/{registro_id}")
def export_ficha_publica(registro_id: str):
    """Public endpoint for downloading ficha PDF (only for recent records, <30 min old)."""
    reg = get_registro_by_id(registro_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # Security: only allow download of records created in the last 30 minutes
    created = reg.get("created_at", "")
    if created:
        try:
            created_dt = datetime.fromisoformat(created)
            age_minutes = (datetime.now() - created_dt).total_seconds() / 60
            if age_minutes > 30:
                raise HTTPException(status_code=403, detail="El PDF solo está disponible dentro de los 30 minutos posteriores al envío")
        except (ValueError, TypeError):
            pass

    from pdf_ficha import generar_ficha_pdf
    pdf_bytes = generar_ficha_pdf(reg)

    filename = f"ficha_{registro_id.replace('/', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ─── MSPAS Queue Endpoints ─────────────────────────────────

@app.post("/api/mspas/config")
async def mspas_save_config(request: Request, x_api_key: str = Header(None)):
    """Save MSPAS EPIWEB credentials."""
    verify_api_key(x_api_key)
    data = await request.json()
    username = data.get("username", "")
    password = data.get("password", "")
    if not username or not password:
        raise HTTPException(400, "Username and password required")
    save_credentials(username, password)
    return {"status": "ok", "message": "Credentials saved"}


@app.get("/api/mspas/config")
def mspas_get_config(x_api_key: str = Header(None)):
    """Check if MSPAS credentials are configured."""
    verify_api_key(x_api_key)
    username, password = get_credentials()
    return {
        "configured": bool(username and password),
        "username": username[:3] + "***" if username else None,
    }


@app.post("/api/mspas/test")
def mspas_test_connection(x_api_key: str = Header(None)):
    """Test MSPAS login without submitting anything."""
    verify_api_key(x_api_key)
    username, password = get_credentials()
    if not username:
        raise HTTPException(400, "MSPAS credentials not configured")

    from mspas_bot import MSPASBot
    bot = MSPASBot(username, password)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            success = bot.login(page)
            return {"success": success, "message": "Login exitoso" if success else "Login fallido"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            browser.close()


@app.get("/api/mspas/queue")
def mspas_get_queue(
    estado: str = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    x_api_key: str = Header(None),
):
    """Get MSPAS submission queue."""
    verify_api_key(x_api_key)
    items = get_queue(estado=estado, limit=limit, offset=offset)
    counts = get_queue_counts()
    return {"data": items, "counts": counts, "total": sum(counts.values())}


@app.post("/api/mspas/queue/enqueue-all")
def mspas_enqueue_all(x_api_key: str = Header(None)):
    """Add all records not yet in queue."""
    verify_api_key(x_api_key)
    added = enqueue_all_pending()
    return {"added": added}


@app.post("/api/mspas/queue/approve")
async def mspas_approve(request: Request, x_api_key: str = Header(None)):
    """Approve records for MSPAS submission."""
    verify_api_key(x_api_key)
    data = await request.json()
    ids = data.get("ids", [])
    if not ids:
        raise HTTPException(400, "No IDs provided")
    approve_records(ids, aprobado_por="api")
    return {"approved": len(ids)}


@app.post("/api/mspas/submit/{registro_id}")
def mspas_submit_one(registro_id: str, x_api_key: str = Header(None)):
    """Submit a single record to MSPAS (or test-fill in non-production mode)."""
    verify_api_key(x_api_key)

    # Auto-recover any stuck submissions before processing
    recovered = recover_stuck_submissions(timeout_minutes=10)
    if recovered:
        logger.info(f"Auto-recovered {recovered} stuck MSPAS submissions before submit")

    username, password = get_credentials()
    if not username:
        raise HTTPException(400, "MSPAS credentials not configured")

    reg = get_registro_by_id(registro_id)
    if not reg:
        raise HTTPException(404, f"Registro {registro_id} not found")

    if not try_claim_for_submission(registro_id):
        raise HTTPException(409, "Record is already being processed or not in 'aprobado' state")

    from mspas_bot import MSPASBot
    bot = MSPASBot(username, password)
    result = bot.process_record(reg)

    if result.get("duplicate"):
        # Patient already exists in MSPAS — mark as duplicate (confirmed or possible)
        if result.get("duplicate_type") == "possible":
            mark_possible_duplicate(registro_id, result.get("details", ""))
        else:
            mark_duplicate(registro_id, mspas_ficha_id=result.get("mspas_ficha_id", ""))
    elif result.get("success"):
        if result.get("submitted"):
            mark_sent(registro_id, result.get("mspas_ficha_id", ""),
                     result.get("screenshots", [""])[-1] if result.get("screenshots") else "")
        else:
            update_estado(registro_id, 'aprobado')  # Back to approved (test mode)
    else:
        mark_error(registro_id, "; ".join(result.get("errors", ["Unknown error"])))

    return result


@app.post("/api/mspas/submit-batch")
def mspas_submit_batch(x_api_key: str = Header(None)):
    """Submit ALL approved records in batch (single browser session).

    Much faster than individual submissions: 1 login instead of N logins,
    saving ~15s per record. For 1000 records: ~14h instead of ~18h.
    """
    verify_api_key(x_api_key)

    # Recover any stuck submissions first
    recovered = recover_stuck_submissions(timeout_minutes=10)
    if recovered:
        logger.info(f"Auto-recovered {recovered} stuck MSPAS submissions before batch")

    username, password = get_credentials()
    if not username:
        raise HTTPException(400, "MSPAS credentials not configured")

    # Get all approved records
    approved_ids = get_approved_for_submission(limit=99999)
    if not approved_ids:
        return {"processed": 0, "success": 0, "errors": 0,
                "message": "No approved records pending submission"}

    # Claim all for submission (atomically mark as 'enviando')
    claimed = []
    for rid in approved_ids:
        if try_claim_for_submission(rid):
            claimed.append(rid)

    if not claimed:
        return {"processed": 0, "success": 0, "errors": 0,
                "message": "All approved records are already being processed"}

    # Fetch full record data for each claimed ID
    records = []
    for rid in claimed:
        reg = get_registro_by_id(rid)
        if reg:
            records.append(reg)
        else:
            mark_error(rid, "Registro no encontrado en la base de datos")

    if not records:
        return {"processed": 0, "success": 0, "errors": len(claimed),
                "message": "No valid records found for claimed IDs"}

    # Process entire batch with a single browser session.
    # State is updated PER RECORD via on_complete callback so that if the
    # process crashes at record N, records 1..N-1 already have their final
    # state persisted (not stuck in 'enviando').
    from mspas_bot import MSPASBot
    bot = MSPASBot(username, password)

    success_count = 0
    error_count = 0
    duplicate_count = 0

    def _on_record_done(rid, result):
        nonlocal success_count, error_count, duplicate_count
        try:
            if result.get('duplicate'):
                if result.get('duplicate_type') == 'possible':
                    mark_possible_duplicate(rid, result.get('details', ''))
                else:
                    mark_duplicate(rid, mspas_ficha_id=result.get('mspas_ficha_id', ''))
                duplicate_count += 1
            elif result.get('success'):
                if result.get('submitted'):
                    mark_sent(rid, result.get('mspas_ficha_id', ''),
                             result.get('screenshots', [''])[-1] if result.get('screenshots') else '')
                    success_count += 1
                else:
                    # Test mode: back to approved
                    update_estado(rid, 'aprobado')
                    success_count += 1
            else:
                mark_error(rid, '; '.join(result.get('errors', ['Unknown error'])))
                error_count += 1
        except Exception as e:
            logger.error("Failed to update state for record %s: %s", rid, e)
            error_count += 1

    results = bot.process_batch(records, on_complete=_on_record_done)

    return {
        "processed": len(results),
        "success": success_count,
        "errors": error_count,
        "duplicates": duplicate_count,
        "message": f"Batch complete: {success_count} ok, {error_count} errors, {duplicate_count} duplicates",
    }


@app.get("/api/mspas/status/{registro_id}")
def mspas_get_status(registro_id: str, x_api_key: str = Header(None)):
    """Get MSPAS submission status for a record."""
    verify_api_key(x_api_key)
    item = get_status_by_id(registro_id)
    if not item:
        raise HTTPException(404, "Record not in MSPAS queue")
    return item


@app.get("/api/mspas/screenshot/{filename}")
def mspas_get_screenshot(filename: str, x_api_key: str = Header(None)):
    """Serve a bot screenshot file (legacy flat path)."""
    verify_api_key(x_api_key)
    import os
    safe_filename = os.path.basename(filename)
    screenshot_dir = os.environ.get(
        "MSPAS_SCREENSHOT_DIR",
        "/opt/vigilancia-sarampion/data/mspas_screenshots"
    )
    path = os.path.join(screenshot_dir, safe_filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Screenshot not found")
    return FileResponse(path, media_type="image/png")


@app.get("/api/mspas/screenshot/{registro_id}/{filename}")
def mspas_get_screenshot_by_record(registro_id: str, filename: str,
                                    x_api_key: str = Header(None)):
    """Serve a bot screenshot file from a per-record subdirectory."""
    verify_api_key(x_api_key)
    import os
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', registro_id)
    safe_filename = os.path.basename(filename)
    screenshot_dir = os.environ.get(
        "MSPAS_SCREENSHOT_DIR",
        "/opt/vigilancia-sarampion/data/mspas_screenshots"
    )
    path = os.path.join(screenshot_dir, safe_id, safe_filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Screenshot not found")
    return FileResponse(path, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
