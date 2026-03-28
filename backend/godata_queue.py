"""
Cola de sincronización GoData.
Maneja el pipeline: registro → pendiente → aprobado → sincronizado/error.

Similar a mspas_queue.py pero para el destino GoData.
"""
import sqlite3
import logging
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# TABLA Y MIGRACIÓN
# ═══════════════════════════════════════════════════════════

def init_godata_tables():
    """Crea tablas de GoData si no existen."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS godata_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registro_id TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                godata_case_id TEXT,
                godata_visual_id TEXT,
                intentos INTEGER DEFAULT 0,
                ultimo_error TEXT,
                aprobado_por TEXT,
                fecha_aprobacion TEXT,
                fecha_sync TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_godata_queue_registro
            ON godata_queue(registro_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_godata_queue_estado
            ON godata_queue(estado)
        """)
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_godata_queue_registro_unique
            ON godata_queue(registro_id)
        """)

        # Migration: add godata_visual_id column if missing
        try:
            conn.execute("SELECT godata_visual_id FROM godata_queue LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE godata_queue ADD COLUMN godata_visual_id TEXT")
            logger.info("GoData: added godata_visual_id column to godata_queue")

        # Tabla de configuración GoData
        conn.execute("""
            CREATE TABLE IF NOT EXISTS godata_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                godata_url TEXT,
                username TEXT,
                password_encrypted TEXT,
                outbreak_id TEXT,
                outbreak_name TEXT,
                production_mode INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════

def save_godata_config(godata_url: str, username: str, password: str,
                        outbreak_id: str, outbreak_name: str = "") -> dict:
    """Guarda configuración GoData (password encriptado con Fernet)."""
    from mspas_queue import _get_fernet
    f = _get_fernet()
    password_enc = f.encrypt(password.encode()).decode() if f and password else ""

    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            INSERT OR REPLACE INTO godata_config
            (id, godata_url, username, password_encrypted, outbreak_id, outbreak_name, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, datetime('now'))
        """, (godata_url, username, password_enc, outbreak_id, outbreak_name))
        conn.commit()
        return {"status": "ok"}
    finally:
        conn.close()


def get_godata_config() -> dict:
    """Obtiene configuración GoData (sin password)."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM godata_config WHERE id = 1").fetchone()
        if not row:
            return {"configured": False}
        return {
            "configured": True,
            "godata_url": row["godata_url"],
            "username": row["username"],
            "has_password": bool(row["password_encrypted"]),
            "outbreak_id": row["outbreak_id"],
            "outbreak_name": row["outbreak_name"],
            "production_mode": bool(row["production_mode"]),
        }
    finally:
        conn.close()


def get_godata_credentials() -> tuple:
    """Obtiene credenciales GoData (incluyendo password desencriptado). Uso interno."""
    from mspas_queue import _get_fernet
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM godata_config WHERE id = 1").fetchone()
        if not row:
            return ("", "", "", "")
        password = ""
        if row["password_encrypted"]:
            f = _get_fernet()
            if f:
                try:
                    password = f.decrypt(row["password_encrypted"].encode()).decode()
                except Exception:
                    logger.warning("No se pudo desencriptar password GoData")
        return (row["godata_url"], row["username"], password, row["outbreak_id"])
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════
# COLA DE SINCRONIZACIÓN
# ═══════════════════════════════════════════════════════════

# Estados válidos
ESTADOS = ("pendiente", "aprobado", "subido_fase1", "completo",
           "error_fase1", "error_fase2", "sincronizando", "sincronizado",
           "error", "duplicado")

_ALLOWED_UPDATE_COLS = {
    "estado", "godata_case_id", "godata_visual_id", "intentos", "ultimo_error",
    "aprobado_por", "fecha_aprobacion", "fecha_sync", "updated_at"
}


def get_next_visual_id() -> str:
    """Generate next sequential visualId for GoData (SR-NNNN format).

    GoData's SR-9999 mask doesn't auto-generate via API, so we track
    the next available number ourselves.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        # Check existing max from our synced records
        row = conn.execute("""
            SELECT MAX(CAST(SUBSTR(godata_visual_id, 4) AS INTEGER))
            FROM godata_queue
            WHERE godata_visual_id IS NOT NULL AND godata_visual_id LIKE 'SR-%'
        """).fetchone()
        max_num = row[0] if row and row[0] else 0

        # Start from a safe offset to avoid conflicting with manual entries
        next_num = max(max_num + 1, 100)
        return f"SR-{next_num:04d}"
    finally:
        conn.close()


def save_visual_id(registro_id: str, visual_id: str):
    """Save the generated visualId for a registro."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET godata_visual_id = ?,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (visual_id, registro_id))
        conn.commit()
    finally:
        conn.close()


