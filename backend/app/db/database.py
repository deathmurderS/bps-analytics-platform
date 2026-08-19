"""Database connection management for the BPS dashboard backend."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from backend.app.config import settings


def create_db_engine() -> Engine:
    """Create a SQLAlchemy engine for the Neon PostgreSQL database."""
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


engine = create_db_engine()