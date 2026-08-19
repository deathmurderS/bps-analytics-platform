"""Metadata explorer API endpoints."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from backend.app.db.database import engine

router = APIRouter(prefix="/api/metadata", tags=["metadata"])


@router.get("/indicator/{indicator_key}")
def get_indicator_metadata(indicator_key: str):
    """Return metadata for a specific indicator from dim_indicator."""
    query = text("""
        SELECT
            indicator_key,
            indicator_code,
            indicator_name,
            subject_name,
            category_name,
            unit,
            frequency,
            concept,
            definition,
            classification,
            measure,
            data_source,
            aggregation_method
        FROM warehouse.dim_indicator
        WHERE indicator_key = :ik
        LIMIT 1
    """)

    with engine.connect() as conn:
        row = conn.execute(query, {"ik": indicator_key}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail=f"Indicator {indicator_key} not found")

    return dict(row)


@router.get("/indicators")
def list_indicator_metadata():
    """List all indicators with their metadata."""
    query = text("""
        SELECT
            indicator_key,
            indicator_code,
            indicator_name,
            subject_name,
            category_name,
            unit,
            frequency,
            data_source
        FROM warehouse.dim_indicator
        ORDER BY indicator_name
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    return {"indicators": [dict(row) for row in rows]}


@router.get("/glossary")
def get_glossary():
    """Return glossary entries from dim_glossary."""
    query = text("""
        SELECT
            glossary_key,
            glossary_id,
            indicator_name,
            concept,
            definition,
            classification,
            measure,
            unit,
            data_source
        FROM warehouse.dim_glossary
        ORDER BY indicator_name
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    return {"data": [dict(row) for row in rows]}