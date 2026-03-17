"""
Capa de base de datos SQLite para Vigilancia Sarampión.
Compatible con el patrón de Reportes-IGSS (SQLite WAL mode).
"""
import sqlite3
import os
from datetime import datetime
from config import DB_PATH

# Columnas del formulario en orden
COLUMNS = [
    "registro_id",
    "timestamp_envio",
    "diagnostico_registrado",
    "diagnostico_otro",
    "codigo_cie10",
    "unidad_medica",
    "unidad_medica_otra",
    "fecha_registro_diagnostico",
    "fecha_notificacion",
    "semana_epidemiologica",
    "servicio_reporta",
    "envio_ficha",
    "afiliacion",
    "nombre_apellido",
    "edad_anios",
    "edad_meses",
    "sexo",
    "departamento_residencia",
    "municipio_residencia",
    "direccion_exacta",
    "esta_embarazada",
    "semanas_embarazo",
    "fecha_probable_parto",
    "vacuna_embarazada",
    "fecha_vacunacion_embarazada",
    "motivo_consulta",
    "fecha_inicio_sintomas",
    "signo_fiebre",
    "signo_exantema",
    "signo_manchas_koplik",
    "signo_tos",
    "signo_conjuntivitis",
    "signo_artralgia",
    "signo_coriza",
    "signo_adenopatias",
    "numero_dosis_spr",
    "fecha_ultima_dosis",
    "hospitalizado",
    "complicaciones",
    "complicaciones_otra",
    "condicion_egreso",
    "fecha_defuncion",
    "fecha_laboratorios",
    "tipo_muestra",
    "resultado_igg_numerico",
    "resultado_igg_cualitativo",
    "resultado_igm_numerico",
    "resultado_igm_cualitativo",
    "resultado_pcr_orina",
    "resultado_pcr_hisopado",
    "contactos_directos",
    "clasificacion_caso",
    "observaciones",
    # Metadatos
    "ip_origen",
    "created_at",
]


def get_connection():
    """Obtiene conexión SQLite con WAL mode (compatible con Reportes-IGSS)."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA cache_size=-10000")  # 10MB cache
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la tabla si no existe."""
    conn = get_connection()
    cols = ", ".join(f'"{c}" TEXT' for c in COLUMNS)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {cols}
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_afiliacion
        ON registros(afiliacion)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_fecha_notificacion
        ON registros(fecha_notificacion)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_clasificacion
        ON registros(clasificacion_caso)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_registro_id
        ON registros(registro_id)
    """)
    conn.commit()
    conn.close()


def insert_registro(data: dict, ip: str = "") -> str:
    """Inserta un nuevo registro y retorna el registro_id."""
    conn = get_connection()
    try:
        data["ip_origen"] = ip
        data["created_at"] = datetime.now().isoformat()

        cols = []
        vals = []
        for c in COLUMNS:
            cols.append(f'"{c}"')
            vals.append(data.get(c, ""))

        placeholders = ", ".join(["?"] * len(cols))
        col_str = ", ".join(cols)

        conn.execute(
            f"INSERT INTO registros ({col_str}) VALUES ({placeholders})",
            vals,
        )
        conn.commit()
        return data.get("registro_id", "")
    finally:
        conn.close()


def get_registros(limit: int = 1000, offset: int = 0, filters: dict = None):
    """Obtiene registros con filtros opcionales."""
    conn = get_connection()
    try:
        query = "SELECT * FROM registros"
        params = []

        if filters:
            conditions = []
            for key, val in filters.items():
                if key in COLUMNS and val:
                    conditions.append(f'"{key}" = ?')
                    params.append(val)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_count(filters: dict = None) -> int:
    """Cuenta total de registros."""
    conn = get_connection()
    try:
        query = "SELECT COUNT(*) FROM registros"
        params = []

        if filters:
            conditions = []
            for key, val in filters.items():
                if key in COLUMNS and val:
                    conditions.append(f'"{key}" = ?')
                    params.append(val)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        return conn.execute(query, params).fetchone()[0]
    finally:
        conn.close()


def check_duplicate(afiliacion: str, fecha_notificacion: str) -> bool:
    """Verifica si ya existe un registro con misma afiliación y fecha."""
    if not afiliacion or not fecha_notificacion:
        return False
    conn = get_connection()
    try:
        row = conn.execute(
            'SELECT COUNT(*) FROM registros WHERE afiliacion = ? AND fecha_notificacion = ?',
            (afiliacion, fecha_notificacion),
        ).fetchone()
        return row[0] > 0
    finally:
        conn.close()
