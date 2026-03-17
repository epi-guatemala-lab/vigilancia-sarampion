"""
Configuración central del backend de Vigilancia Sarampión.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Base de datos
DB_PATH = os.getenv("DB_PATH", "./data/sarampion_master.db")

# Seguridad
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "dev-key-change-in-production")

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

# Rate limiting
RATE_LIMIT_SECONDS = 5  # Mínimo entre envíos por IP (5 segundos)
