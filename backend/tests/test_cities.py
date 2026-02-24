"""Tests for cities routes."""

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)

def test_list_cities_default_eligible():
    """Test that listing cities defaults to eligible only."""
    response = client.get("/cities")  # Using correct path /cities
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)

    # Check that blocked/caution cities are NOT present (strict policy)
    city_ids = {c["city_id"] for c in cities}
    blocked_ids = {"us-ca-san_francisco", "us-ca-los_angeles", "us-il-chicago"}
    for blocked in blocked_ids:
        assert blocked not in city_ids

    # Check active cities are present
    assert "us-ny-new_york" in city_ids
    assert "us-ma-boston" in city_ids # Now ACTIVE

def test_list_cities_all():
    """Test that listing all cities returns blocked ones too."""
    response = client.get("/cities?eligible=false")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)

    # Check that blocked/caution cities ARE present
    city_ids = {c["city_id"] for c in cities}
    assert "us-ca-san_francisco" in city_ids
    assert "us-ca-los_angeles" in city_ids
    assert "us-il-chicago" in city_ids

def test_list_cities_explicit_eligible():
    """Test explicit eligible=true."""
    response = client.get("/cities?eligible=true")
    assert response.status_code == 200
    cities = response.json()

    city_ids = {c["city_id"] for c in cities}
    blocked_ids = {"us-ca-san_francisco", "us-ca-los_angeles", "us-il-chicago"}
    for blocked in blocked_ids:
        assert blocked not in city_ids
