"""BPS Dashboard Backend API."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.api import economic, metadata, overview, regional, trade
from app.config import settings
from app.db.database import engine

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


@app.exception_handler(OperationalError)
async def db_connection_error_handler(request: Request, exc: OperationalError):
    """Return 503 when the database is unreachable instead of a raw 500."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Database service unavailable. Please try again later."},
    )


@app.exception_handler(ProgrammingError)
async def db_programming_error_handler(request: Request, exc: ProgrammingError):
    """Return 404 for schema-level errors (e.g., table not found)."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Requested data is not available."},
    )


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