import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_list_cities_default():
    """Test getting cities list (default eligible=True)."""
    response = client.get("/cities")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)

    # Check that SF and LA are NOT present
    city_ids = [c["city_id"] for c in cities]
    assert "us-ca-san_francisco" not in city_ids
    assert "us-ca-los_angeles" not in city_ids
    assert "s" not in city_ids
    assert "la" not in city_ids

    # Check that other cities ARE present
    assert "us-ny-new_york" in city_ids

def test_list_cities_eligible_false():
    """Test getting cities list with eligible=false."""
    response = client.get("/cities?eligible=false")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)

    # Check that SF and LA ARE present
    city_ids = [c["city_id"] for c in cities]
    assert "us-ca-san_francisco" in city_ids
    assert "us-ca-los_angeles" in city_ids

def test_list_cities_eligible_explicit_true():
    """Test getting cities list with eligible=true explicitly."""
    response = client.get("/cities?eligible=true")
    assert response.status_code == 200
    cities = response.json()

    # Check that SF and LA are NOT present
    city_ids = [c["city_id"] for c in cities]
    assert "us-ca-san_francisco" not in city_ids
