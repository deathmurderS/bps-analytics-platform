"""Trade analysis API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from backend.app.db.database import engine

router = APIRouter(prefix="/api/trade", tags=["trade"])


def _handle_db_error(exc: Exception) -> None:
    """Convert database errors to 404 if table doesn't exist."""
    if isinstance(exc, ProgrammingError) and "does not exist" in str(exc):
        raise HTTPException(status_code=404, detail="Trade data not available yet")
    raise exc


@router.get("/trend")
def get_trade_trend(
    year: Optional[int] = Query(None, description="Filter by year"),
):
    """Return export/import trend from mart.trade_trend."""
    query = """
        SELECT
            year,
            trade_flow,
            total_value_usd,
            total_weight_kg,
            transaction_count
        FROM mart.trade_trend
    """
    params = {}
    if year:
        query += " WHERE year = :yr"
        params["yr"] = year
    query += " ORDER BY year, trade_flow"

    try:
        with engine.connect() as conn:
            rows = conn.execute(text(query), params).mappings().all()
    except ProgrammingError as exc:
        _handle_db_error(exc)

    if not rows:
        raise HTTPException(status_code=404, detail="No trade trend data available")

    return {"data": [dict(row) for row in rows]}


@router.get("/commodities")
def get_trade_commodities(
    year: Optional[int] = Query(None, description="Filter by year"),
    trade_flow: Optional[str] = Query(None, description="Filter by trade flow (Ekspor/Impor)"),
    limit: int = Query(20, ge=1, le=100),
):
    """Return commodity ranking from mart.trade_commodity."""
    query = """
        SELECT
            year,
            trade_flow,
            product_code,
            product_name,
            total_value_usd,
            total_weight_kg,
            commodity_rank
        FROM mart.trade_commodity
    """
    params = {}
    conditions = []
    if year:
        conditions.append("year = :yr")
        params["yr"] = year
    if trade_flow:
        conditions.append("trade_flow = :tf")
        params["tf"] = trade_flow
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY year DESC, commodity_rank LIMIT :limit"
    params["limit"] = limit

    try:
        with engine.connect() as conn:
            rows = conn.execute(text(query), params).mappings().all()
    except ProgrammingError as exc:
        _handle_db_error(exc)

    if not rows:
        raise HTTPException(status_code=404, detail="No commodity data available")

    return {"data": [dict(row) for row in rows]}


@router.get("/partners")
def get_trade_partners(
    year: Optional[int] = Query(None, description="Filter by year"),
    trade_flow: Optional[str] = Query(None, description="Filter by trade flow (Ekspor/Impor)"),
    limit: int = Query(20, ge=1, le=100),
):
    """Return trading partner ranking from mart.trade_partner."""
    query = """
        SELECT
            year,
            trade_flow,
            country_code,
            country_name,
            total_value_usd,
            partner_rank
        FROM mart.trade_partner
    """
    params = {}
    conditions = []
    if year:
        conditions.append("year = :yr")
        params["yr"] = year
    if trade_flow:
        conditions.append("trade_flow = :tf")
        params["tf"] = trade_flow
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY year DESC, partner_rank LIMIT :limit"
    params["limit"] = limit

    try:
        with engine.connect() as conn:
            rows = conn.execute(text(query), params).mappings().all()
    except ProgrammingError as exc:
        _handle_db_error(exc)

    if not rows:
        raise HTTPException(status_code=404, detail="No partner data available")

    return {"data": [dict(row) for row in rows]}


@router.get("/balance")
def get_trade_balance():
    """Return economic vs trade bridge data."""
    query = text("""
        SELECT
            year,
            national_value,
            national_growth_pct,
            export_total_usd,
            import_total_usd,
            trade_balance_usd
        FROM mart.economic_trade_bridge
        ORDER BY year
    """)

    try:
        with engine.connect() as conn:
            rows = conn.execute(query).mappings().all()
    except ProgrammingError as exc:
        _handle_db_error(exc)

    if not rows:
        raise HTTPException(status_code=404, detail="No trade balance data available")

    return {"data": [dict(row) for row in rows]}