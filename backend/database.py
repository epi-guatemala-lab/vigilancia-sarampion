"""
Capa de base de datos SQLite para Vigilancia Sarampión.
Compatible con el patrón de Reportes-IGSS (SQLite WAL mode).
"""
import sqlite3
import os
from datetime import datetime
from config import DB_PATH

# Columnas del formulario en orden
# Incluye campos MSPAS EPIWEB (Tabs 1-5) + campos IGSS + campos formato 2026 GoData
COLUMNS = [
    "registro_id",
    "timestamp_envio",
    # Tab 1: Datos Generales
    "diagnostico_registrado",
    "diagnostico_otro",
    "codigo_cie10",
    "unidad_medica",
    "unidad_medica_otra",
    "centro_externo",
    "fecha_registro_diagnostico",
    "fecha_notificacion",
    "semana_epidemiologica",
    "servicio_reporta",
    "nom_responsable",
    "cargo_responsable",
    "telefono_responsable",
    "envio_ficha",
    # Tab 2: Datos del Paciente
    "afiliacion",
    "nombres",
    "apellidos",
    "nombre_apellido",  # Backward-compat: computed from nombres + apellidos
    "sexo",
    "fecha_nacimiento",
    "edad_anios",
    "edad_meses",
    "edad_dias",
    "pueblo_etnia",
    "comunidad_linguistica",
    "ocupacion",
    "escolaridad",
    "departamento_residencia",
    "municipio_residencia",
    "poblado",
    "direccion_exacta",
    "nombre_encargado",
    "telefono_encargado",
    # Tab 3: Embarazo
    "esta_embarazada",
    "lactando",
    "semanas_embarazo",
    "fecha_probable_parto",
    "vacuna_embarazada",
    "fecha_vacunacion_embarazada",
    # Tab 4: Información Clínica
    "fecha_inicio_sintomas",
    "fecha_captacion",
    "fuente_notificacion",
    "fuente_notificacion_otra",
    "fecha_visita_domiciliaria",
    "fecha_inicio_investigacion",
    "busqueda_activa",
    "busqueda_activa_otra",
    "fecha_inicio_erupcion",
    "sitio_inicio_erupcion",
    "sitio_inicio_erupcion_otro",
    "fecha_inicio_fiebre",
    "temperatura_celsius",
    "signo_fiebre",
    "signo_exantema",
    "signo_manchas_koplik",
    "signo_tos",
    "signo_conjuntivitis",
    "signo_artralgia",
    "asintomatico",
    "signo_coriza",
    "signo_adenopatias",
    "vacunado",
    "fuente_info_vacuna",
    "tipo_vacuna",
    "numero_dosis_spr",
    "fecha_ultima_dosis",
    "observaciones_vacuna",
    "hospitalizado",
    "hosp_nombre",
    "hosp_fecha",
    "no_registro_medico",
    "complicaciones",
    "complicaciones_otra",
    "condicion_egreso",
    "fecha_egreso",
    "fecha_defuncion",
    "medico_certifica_defuncion",
    "motivo_consulta",
    # Tab 5: Factores de Riesgo
    "contacto_sospechoso_7_23",
    "caso_sospechoso_comunidad_3m",
    "viajo_7_23_previo",
    "destino_viaje",
    "contacto_enfermo_catarro",
    "contacto_embarazada",
    # Tab 6: Laboratorio
    "recolecto_muestra",
    "motivo_no_recoleccion",
    "motivo_no_recoleccion_otro",
    "muestra_suero",
    "muestra_suero_fecha",
    "muestra_hisopado",
    "muestra_hisopado_fecha",
    "muestra_orina",
    "muestra_orina_fecha",
    "muestra_otra",
    "muestra_otra_descripcion",
    "muestra_otra_fecha",
    "antigeno_prueba",
    "antigeno_otro",
    "resultado_prueba",
    "fecha_recepcion_laboratorio",
    "fecha_resultado_laboratorio",
    "fecha_laboratorios",  # Backward-compat
    "tipo_muestra",  # Backward-compat
    "resultado_igg_numerico",
    "resultado_igg_cualitativo",
    "resultado_igm_numerico",
    "resultado_igm_cualitativo",
    "resultado_pcr_orina",
    "resultado_pcr_hisopado",
    # Tab 7: Contactos y Datos IGSS
    "contactos_directos",
    "clasificacion_caso",
    "fecha_clasificacion_final",
    "responsable_clasificacion",
    "observaciones",
    "es_empleado_igss",
    "unidad_medica_trabaja",
    "puesto_desempena",
    "subgerencia_igss",
    "subgerencia_igss_otra",
    "direccion_igss",
    "direccion_igss_otra",
    "departamento_igss",
    "departamento_igss_otro",
    "seccion_igss",
    "seccion_igss_otra",
    # ═══ FORMATO 2026 (GoData + MSPAS nuevo) ═══
    # Sección 0: Header — Diagnóstico de Sospecha
    "diagnostico_sospecha",
    "diagnostico_sospecha_otro",
    # Sección 1: Unidad Notificadora (nuevos)
    "area_salud_mspas",
    "distrito_salud_mspas",
    "servicio_salud_mspas",
    "correo_responsable",
    "es_seguro_social",
    "establecimiento_privado",
    "establecimiento_privado_nombre",
    # Sección 2: Paciente (nuevos)
    "tipo_identificacion",
    "numero_identificacion",
    "parentesco_tutor",
    "tipo_id_tutor",
    "numero_id_tutor",
    "es_migrante",
    "trimestre_embarazo",
    "telefono_paciente",
    "pais_residencia",
    # Sección 3: Antecedentes Médicos y Vacunación (nuevos)
    "tiene_antecedentes_medicos",
    "antecedentes_medicos_detalle",
    "antecedente_desnutricion",
    "antecedente_inmunocompromiso",
    "antecedente_enfermedad_cronica",
    "dosis_spr",
    "fecha_ultima_spr",
    "dosis_sr",
    "fecha_ultima_sr",
    "dosis_sprv",
    "fecha_ultima_sprv",
    "sector_vacunacion",
    # Sección 4: Clínicos (nuevos)
    "tiene_complicaciones",
    "comp_neumonia",
    "comp_encefalitis",
    "comp_diarrea",
    "comp_trombocitopenia",
    "comp_otitis",
    "comp_ceguera",
    "comp_otra_texto",
    "aislamiento_respiratorio",
    "fecha_aislamiento",
    # Sección 5: Factores de Riesgo (nuevos)
    "viaje_pais",
    "viaje_pais_otro",
    "viaje_departamento",
    "viaje_municipio",
    "viaje_ciudad_destino",
    "viaje_fecha_salida",
    "viaje_fecha_entrada",
    "familiar_viajo_exterior",
    "familiar_fecha_retorno",
    "fuente_posible_contagio",
    "fuente_contagio_otro",
    # Sección 6: Acciones de Respuesta (completamente nueva)
    "bai_realizada",
    "bai_casos_sospechosos",
    "bac_realizada",
    "bac_casos_sospechosos",
    "vacunacion_bloqueo",
    "monitoreo_rapido_vacunacion",
    "vacunacion_barrido",
    "vitamina_a_administrada",
    "vitamina_a_dosis",
    # Sección 7: Laboratorio (nuevos — detallado formato 2026)
    "lab_muestras_json",
    "motivo_no_3_muestras",
    "motivo_no_3_muestras_otro",
    "secuenciacion_resultado",
    "secuenciacion_fecha",
    # Muestras Rechazadas (Boleta de Rechazo - LNS)
    "muestra_rechazada",
    "muestra_rechazada_codigo",
    "muestra_rechazada_fecha",
    "muestra_rechazada_criterio",
    "muestra_rechazada_criterio_otro",
    "muestra_rechazada_tipo",
    "muestra_rechazada_observaciones",
    # Sección 8: Clasificación (nuevos)
    "criterio_confirmacion",
    "nexo_numero_ficha",
    "nexo_nombre_caso_confirmatorio",
    "contacto_otro_caso",
    "contacto_otro_caso_detalle",
    "criterio_descarte",
    "fuente_infeccion",
    "pais_importacion",
    "caso_analizado_por",
    "caso_analizado_por_otro",
    "condicion_final_paciente",
    "causa_muerte_certificado",
    # GoData tracking
    "godata_case_id",
    "godata_sync_status",
    "godata_last_sync",
    "godata_outbreak_id",
    "form_version",
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


def _migrate_columns(conn):
    """Add any missing columns to existing table (non-destructive migration)."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(registros)").fetchall()}
    added = 0
    for col in COLUMNS:
        if col not in existing:
            conn.execute(f'ALTER TABLE registros ADD COLUMN "{col}" TEXT')
            added += 1
    if added > 0:
        conn.commit()
        import logging
        logging.getLogger(__name__).info(f"Migrated {added} new columns to registros table")


def init_db():
    """Crea la tabla si no existe y migra columnas faltantes."""
    conn = get_connection()
    cols = ", ".join(f'"{c}" TEXT' for c in COLUMNS)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {cols}
        )
    """)
    # Migrate any new columns added since last deploy
    _migrate_columns(conn)
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

        # Backward-compat: compute nombre_apellido from nombres + apellidos
        if data.get("nombres") or data.get("apellidos"):
            parts = [data.get("nombres", ""), data.get("apellidos", "")]
            data["nombre_apellido"] = " ".join(p for p in parts if p).strip()
        elif data.get("nombre_apellido") and not data.get("nombres"):
            # Old-style submission with combined name
            pass

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


