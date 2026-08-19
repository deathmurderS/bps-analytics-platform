"""Overview API endpoints."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from backend.app.db.database import engine

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("")
def get_overview():
    """Return overview KPIs from the economic overview mart."""
    query = text("""
        SELECT
            indicator_key,
            indicator_name,
            unit,
            frequency,
            MAX(year) AS latest_year,
            COUNT(DISTINCT year) AS years_available,
            MAX(region_count) AS region_count
        FROM mart.economic_overview
        GROUP BY indicator_key, indicator_name, unit, frequency
        ORDER BY indicator_name
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No economic data available")

    # Get latest year values for each indicator
    result = []
    for row in rows:
        latest = text("""
            SELECT national_value, national_growth_pct
            FROM mart.economic_overview
            WHERE indicator_key = :ik AND year = :yr
            LIMIT 1
        """)
        with engine.connect() as conn:
            latest_row = conn.execute(
                latest, {"ik": row["indicator_key"], "yr": row["latest_year"]}
            ).mappings().first()

        result.append({
            "indicator_key": row["indicator_key"],
            "indicator_name": row["indicator_name"],
            "unit": row["unit"],
            "frequency": row["frequency"],
            "latest_year": row["latest_year"],
            "years_available": row["years_available"],
            "region_count": row["region_count"],
            "current_value": latest_row["national_value"] if latest_row else None,
            "yoy_growth": latest_row["national_growth_pct"] if latest_row else None,
        })

    return {"indicators": result}