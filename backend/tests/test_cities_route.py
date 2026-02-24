"""
Test cities route.
"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import app

client = TestClient(app)

def test_list_cities_default_eligible():
    """Test getting cities with default eligibility (True)."""
    response = client.get("/cities")
    assert response.status_code == 200
    cities = response.json()

    # Verify SF and LA are excluded
    city_ids = [c["city_id"] for c in cities]
    assert "us-ca-san_francisco" not in city_ids
    assert "us-ca-los_angeles" not in city_ids
    assert "s" not in city_ids
    assert "la" not in city_ids

    # Verify other cities are included
    assert "us-ny-new_york" in city_ids

def test_list_cities_eligible_true():
    """Test getting cities with explicit eligible=true."""
    response = client.get("/cities?eligible=true")
    assert response.status_code == 200
    cities = response.json()

    city_ids = [c["city_id"] for c in cities]
    assert "us-ca-san_francisco" not in city_ids
    assert "us-ca-los_angeles" not in city_ids

def test_list_cities_eligible_false():
    """Test getting all cities with eligible=false."""
    response = client.get("/cities?eligible=false")
    assert response.status_code == 200
    cities = response.json()

    city_ids = [c["city_id"] for c in cities]
    # Verify SF and LA are included
    assert "us-ca-san_francisco" in city_ids
    assert "us-ca-los_angeles" in city_ids