def find_duplicate_21_dias(
    numero_afiliado: str,
    fecha_inicio_sintomas: str = "",
    fecha_notificacion: str = "",
    exclude_registro_id: str = "",
) -> dict | None:
    """
    Período sarampión: retorna el registro activo más reciente del mismo afiliado
    cuya fecha_inicio_sintomas (o fecha_notificacion si la primera no existe)
    esté dentro de ±21 días de la fecha entregada. None si no hay duplicado.

    exclude_registro_id permite excluir el registro actual en edición (PUT).
    """
    if not numero_afiliado:
        return None
    # Escoger fecha pivote: preferir síntomas, fallback a notificación
    pivote = (fecha_inicio_sintomas or fecha_notificacion or "").strip()
    if not pivote:
        return None
    try:
        from datetime import datetime, timedelta
        d0 = datetime.strptime(pivote[:10], "%Y-%m-%d")
    except Exception:
        return None
    min_d = (d0 - timedelta(days=21)).strftime("%Y-%m-%d")
    max_d = (d0 + timedelta(days=21)).strftime("%Y-%m-%d")

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        # Detectar si la columna _soft_deleted existe para incluir el filtro
        has_soft = False
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(registros)").fetchall()}
            has_soft = "_soft_deleted" in cols
        except Exception:
            has_soft = False
        soft_clause = "COALESCE(_soft_deleted,0)=0 AND " if has_soft else ""

        sql = (
            f"SELECT registro_id, fecha_inicio_sintomas, fecha_notificacion, nombres, apellidos "
            f"FROM registros "
            f"WHERE {soft_clause}"
            f"  afiliacion = ? "
            f"  AND ( "
            f"    (COALESCE(fecha_inicio_sintomas,'') != '' AND substr(fecha_inicio_sintomas,1,10) BETWEEN ? AND ?) "
            f"    OR (COALESCE(fecha_inicio_sintomas,'') = '' AND substr(fecha_notificacion,1,10) BETWEEN ? AND ?) "
            f"  ) "
            f"  AND (? = '' OR registro_id != ?) "
            f"ORDER BY substr(COALESCE(fecha_inicio_sintomas, fecha_notificacion),1,10) DESC "
            f"LIMIT 1"
        )
        row = conn.execute(
            sql,
            (
                numero_afiliado,
                min_d, max_d,
                min_d, max_d,
                exclude_registro_id or "", exclude_registro_id or "",
            ),
        ).fetchone()
        return dict(row) if row else None
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


