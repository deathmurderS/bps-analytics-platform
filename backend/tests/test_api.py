"""Backend API tests."""

import os
import sys
from pathlib import Path

# Add project root to path so backend package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


def test_overview_endpoint():
    """Test the overview endpoint returns a response."""
    response = client.get("/api/overview")
    # Should return either data or 404 if no data
    assert response.status_code in (200, 404)


def test_economic_trend_endpoint():
    """Test the economic trend endpoint."""
    response = client.get("/api/economic/trend")
    assert response.status_code in (200, 404)


def test_economic_regional_endpoint():
    """Test the economic regional endpoint."""
    response = client.get("/api/economic/regional")
    assert response.status_code in (200, 404)


def test_regional_ranking_endpoint():
    """Test the regional ranking endpoint."""
    response = client.get("/api/regional/ranking")
    assert response.status_code in (200, 404)


def test_trade_trend_endpoint():
    """Test the trade trend endpoint."""
    response = client.get("/api/trade/trend")
    assert response.status_code in (200, 404)


def test_trade_commodities_endpoint():
    """Test the trade commodities endpoint."""
    response = client.get("/api/trade/commodities")
    assert response.status_code in (200, 404)


def test_trade_partners_endpoint():
    """Test the trade partners endpoint."""
    response = client.get("/api/trade/partners")
    assert response.status_code in (200, 404)


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