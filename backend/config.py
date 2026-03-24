"""
Configuración central del backend de Vigilancia Sarampión.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Base de datos
DB_PATH = os.getenv("DB_PATH", "./data/sarampion_master.db")

# Seguridad
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "")
if not API_SECRET_KEY:
    import warnings
    warnings.warn("API_SECRET_KEY not set! Using insecure default. Set API_SECRET_KEY env var in production.")
    API_SECRET_KEY = "dev-key-change-in-production"  # Only for dev

# CORS
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "https://epi-guatemala-lab.github.io,http://localhost:5173,http://localhost:5174"
    ).split(",")
]

# Server
PORT = int(os.getenv("PORT", "8502"))

# Rate limiting (configurable via env para permitir carga masiva)
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "1"))

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
