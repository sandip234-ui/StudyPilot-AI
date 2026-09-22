"""
Application configuration.
All values are read from environment variables loaded from .env.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve the backend/ root regardless of where the process is launched from.
# This file lives at backend/app/core/config.py → go up three levels → backend/
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=_BACKEND_ROOT / ".env")


class Settings:
    # ── Ollama ────────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Must be set in .env before production use.
    # Leave empty for development without Ollama (mock mode via conftest).
    # Example: OLLAMA_MODEL=llama3.2:1b
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "")

    # HTTP timeout in seconds for the Ollama generate call.
    # 1B models on CPU can take 30–90 s; increase if generation is cut short.
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "60"))

    # ── Server ────────────────────────────────────────────────────────────────
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Explicit origins only — no wildcard.
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
