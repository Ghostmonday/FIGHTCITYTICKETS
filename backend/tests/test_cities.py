"""Tests for cities routes."""

from fastapi.testclient import TestClient

from src.app import app
from src.services.city_registry import BLOCKED_CITIES

client = TestClient(app)

def test_list_cities_default_eligible():
    """Test that listing cities defaults to eligible only."""
    response = client.get("/api/cities")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)

    # Check that blocked cities are NOT present
    # We filter out the IDs that are actual city IDs (e.g. "us-ca-san_francisco")
    city_ids = {c["city_id"] for c in cities}

    # Check actual IDs
    blocked_ids = {"us-ca-san_francisco", "us-ca-los_angeles"}
    for blocked in blocked_ids:
        assert blocked not in city_ids

def test_list_cities_all():
    """Test that listing all cities returns blocked ones too."""
    response = client.get("/api/cities?eligible=false")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)

    # Check that blocked cities ARE present
    city_ids = {c["city_id"] for c in cities}
    assert "us-ca-san_francisco" in city_ids
    assert "us-ca-los_angeles" in city_ids

def test_list_cities_explicit_eligible():
    """Test explicit eligible=true."""
    response = client.get("/api/cities?eligible=true")
    assert response.status_code == 200
    cities = response.json()

    city_ids = {c["city_id"] for c in cities}
    blocked_ids = {"us-ca-san_francisco", "us-ca-los_angeles"}
    for blocked in blocked_ids:
        assert blocked not in city_ids