def enqueue_pending_records() -> dict:
    """Encola todos los registros que no están en la cola GoData."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        cursor = conn.execute("""
            INSERT INTO godata_queue (registro_id, estado)
            SELECT r.registro_id, 'pendiente'
            FROM registros r
            WHERE r.registro_id != ''
              AND r.registro_id NOT IN (SELECT registro_id FROM godata_queue)
        """)
        count = cursor.rowcount
        conn.commit()
        return {"enqueued": count}
    finally:
        conn.close()


def get_queue(estado: str = None, limit: int = 100) -> dict:
    """Obtiene la cola de sincronización GoData."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        # Conteos por estado
        counts = {}
        for e in ESTADOS:
            row = conn.execute(
                "SELECT COUNT(*) FROM godata_queue WHERE estado = ?", (e,)
            ).fetchone()
            counts[e] = row[0]

        # Registros filtrados
        query = """
            SELECT q.*, r.nombres, r.apellidos, r.afiliacion, r.fecha_notificacion,
                   r.clasificacion_caso, r.departamento_residencia
            FROM godata_queue q
            LEFT JOIN registros r ON q.registro_id = r.registro_id
        """
        params = []
        if estado:
            query += " WHERE q.estado = ?"
            params.append(estado)
        query += " ORDER BY q.id DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        data = [dict(r) for r in rows]
        return {"data": data, "counts": counts}
    finally:
        conn.close()


def approve_records(ids: list, usuario: str = "api") -> dict:
    """Aprueba registros para sincronización con GoData."""
    if not ids:
        return {"approved": 0}
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        approved = 0
        for registro_id in ids:
            cursor = conn.execute("""
                UPDATE godata_queue
                SET estado = 'aprobado',
                    aprobado_por = ?,
                    fecha_aprobacion = datetime('now'),
                    updated_at = datetime('now')
                WHERE registro_id = ?
                  AND estado IN ('pendiente', 'error', 'error_fase1')
            """, (usuario, registro_id))
            approved += cursor.rowcount
        conn.commit()
        return {"approved": approved}
    finally:
        conn.close()


def try_claim_for_sync(registro_id: str) -> bool:
    """Atómica: marca registro como 'sincronizando' si está 'aprobado'."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        cursor = conn.execute("""
            UPDATE godata_queue
            SET estado = 'sincronizando',
                intentos = intentos + 1,
                updated_at = datetime('now')
            WHERE registro_id = ?
              AND estado = 'aprobado'
        """, (registro_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def mark_synced(registro_id: str, godata_case_id: str):
    """Marca registro como sincronizado exitosamente."""
    # Get outbreak_id from config to fill godata_outbreak_id in registros
    outbreak_id = ""
    try:
        config = get_godata_config()
        outbreak_id = config.get("outbreak_id", "")
    except Exception:
        pass

    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'sincronizado',
                godata_case_id = ?,
                fecha_sync = datetime('now'),
                ultimo_error = NULL,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (godata_case_id, registro_id))
        # También actualizar el registro principal (including outbreak_id)
        conn.execute("""
            UPDATE registros
            SET godata_case_id = ?,
                godata_sync_status = 'SYNCED',
                godata_last_sync = datetime('now'),
                godata_outbreak_id = ?
            WHERE registro_id = ?
        """, (godata_case_id, outbreak_id, registro_id))
        conn.commit()
    finally:
        conn.close()


def mark_error(registro_id: str, error: str):
    """Marca registro con error de sincronización."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'error',
                ultimo_error = ?,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (error[:500], registro_id))
        conn.execute("""
            UPDATE registros
            SET godata_sync_status = 'ERROR'
            WHERE registro_id = ?
        """, (registro_id,))
        conn.commit()
    finally:
        conn.close()


def mark_duplicate(registro_id: str, godata_case_id: str = ""):
    """Marca registro como duplicado en GoData."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'duplicado',
                godata_case_id = ?,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (godata_case_id, registro_id))
        conn.execute("""
            UPDATE registros
            SET godata_sync_status = 'DUPLICATE',
                godata_case_id = ?
            WHERE registro_id = ?
        """, (godata_case_id, registro_id))
        conn.commit()
    finally:
        conn.close()


def get_approved_for_sync(limit: int = 50) -> list:
    """Obtiene registros aprobados listos para sincronizar."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT q.registro_id
            FROM godata_queue q
            WHERE q.estado = 'aprobado' AND q.intentos < 5
            ORDER BY q.id ASC
            LIMIT ?
        """, (limit,)).fetchall()
        return [row["registro_id"] for row in rows]
    finally:
        conn.close()


def recover_stuck_syncs(max_age_minutes: int = 60):
    """Recupera registros stuck en 'sincronizando' por más de max_age_minutes."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        cursor = conn.execute("""
            UPDATE godata_queue
            SET estado = 'aprobado',
                updated_at = datetime('now')
            WHERE estado = 'sincronizando'
              AND updated_at < datetime('now', ? || ' minutes')
        """, (f"-{max_age_minutes}",))
        recovered = cursor.rowcount
        if recovered:
            conn.commit()
            logger.info("GoData: recuperados %d registros stuck", recovered)
        return recovered
    finally:
        conn.close()


def get_sync_status(registro_id: str) -> dict:
    """Obtiene estado de sincronización de un registro."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM godata_queue WHERE registro_id = ?",
            (registro_id,)
        ).fetchone()
        return dict(row) if row else {"estado": "no_enqueued"}
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════
# 2-PHASE SYNC FUNCTIONS
# ═══════════════════════════════════════════════════════════

