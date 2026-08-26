"""Overview API for the dashboard.

Current contract:
    GET /api/overview?domain=&year=&region=&indicator_key=

Response shape:
    {
        "kpis": [],
        "trend": [],
        "regional": [],
        "insights": [],
        "metadata": {},
        "filters": {}
    }

Analytical data is sourced from mart.*. Metadata is sourced from
warehouse.dim_indicator.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from app.db.database import engine

router = APIRouter(prefix="/api/overview", tags=["overview"])

REGION_NATIONAL = "national"

# External API contract -> database subject mapping.
# Keep this explicit so the frontend never depends on raw dim_indicator.subject_name values.
DOMAIN_SUBJECT_CANDIDATES = {
    "economic": [
        "economic",
        "ekonomi",
        "ekonomi makro",
    ],
    "poverty": [
        "kemiskinan dan ketimpangan",
        "kemiskinan",
    ],
}


def _run(query: str, params: dict[str, Any] | None = None):
    with engine.connect() as conn:
        return conn.execute(text(query), params or {}).mappings().all()


def _normalize_domain(domain: Optional[str]) -> Optional[str]:
    if domain is None:
        return None

    normalized = domain.strip().lower()
    if not normalized:
        return None

    return normalized


def _normalize_region(region: Optional[str]) -> str:
    if region is None:
        return REGION_NATIONAL

    normalized = region.strip().lower()
    if normalized in {"", "nasional", "national"}:
        return REGION_NATIONAL

    return normalized


def _serialize_optional_number(value: Any) -> Any:
    """Return JSON-safe numeric values while preserving NULL semantics."""
    return None if value is None else value


def _fetch_kpis(domain: Optional[str] = None, indicator_key: Optional[str] = None):
    query = """
        SELECT
            eo.indicator_key,
            eo.indicator_name,
            eo.unit,
            eo.frequency,
            MAX(eo.year) AS latest_year,
            COUNT(DISTINCT eo.year) AS years_available,
            MAX(eo.region_count) AS region_count
        FROM mart.economic_overview eo
        LEFT JOIN warehouse.dim_indicator di ON eo.indicator_key = di.indicator_key
        WHERE 1=1
    """
    params: dict[str, Any] = {}

    if domain:
        subject_candidates = DOMAIN_SUBJECT_CANDIDATES.get(domain)
        if not subject_candidates:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported domain '{domain}' for /api/overview",
            )

        query += """
            AND EXISTS (
                SELECT 1
                FROM unnest(:subject_candidates) AS subject_name
                WHERE LOWER(COALESCE(di.subject_name, '')) = subject_name
            )
        """
        params["subject_candidates"] = subject_candidates

    if indicator_key:
        query += " AND eo.indicator_key = :indicator_key"
        params["indicator_key"] = indicator_key

    query += """
        GROUP BY eo.indicator_key, eo.indicator_name, eo.unit, eo.frequency
        ORDER BY eo.indicator_name
    """

    rows = _run(query, params)
    kpis = []

    for row in rows:
        latest_row = _run(
            """
            SELECT national_value, national_growth_pct
            FROM mart.economic_overview
            WHERE indicator_key = :indicator_key AND year = :year
            LIMIT 1
            """,
            {
                "indicator_key": row["indicator_key"],
                "year": row["latest_year"],
            },
        )
        latest_metrics = latest_row[0] if latest_row else None
        current_value = (
            _serialize_optional_number(latest_metrics["national_value"])
            if latest_metrics
            else None
        )
        yoy_growth = (
            _serialize_optional_number(latest_metrics["national_growth_pct"])
            if latest_metrics
            else None
        )
        kpis.append(
            {
                **{
                    key: row[key]
                    for key in [
                        "indicator_key",
                        "indicator_name",
                        "unit",
                        "frequency",
                        "latest_year",
                        "years_available",
                        "region_count",
                    ]
                },
                "current_value": current_value,
                "yoy_growth": yoy_growth,
                "national_value_status": "unavailable" if current_value is None else "available",
            }
        )

    return kpis


def _fetch_trend(indicator_key: str):
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
        WHERE indicator_key = :indicator_key
        ORDER BY year
    """
    return [dict(row) for row in _run(query, {"indicator_key": indicator_key})]


