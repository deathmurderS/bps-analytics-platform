"""Backend API tests."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add backend root to path so app package can be imported from `backend/`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.api import overview

client = TestClient(app)

# Skip database-integration tests when DATABASE_URL is not available
# (e.g., pull requests from forks where GitHub secrets are not exposed)
requires_db = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL environment variable is not set",
)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


@requires_db
def test_overview_endpoint():
    """Test the overview endpoint returns a response."""
    response = client.get("/api/overview")
    # Should return either data or 404 if no data
    assert response.status_code in (200, 404)


@requires_db
def test_economic_trend_endpoint():
    """Test the economic trend endpoint."""
    response = client.get("/api/economic/trend")
    assert response.status_code in (200, 404)


@requires_db
def test_economic_regional_endpoint():
    """Test the economic regional endpoint."""
    response = client.get("/api/economic/regional")
    assert response.status_code in (200, 404)


@requires_db
def test_regional_ranking_endpoint():
    """Test the regional ranking endpoint."""
    response = client.get("/api/regional/ranking")
    assert response.status_code in (200, 404)


@requires_db
def test_trade_trend_endpoint():
    """Test the trade trend endpoint."""
    response = client.get("/api/trade/trend")
    assert response.status_code in (200, 404)


@requires_db
def test_trade_commodities_endpoint():
    """Test the trade commodities endpoint."""
    response = client.get("/api/trade/commodities")
    assert response.status_code in (200, 404)


@requires_db
def test_trade_partners_endpoint():
    """Test the trade partners endpoint."""
    response = client.get("/api/trade/partners")
    assert response.status_code in (200, 404)


@requires_db
def test_metadata_indicators_endpoint():
    """Test the metadata indicators endpoint."""
    response = client.get("/api/metadata/indicators")
    assert response.status_code in (200, 404)


def test_parameter_validation():
    """Test that invalid parameters are rejected."""
    response = client.get("/api/regional/ranking?limit=0")
    assert response.status_code == 422  # Validation error

    response = client.get("/api/regional/ranking?limit=1000")
    assert response.status_code == 422  # Validation error


def test_overview_rejects_unsupported_region():
    """Overview currently supports national scope only."""
    response = client.get("/api/overview?region=jakarta")
    assert response.status_code == 400
    assert response.json()["detail"] == "Only region='national' is currently supported for /api/overview"


def test_overview_rejects_unsupported_domain():
    """Overview should reject domain values that are not explicitly mapped."""
    response = client.get("/api/overview?domain=unknown&region=national")
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported domain 'unknown' for /api/overview"


@pytest.fixture
def overview_null_national_monkeypatch(monkeypatch):
    def fake_fetch_kpis(domain=None, indicator_key=None):
        return [
            {
                "indicator_key": indicator_key or "192",
                "indicator_name": "Persentase Penduduk Miskin (P0)",
                "unit": "Persen",
                "frequency": None,
                "latest_year": 2023,
                "years_available": 4,
                "region_count": 34,
                "current_value": None,
                "yoy_growth": None,
                "national_value_status": "unavailable",
            }
        ]

    monkeypatch.setattr(overview, "_fetch_kpis", fake_fetch_kpis)
    monkeypatch.setattr(
        overview,
        "_fetch_trend",
        lambda indicator_key: [
            {
                "year": 2022,
                "indicator_key": indicator_key,
                "indicator_name": "Persentase Penduduk Miskin (P0)",
                "unit": "Persen",
                "national_value": None,
                "previous_value": None,
                "growth_pct": None,
            },
            {
                "year": 2023,
                "indicator_key": indicator_key,
                "indicator_name": "Persentase Penduduk Miskin (P0)",
                "unit": "Persen",
                "national_value": None,
                "previous_value": None,
                "growth_pct": None,
            },
        ],
    )
    monkeypatch.setattr(
        overview,
        "_fetch_regional",
        lambda indicator_key, year=None: [
            {
                "year": year or 2023,
                "region_key": "1100",
                "region_name": "Aceh",
                "indicator_key": indicator_key,
                "indicator_name": "Persentase Penduduk Miskin (P0)",
                "value": 14.45,
                "regional_rank": 1,
                "previous_value": 14.0,
                "growth_pct": 3.21,
            }
        ],
    )
    monkeypatch.setattr(
        overview,
        "_fetch_metadata",
        lambda indicator_key: {
            "indicator_key": indicator_key,
            "indicator_code": indicator_key,
            "indicator_name": "Persentase Penduduk Miskin (P0)",
            "subject_name": "Kemiskinan dan Ketimpangan",
            "category_name": None,
            "unit": "Persen",
            "frequency": None,
            "concept": None,
            "definition": None,
            "classification": None,
            "measure": None,
            "data_source": None,
            "aggregation_method": "N/A",
        },
    )


def test_overview_allows_null_national_values(overview_null_national_monkeypatch):
    """Overview should return valid JSON when national values are unavailable."""
    response = client.get("/api/overview?indicator_key=192&region=national")
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"][0]["current_value"] is None
    assert data["kpis"][0]["yoy_growth"] is None
    assert data["kpis"][0]["national_value_status"] == "unavailable"
    assert data["trend"][0]["national_value"] is None
    assert data["trend"][0]["growth_pct"] is None


def test_overview_null_national_values_do_not_serialize_as_zero(overview_null_national_monkeypatch):
    """Null national values must remain null instead of falling back to 0."""
    response = client.get("/api/overview?indicator_key=192&region=national")
    assert response.status_code == 200
    payload = response.json()
    assert payload["kpis"][0]["current_value"] is not 0
    assert payload["kpis"][0]["current_value"] is None
    assert payload["kpis"][0]["yoy_growth"] is None
