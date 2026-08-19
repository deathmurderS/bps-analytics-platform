"""Economic analysis API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from backend.app.db.database import engine

router = APIRouter(prefix="/api/economic", tags=["economic"])


@router.get("/trend")
def get_economic_trend(
    indicator_key: Optional[str] = Query(None, description="Filter by indicator key"),
):
    """Return indicator trend from mart.indicator_trend."""
    query = """
        SELECT
            year,
            indicator_key,
            indicator_name,
            unit,
            national_value,
            previous_value,
            growth_pct
        FROM mart.indicator_trend
    """
    params = {}
    if indicator_key:
        query += " WHERE indicator_key = :ik"
        params["ik"] = indicator_key
    query += " ORDER BY indicator_name, year"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No trend data available")

    return {"data": [dict(row) for row in rows]}


@router.get("/regional")
def get_economic_regional(
    indicator_key: Optional[str] = Query(None, description="Filter by indicator key"),
    year: Optional[int] = Query(None, description="Filter by year"),
):
    """Return regional performance from mart.regional_performance."""
    query = """
        SELECT
            year,
            region_key,
            region_name,
            indicator_key,
            indicator_name,
            value,
            regional_rank,
            previous_value,
            growth_pct
        FROM mart.regional_performance
    """
    params = {}
    conditions = []
    if indicator_key:
        conditions.append("indicator_key = :ik")
        params["ik"] = indicator_key
    if year:
        conditions.append("year = :yr")
        params["yr"] = year
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY year, regional_rank"

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No regional data available")

    return {"data": [dict(row) for row in rows]}


@router.get("/indicators")
def list_indicators():
    """List all available economic indicators."""
    query = text("""
        SELECT DISTINCT
            indicator_key,
            indicator_name,
            unit,
            frequency
        FROM mart.economic_overview
        ORDER BY indicator_name
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    return {"indicators": [dict(row) for row in rows]}