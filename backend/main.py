"""
API FastAPI para Vigilancia Epidemiológica — Brote Sarampión 2026
IGSS — Departamento de Medicina Preventiva — Sección de Epidemiología

Endpoints:
  POST /api/registro         → Guardar nuevo registro (público, desde formulario)
  GET  /api/registros        → Listar registros (requiere API key)
  GET  /api/registros/count  → Contar registros
  GET  /api/export/excel     → Descargar como Excel (requiere API key)
  GET  /api/export/csv       → Descargar como CSV (requiere API key)
  GET  /api/health           → Health check
"""
import io
import csv
import time
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, Request, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from config import ALLOWED_ORIGINS, API_SECRET_KEY, PORT, RATE_LIMIT_SECONDS
from database import init_db, insert_registro, get_registros, get_count, check_duplicate, COLUMNS

# ─── App ──────────────────────────────────────────────────
app = FastAPI(
    title="Vigilancia Sarampión - IGSS API",
    description="API de registro de casos sospechosos de sarampión",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting por IP (en memoria)
_rate_limiter: dict[str, float] = defaultdict(float)

# ─── Init DB ──────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print(f"Vigilancia Sarampión API iniciada en puerto {PORT}")


# ─── Helpers ──────────────────────────────────────────────
def verify_api_key(x_api_key: str = Header(None)):
    """Verifica la API key para endpoints protegidos."""
    if not x_api_key or x_api_key != API_SECRET_KEY:
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
        "timestamp": datetime.now().isoformat(),
        "total_registros": get_count(),
    }


@app.post("/api/registro")
async def crear_registro(request: Request):
    """
    Recibe datos del formulario y los guarda en la DB.
    Rate limited: máximo 1 envío cada 30 segundos por IP.
    """
    ip = get_client_ip(request)

    # Rate limiting
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

    if not data.get("registro_id"):
        raise HTTPException(status_code=400, detail="registro_id es requerido")

    # Verificar duplicado
    afiliacion = data.get("afiliacion", "")
    fecha = data.get("fecha_notificacion", "")
    if check_duplicate(afiliacion, fecha):
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un registro para afiliación {afiliacion} con fecha {fecha}",
        )

    # Sanitizar: solo aceptar campos conocidos
    clean = {}
    for col in COLUMNS:
        val = data.get(col, "")
        if isinstance(val, str):
            # Sanitizar caracteres peligrosos
            val = val.replace("\x00", "").strip()
        clean[col] = str(val) if val is not None else ""

    registro_id = insert_registro(clean, ip=ip)
    _rate_limiter[ip] = now

    return {
        "success": True,
        "registro_id": registro_id,
        "message": "Registro guardado correctamente",
    }


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

    # Headers con estilo IGSS
    header_fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
    header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
    header_border = Border(
        bottom=Side(style="thin", color="000000"),
        right=Side(style="thin", color="E0E0E0"),
    )

    # Nombres legibles para headers
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

    # Columnas a exportar (excluir metadatos internos)
    export_cols = [c for c in COLUMNS if c not in ("ip_origen", "created_at", "diagnostico_otro", "unidad_medica_otra", "complicaciones_otra", "semanas_embarazo", "fecha_probable_parto", "vacuna_embarazada", "fecha_vacunacion_embarazada", "resultado_igg_numerico", "resultado_igm_numerico")]

    for col_idx, col in enumerate(export_cols, 1):
        cell = ws.cell(row=1, column=col_idx, value=header_labels.get(col, col))
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = header_border

    # Datos
    for row_idx, reg in enumerate(registros, 2):
        for col_idx, col in enumerate(export_cols, 1):
            ws.cell(row=row_idx, column=col_idx, value=reg.get(col, ""))

    # Auto-width
    for col_idx, col in enumerate(export_cols, 1):
        max_len = max(len(str(header_labels.get(col, col))), 12)
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = min(max_len + 2, 30)

    # Freeze header
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


# ─── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
