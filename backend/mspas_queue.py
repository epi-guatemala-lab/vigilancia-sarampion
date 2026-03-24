"""
MSPAS Submission Queue — Manages the pipeline of records to submit to EPIWEB.
States: pendiente -> revisado -> aprobado -> enviando -> enviado | error | duplicado
"""
import sqlite3
import os
import logging
from datetime import datetime
from cryptography.fernet import Fernet

from config import DB_PATH

logger = logging.getLogger(__name__)

# Encryption key for MSPAS credentials (from env var)
_FERNET_KEY = os.environ.get('MSPAS_ENCRYPT_KEY', '')


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_mspas_tables():
    """Create MSPAS queue and config tables if they don't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mspas_envios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_id TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            revisado_por TEXT,
            fecha_revision TEXT,
            aprobado_por TEXT,
            fecha_aprobacion TEXT,
            mspas_ficha_id TEXT,
            fecha_envio TEXT,
            intentos INTEGER DEFAULT 0,
            ultimo_error TEXT,
            screenshot_path TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_mspas_registro
        ON mspas_envios(registro_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_mspas_estado
        ON mspas_envios(estado)
    """)
    # Config table for encrypted credentials
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mspas_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


# --- Credential Management (encrypted) ---

def save_credentials(username: str, password: str):
    """Save MSPAS credentials encrypted."""
    if not _FERNET_KEY:
        # Fallback: store as-is (not recommended for production)
        _save_config('mspas_username', username)
        _save_config('mspas_password', password)
        return
    f = Fernet(_FERNET_KEY.encode())
    _save_config('mspas_username', f.encrypt(username.encode()).decode())
    _save_config('mspas_password', f.encrypt(password.encode()).decode())
    _save_config('mspas_encrypted', 'true')


def get_credentials() -> tuple:
    """Get MSPAS credentials (decrypted). Returns (username, password) or (None, None)."""
    username = _get_config('mspas_username')
    password = _get_config('mspas_password')
    if not username or not password:
        return (None, None)
    encrypted = _get_config('mspas_encrypted')
    if encrypted == 'true' and _FERNET_KEY:
        try:
            f = Fernet(_FERNET_KEY.encode())
            username = f.decrypt(username.encode()).decode()
            password = f.decrypt(password.encode()).decode()
        except Exception:
            return (None, None)
    return (username, password)


def _save_config(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO mspas_config (key, value, updated_at) VALUES (?, ?, ?)",
        (key, value, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def _get_config(key: str) -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM mspas_config WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else ''


# --- Queue Management ---

def enqueue_record(registro_id: str) -> bool:
    """Add a record to the submission queue. Returns True if added, False if already exists."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO mspas_envios (registro_id) VALUES (?)",
            (registro_id,)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Already in queue
    finally:
        conn.close()


def enqueue_all_pending():
    """Add all records NOT yet in the queue to the submission queue."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO mspas_envios (registro_id)
            SELECT registro_id FROM registros
            WHERE registro_id NOT IN (SELECT registro_id FROM mspas_envios)
            AND registro_id IS NOT NULL AND registro_id != ''
        """)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def get_queue(estado: str = None, limit: int = 100, offset: int = 0) -> list:
    """Get queue entries with optional state filter."""
    conn = get_connection()
    try:
        query = "SELECT * FROM mspas_envios"
        params = []
        if estado:
            query += " WHERE estado = ?"
            params.append(estado)
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_queue_counts() -> dict:
    """Get count of records per state."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT estado, COUNT(*) as total FROM mspas_envios GROUP BY estado"
        ).fetchall()
        return {r['estado']: r['total'] for r in rows}
    finally:
        conn.close()


def update_estado(registro_id: str, estado: str, **kwargs):
    """Update the state of a queue entry."""
    conn = get_connection()
    try:
        sets = ["estado = ?", "updated_at = ?"]
        params = [estado, datetime.now().isoformat()]
        for key, val in kwargs.items():
            sets.append(f"{key} = ?")
            params.append(val)
        params.append(registro_id)
        conn.execute(
            f"UPDATE mspas_envios SET {', '.join(sets)} WHERE registro_id = ?",
            params
        )
        conn.commit()
    finally:
        conn.close()


def approve_records(registro_ids: list, aprobado_por: str = 'api'):
    """Mark records as approved for submission."""
    conn = get_connection()
    try:
        now = datetime.now().isoformat()
        for rid in registro_ids:
            conn.execute(
                "UPDATE mspas_envios SET estado = 'aprobado', aprobado_por = ?, fecha_aprobacion = ?, updated_at = ? WHERE registro_id = ? AND estado IN ('pendiente', 'revisado', 'error')",
                (aprobado_por, now, now, rid)
            )
        conn.commit()
    finally:
        conn.close()


def mark_sent(registro_id: str, mspas_ficha_id: str, screenshot_path: str = ''):
    """Mark a record as successfully sent to MSPAS."""
    update_estado(registro_id, 'enviado',
        mspas_ficha_id=mspas_ficha_id,
        fecha_envio=datetime.now().isoformat(),
        screenshot_path=screenshot_path
    )


def mark_error(registro_id: str, error_msg: str):
    """Mark a record as failed."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE mspas_envios SET estado = 'error', ultimo_error = ?, intentos = intentos + 1, updated_at = ? WHERE registro_id = ?",
            (error_msg, datetime.now().isoformat(), registro_id)
        )
        conn.commit()
    finally:
        conn.close()


def try_claim_for_submission(registro_id: str) -> bool:
    """Atomically claim a record for submission. Returns True if claimed, False if already claimed."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE mspas_envios SET estado = 'enviando', updated_at = ? WHERE registro_id = ? AND estado = 'aprobado'",
            (datetime.now().isoformat(), registro_id)
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()


def recover_stuck_submissions(timeout_minutes: int = 10):
    """Reset records stuck in 'enviando' state for longer than timeout."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE mspas_envios SET estado = 'error', ultimo_error = 'Timeout: proceso interrumpido', updated_at = ? WHERE estado = 'enviando' AND updated_at < datetime('now', ?)",
            (datetime.now().isoformat(), f'-{timeout_minutes} minutes')
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def get_approved_for_submission(limit: int = 50) -> list:
    """Get records approved and ready to submit."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT registro_id FROM mspas_envios WHERE estado = 'aprobado' ORDER BY id ASC LIMIT ?",
            (limit,)
        ).fetchall()
        return [r['registro_id'] for r in rows]
    finally:
        conn.close()