def _fetch_regional(indicator_key: str, year: Optional[int] = None):
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
        WHERE indicator_key = :indicator_key
    """
    params: dict[str, Any] = {"indicator_key": indicator_key}

    if year is not None:
        query += " AND year = :year"
        params["year"] = year

    query += " ORDER BY year, regional_rank"
    return [dict(row) for row in _run(query, params)]


def _fetch_metadata(indicator_key: str):
    query = """
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
        WHERE indicator_key = :indicator_key
        LIMIT 1
    """
    rows = _run(query, {"indicator_key": indicator_key})
    return dict(rows[0]) if rows else None


def _list_available_domains():
    rows = _run(
        """
        SELECT DISTINCT LOWER(TRIM(subject_name)) AS subject_name
        FROM warehouse.dim_indicator
        WHERE subject_name IS NOT NULL AND TRIM(subject_name) <> ''
        ORDER BY 1
        """
    )
    available_subjects = [row["subject_name"] for row in rows]

    configured_domains = {
        domain: {
            "subject_candidates": candidates,
            "matched_subjects": [
                subject for subject in available_subjects if subject in candidates
            ],
        }
        for domain, candidates in DOMAIN_SUBJECT_CANDIDATES.items()
    }

    supported_domains = [
        {
            "key": domain,
            "subject_candidates": payload["subject_candidates"],
            "matched_subjects": payload["matched_subjects"],
            "available": len(payload["matched_subjects"]) > 0,
        }
        for domain, payload in configured_domains.items()
    ]

    return {
        "available_subjects": available_subjects,
        "configured_domains": configured_domains,
        "supported_domains": supported_domains,
    }


def _build_insights(kpis, trend, regional):
    insights = []
    if not kpis:
        return insights

    indicator = kpis[0]

    if trend:
        latest_trend = sorted(trend, key=lambda row: row["year"])[-1]
        growth = latest_trend.get("growth_pct")
        if growth is not None:
            insights.append(
                {
                    "id": "insight-trend",
                    "category": indicator.get("frequency") or "Indikator",
                    "title": f"{indicator['indicator_name']} — tren terakhir",
                    "description": (
                        f"Indikator mencatat pertumbuhan {growth:.2f}% pada periode terakhir ({latest_trend['year']}) dibandingkan periode sebelumnya."
                        if growth >= 0
                        else f"Indikator mencatat penurunan {growth:.2f}% pada periode terakhir ({latest_trend['year']}) dibandingkan periode sebelumnya."
                    ),
                    "direction": "up" if growth > 0 else ("down" if growth < 0 else "neutral"),
                    "value": f"{growth:+.2f}%",
                }
            )

    if regional:
        latest_year = max(row["year"] for row in regional)
        latest_rows = sorted(
            [row for row in regional if row["year"] == latest_year],
            key=lambda row: row["regional_rank"] or 0,
        )
        if latest_rows:
            top_region = latest_rows[0]
            insights.append(
                {
                    "id": "insight-region-top",
                    "category": "Regional",
                    "title": f"{top_region['region_name']} memimpin peringkat",
                    "description": f"Pada tahun {latest_year}, {top_region['region_name']} menempati peringkat teratas dengan nilai {top_region['value']}.",
                    "direction": "neutral",
                    "value": f"Rank #{top_region['regional_rank']}",
                }
            )

            fastest_region = sorted(
                latest_rows,
                key=lambda row: row.get("growth_pct") or 0,
                reverse=True,
            )[0]
            fastest_growth = fastest_region.get("growth_pct")
            if fastest_growth is not None:
                insights.append(
                    {
                        "id": "insight-region-growth",
                        "category": "Regional",
                        "title": f"{fastest_region['region_name']} tumbuh tercepat",
                        "description": f"Pertumbuhan {fastest_growth:+.2f}% menjadikannya wilayah dengan laju tercepat pada periode {latest_year}.",
                        "direction": "up" if fastest_growth > 0 else "down",
                        "value": f"{fastest_growth:+.2f}%",
                    }
                )

    return insights


@router.get("/domains")
def get_overview_domains():
    """Audit helper to verify API domain contract against dim_indicator.subject_name."""
    return _list_available_domains()


@router.get("")
def get_overview(
    domain: Optional[str] = Query(None, description="Dashboard domain filter"),
    year: Optional[int] = Query(None, description="Regional period; defaults to latest available year"),
    region: Optional[str] = Query(REGION_NATIONAL, description="Region scope; currently only 'national' is supported"),
    indicator_key: Optional[str] = Query(None, description="Specific indicator key"),
):
    """Return combined overview data for KPI, trend, regional, insights, and metadata panels."""
    normalized_domain = _normalize_domain(domain)
    normalized_region = _normalize_region(region)

    if normalized_region != REGION_NATIONAL:
        raise HTTPException(
            status_code=400,
            detail="Only region='national' is currently supported for /api/overview",
        )

    kpis = _fetch_kpis(domain=normalized_domain, indicator_key=indicator_key)
    if not kpis:
        raise HTTPException(status_code=404, detail="No economic data available")

    primary_key = indicator_key or kpis[0]["indicator_key"]
    resolved_year = year or kpis[0]["latest_year"]
    trend = _fetch_trend(primary_key)
    regional = _fetch_regional(primary_key, resolved_year)
    metadata = _fetch_metadata(primary_key)
    insights = _build_insights(kpis, trend, regional)

    return {
        "kpis": kpis,
        "trend": trend,
        "regional": regional,
        "insights": insights,
        "metadata": metadata,
        "filters": {
            "domain": normalized_domain,
            "year": resolved_year,
            "region": normalized_region,
            "indicator_key": primary_key,
        },
    }
