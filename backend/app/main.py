"""BPS Dashboard Backend API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.api import economic, metadata, overview, regional, trade
from backend.app.config import settings
from backend.app.db.database import engine

app = FastAPI(
    title="BPS Analytics Platform API",
    description="REST API for the BPS Data Warehouse dashboard.",
    version="1.0.0",
)

# CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(overview.router)
app.include_router(economic.router)
app.include_router(regional.router)
app.include_router(trade.router)
app.include_router(metadata.router)


@app.get("/api/health")
def health_check():
    """Return API and database health status."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {"status": "ok", "database": db_status, "version": "1.0.0"}