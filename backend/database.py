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
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_afiliacion_fecha
        ON registros(afiliacion, fecha_notificacion)
        WHERE afiliacion != '' AND fecha_notificacion != ''
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


# ─── Nuevas funciones para visor/edición ─────────────────

# Campos que NO se pueden editar desde la API
_READONLY_FIELDS = {"id", "ip_origen", "created_at", "registro_id"}

# Columnas editables
EDITABLE_COLUMNS = [c for c in COLUMNS if c not in _READONLY_FIELDS]


def get_registro_by_id(registro_id: str) -> dict | None:
    """Obtiene un registro por su registro_id."""
    conn = get_connection()
    try:
        row = conn.execute(
            'SELECT * FROM registros WHERE registro_id = ?',
            (registro_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_registro(registro_id: str, data: dict) -> bool:
    """Actualiza campos de un registro existente.
    Solo actualiza campos en EDITABLE_COLUMNS que estén presentes en data.
    Retorna True si se actualizó alguna fila.
    """
    # Filtrar solo columnas editables válidas
    updates = {k: v for k, v in data.items() if k in EDITABLE_COLUMNS}
    if not updates:
        return False

    conn = get_connection()
    try:
        set_clause = ", ".join(f'"{k}" = ?' for k in updates)
        values = list(updates.values()) + [registro_id]
        cursor = conn.execute(
            f'UPDATE registros SET {set_clause} WHERE registro_id = ?',
            values,
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def bulk_insert_registros(rows: list[dict], ip: str = "") -> dict:
    """Inserta múltiples registros en una transacción.
    Retorna {inserted, duplicates, errors: [{row, error}]}.
    """
    result = {"inserted": 0, "duplicates": 0, "errors": []}
    conn = get_connection()
    try:
        for i, row_data in enumerate(rows):
            try:
                afiliacion = row_data.get("afiliacion", "")
                fecha = row_data.get("fecha_notificacion", "")

                # Check duplicate
                if afiliacion and fecha:
                    dup = conn.execute(
                        'SELECT COUNT(*) FROM registros WHERE afiliacion = ? AND fecha_notificacion = ?',
                        (afiliacion, fecha),
                    ).fetchone()[0]
                    if dup > 0:
                        result["duplicates"] += 1
                        continue

                row_data["ip_origen"] = ip
                row_data["created_at"] = datetime.now().isoformat()

                cols = []
                vals = []
                for c in COLUMNS:
                    cols.append(f'"{c}"')
                    vals.append(row_data.get(c, ""))

                placeholders = ", ".join(["?"] * len(cols))
                col_str = ", ".join(cols)

                conn.execute(
                    f"INSERT INTO registros ({col_str}) VALUES ({placeholders})",
                    vals,
                )
                result["inserted"] += 1
            except sqlite3.IntegrityError:
                result["duplicates"] += 1
            except Exception as e:
                result["errors"].append({"row": i + 2, "error": str(e)})

        conn.commit()
    except Exception as e:
        conn.rollback()
        result["errors"].append({"row": 0, "error": f"Error general: {e}"})
    finally:
        conn.close()
    return result


# ─── Auditoría ────────────────────────────────────────────

def init_audit_table():
    """Crea la tabla de auditoría si no existe."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registro_id TEXT NOT NULL,
                campo TEXT NOT NULL,
                valor_anterior TEXT,
                valor_nuevo TEXT,
                usuario TEXT DEFAULT 'api',
                ip_origen TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_registro
            ON audit_log(registro_id)
        """)
        conn.commit()
    finally:
        conn.close()


def log_changes(registro_id: str, old: dict, new: dict, usuario: str = "api", ip: str = ""):
    """Registra cambios campo por campo en la tabla de auditoría."""
    changes = []
    for field, new_val in new.items():
        if field in _READONLY_FIELDS:
            continue
        old_val = str(old.get(field, "") or "")
        new_val_str = str(new_val or "")
        if old_val != new_val_str:
            changes.append((registro_id, field, old_val, new_val_str, usuario, ip))

    if not changes:
        return

    conn = get_connection()
    try:
        conn.executemany(
            'INSERT INTO audit_log (registro_id, campo, valor_anterior, valor_nuevo, usuario, ip_origen) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            changes,
        )
        conn.commit()
    finally:
        conn.close()


def get_audit_trail(registro_id: str) -> list[dict]:
    """Obtiene el historial de cambios de un registro."""
    conn = get_connection()
    try:
        rows = conn.execute(
            'SELECT campo, valor_anterior, valor_nuevo, usuario, ip_origen, timestamp '
            'FROM audit_log WHERE registro_id = ? ORDER BY id DESC LIMIT 200',
            (registro_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