def delete_registro(registro_id: str, usuario: str = "api", ip: str = "") -> bool:
    """Elimina un registro por su registro_id.
    Guarda snapshot completo en audit_log antes de borrar para posible restauración.
    """
    conn = get_connection()
    try:
        # Leer registro completo antes de borrar
        row = conn.execute(
            'SELECT * FROM registros WHERE registro_id = ?', (registro_id,),
        ).fetchone()
        if not row:
            return False

        reg = dict(row)

        # Guardar snapshot completo en audit_log (campo = _DELETED, valor_anterior = JSON)
        import json
        snapshot = json.dumps({k: v for k, v in reg.items() if k != "id"}, ensure_ascii=False)
        conn.execute(
            'INSERT INTO audit_log (registro_id, campo, valor_anterior, valor_nuevo, usuario, ip_origen) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (registro_id, "_DELETED", snapshot, "", usuario, ip),
        )

        # Borrar
        cursor = conn.execute(
            'DELETE FROM registros WHERE registro_id = ?', (registro_id,),
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


def search_registros(query: str, limit: int = 20) -> list:
    """Search records by afiliacion, nombre, apellido, or registro_id."""
    conn = get_connection()
    try:
        q = f"%{query}%"
        rows = conn.execute("""
            SELECT * FROM registros
            WHERE registro_id LIKE ?
               OR afiliacion LIKE ?
               OR nombre_apellido LIKE ?
               OR nombres LIKE ?
               OR apellidos LIKE ?
            ORDER BY id DESC LIMIT ?
        """, (q, q, q, q, q, limit)).fetchall()
        return [dict(r) for r in rows]
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
