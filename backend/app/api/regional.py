"""Regional analysis API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from backend.app.db.database import engine

router = APIRouter(prefix="/api/regional", tags=["regional"])


@router.get("/ranking")
def get_regional_ranking(
    indicator_key: Optional[str] = Query(None, description="Filter by indicator key"),
    year: Optional[int] = Query(None, description="Filter by year"),
    limit: int = Query(20, ge=1, le=100, description="Max rows to return"),
):
    """Return regional ranking from mart.regional_performance."""
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
            growth_pct,
            CASE
                WHEN growth_pct > 0 THEN 'Positive'
                WHEN growth_pct < 0 THEN 'Negative'
                ELSE 'Stable'
            END AS growth_status
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
    query += " ORDER BY year DESC, regional_rank LIMIT :limit"
    params["limit"] = limit

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No regional ranking data available")

    return {"data": [dict(row) for row in rows]}


@router.get("/{region_key}")
def get_region_detail(region_key: str):
    """Return detailed regional performance for a specific region."""
    query = text("""
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
        WHERE region_key = :rk
        ORDER BY indicator_name, year
    """)

    with engine.connect() as conn:
        rows = conn.execute(query, {"rk": region_key}).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail=f"Region {region_key} not found")

    return {"data": [dict(row) for row in rows]}