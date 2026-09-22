"""
StudyPilot — FastAPI application entry point.

Registers:
  - CORS middleware (explicit origins only, no wildcard)
  - All API routes under /api prefix
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="StudyPilot API",
    description="AI-Powered Personalised Learning Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Only the Vite dev server origins are allowed — no wildcard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,   # ["http://localhost:5173", "http://127.0.0.1:5173"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
# All endpoints live under /api:
#   GET  /api/health
#   POST /api/learn
app.include_router(router, prefix="/api")