def mark_fase1_sent(registro_id: str, godata_case_id: str):
    """Mark record as Phase 1 sent (case created in GoData).

    Case exists in GoData with basic data. Ready for Phase 2 (lab + classification).
    """
    outbreak_id = ""
    try:
        config = get_godata_config()
        outbreak_id = config.get("outbreak_id", "")
    except Exception:
        pass

    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'subido_fase1',
                godata_case_id = ?,
                ultimo_error = NULL,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (godata_case_id, registro_id))
        # Also update the main registros table
        conn.execute("""
            UPDATE registros
            SET godata_case_id = ?,
                godata_sync_status = 'FASE1',
                godata_last_sync = datetime('now'),
                godata_outbreak_id = ?
            WHERE registro_id = ?
        """, (godata_case_id, outbreak_id, registro_id))
        conn.commit()
    finally:
        conn.close()


def mark_complete(registro_id: str):
    """Mark record as complete (Phase 2 successful — fully synced)."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'completo',
                fecha_sync = datetime('now'),
                ultimo_error = NULL,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (registro_id,))
        conn.execute("""
            UPDATE registros
            SET godata_sync_status = 'SYNCED',
                godata_last_sync = datetime('now')
            WHERE registro_id = ?
        """, (registro_id,))
        conn.commit()
    finally:
        conn.close()


def mark_error_fase1(registro_id: str, error: str):
    """Phase 1 error — case was NOT created in GoData."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'error_fase1',
                ultimo_error = ?,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (error[:500], registro_id))
        conn.execute("""
            UPDATE registros
            SET godata_sync_status = 'ERROR_F1'
            WHERE registro_id = ?
        """, (registro_id,))
        conn.commit()
    finally:
        conn.close()


def mark_error_fase2(registro_id: str, error: str):
    """Phase 2 error — case exists in GoData but update failed."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        conn.execute("""
            UPDATE godata_queue
            SET estado = 'error_fase2',
                ultimo_error = ?,
                updated_at = datetime('now')
            WHERE registro_id = ?
        """, (error[:500], registro_id))
        conn.execute("""
            UPDATE registros
            SET godata_sync_status = 'ERROR_F2'
            WHERE registro_id = ?
        """, (registro_id,))
        conn.commit()
    finally:
        conn.close()


def get_fase1_pending(limit: int = 50) -> list:
    """Get records in subido_fase1 state ready for Phase 2."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT q.registro_id, q.godata_case_id
            FROM godata_queue q
            WHERE q.estado = 'subido_fase1' AND q.intentos < 5
            ORDER BY q.id ASC
            LIMIT ?
        """, (limit,)).fetchall()
        return [{"registro_id": row["registro_id"], "godata_case_id": row["godata_case_id"]}
                for row in rows]
    finally:
        conn.close()


def requeue_for_update(registro_id: str) -> bool:
    """Move a 'completo' record back to 'subido_fase1' for re-update via Fase 2."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        cursor = conn.execute("""
            UPDATE godata_queue
            SET estado = 'subido_fase1',
                updated_at = datetime('now')
            WHERE registro_id = ?
              AND estado = 'completo'
        """, (registro_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def unapprove_records(ids: list) -> dict:
    """Move records from 'aprobado' back to 'pendiente'."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        count = 0
        for rid in ids:
            cursor = conn.execute("""
                UPDATE godata_queue
                SET estado = 'pendiente',
                    aprobado_por = NULL,
                    fecha_aprobacion = NULL,
                    updated_at = datetime('now')
                WHERE registro_id = ?
                  AND estado = 'aprobado'
            """, (rid,))
            count += cursor.rowcount
        conn.commit()
        return {"unapproved": count}
    finally:
        conn.close()


def try_claim_for_fase2(registro_id: str) -> bool:
    """Atomic: claim record for Phase 2 update. Only works on subido_fase1 or error_fase2."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        cursor = conn.execute("""
            UPDATE godata_queue
            SET estado = 'sincronizando',
                intentos = intentos + 1,
                updated_at = datetime('now')
            WHERE registro_id = ?
              AND estado IN ('subido_fase1', 'error_fase2')
        """, (registro_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
