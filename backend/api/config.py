"""Central configuration. Everything comes from environment variables (.env)."""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "backend" / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
# Model names change over time - override in .env if Google retires one.
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_hex(32)  # set it, or tokens reset on restart
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", 12 * 3600))
DB_PATH = Path(os.getenv("DB_PATH", ROOT / "backend" / "database" / "elite.db"))

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,https://eliterecosys-37ajmiti7-sjri2.vercel.app"
    ).split(",")
    if o.strip()
]

DEMO_CSV = ROOT / "backend" / "ad_analysis_results.csv"
GEMINI_FALLBACK_MODELS = [m.strip() for m in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-2.5-flash-lite").split(",") if m.strip()]
