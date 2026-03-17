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
from fastapi.responses import StreamingResponse, JSONResponse

from config import ALLOWED_ORIGINS, API_SECRET_KEY, PORT, RATE_LIMIT_SECONDS, MAX_UPLOAD_SIZE_MB
from database import (
    init_db, insert_registro, get_registros, get_count, check_duplicate,
    get_registro_by_id, update_registro, delete_registro, bulk_insert_registros,
    init_audit_table, log_changes, get_audit_trail,
    COLUMNS, EDITABLE_COLUMNS,
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
VALID_CLASIFICACIONES = {"SOSPECHOSO", "CONFIRMADO", "DESCARTADO", "CLÍNICO", "FALSO", "ERROR DIAGNÓSTICO"}
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
    """Exporta todos los registros como archivo Excel. Requiere API key."""
    verify_api_key(x_api_key)

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    registros = get_registros(limit=50000)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SOSPECHOSOS"

    header_fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
    header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
    header_border = Border(
        bottom=Side(style="thin", color="000000"),
        right=Side(style="thin", color="E0E0E0"),
    )

    header_labels = {
        "registro_id": "No. Registro",
        "timestamp_envio": "Fecha/Hora Envío",
        "diagnostico_registrado": "Diagnóstico Registrado",
        "codigo_cie10": "Código CIE-10",
        "unidad_medica": "Unidad Médica",
        "fecha_registro_diagnostico": "Fecha Registro Diagnóstico",
        "fecha_notificacion": "Fecha Notificación",
        "semana_epidemiologica": "Semana Epidemiológica",
        "servicio_reporta": "Servicio que Reporta",
        "envio_ficha": "Enviaron Ficha",
        "afiliacion": "Afiliación",
        "nombre_apellido": "Nombre y Apellido",
        "edad_anios": "Edad (años)",
        "edad_meses": "Edad (meses)",
        "sexo": "Sexo",
        "departamento_residencia": "Departamento",
        "municipio_residencia": "Municipio",
        "direccion_exacta": "Dirección",
        "esta_embarazada": "Embarazada",
        "motivo_consulta": "Motivo de Consulta",
        "fecha_inicio_sintomas": "Fecha Inicio Síntomas",
        "signo_fiebre": "Fiebre",
        "signo_exantema": "Exantema",
        "signo_manchas_koplik": "Manchas Koplik",
        "signo_tos": "Tos",
        "signo_conjuntivitis": "Conjuntivitis",
        "signo_artralgia": "Artralgia",
        "signo_coriza": "Coriza",
        "signo_adenopatias": "Adenopatías",
        "numero_dosis_spr": "Dosis SPR/SR",
        "fecha_ultima_dosis": "Fecha Última Dosis",
        "hospitalizado": "Hospitalizado",
        "complicaciones": "Complicaciones",
        "condicion_egreso": "Condición Egreso",
        "fecha_defuncion": "Fecha Defunción",
        "fecha_laboratorios": "Fecha Laboratorios",
        "tipo_muestra": "Tipo Muestra",
        "resultado_igg_cualitativo": "IgG Cualitativo",
        "resultado_igm_cualitativo": "IgM Cualitativo",
        "resultado_pcr_orina": "RT-PCR Orina",
        "resultado_pcr_hisopado": "RT-PCR Hisopado",
        "contactos_directos": "Contactos Directos",
        "clasificacion_caso": "Clasificación",
        "observaciones": "Observaciones",
    }

    export_cols = [c for c in COLUMNS if c not in (
        "ip_origen", "created_at", "diagnostico_otro", "unidad_medica_otra",
        "complicaciones_otra", "semanas_embarazo", "fecha_probable_parto",
        "vacuna_embarazada", "fecha_vacunacion_embarazada",
        "resultado_igg_numerico", "resultado_igm_numerico",
    )]

    for col_idx, col in enumerate(export_cols, 1):
        cell = ws.cell(row=1, column=col_idx, value=header_labels.get(col, col))
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = header_border

    for row_idx, reg in enumerate(registros, 2):
        for col_idx, col in enumerate(export_cols, 1):
            ws.cell(row=row_idx, column=col_idx, value=reg.get(col, ""))

    for col_idx, col in enumerate(export_cols, 1):
        max_len = max(len(str(header_labels.get(col, col))), 12)
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = min(max_len + 2, 30)

    ws.freeze_panes = "A2"

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"vigilancia_sarampion_igss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
