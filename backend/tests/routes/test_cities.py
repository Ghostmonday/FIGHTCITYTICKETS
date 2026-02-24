import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add backend directory to path so imports work
backend_dir = str(Path(__file__).parents[2])
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from src.app import app
from src.services.city_registry import CityRegistry

client = TestClient(app)

@pytest.fixture
def mock_registry():
    # Create a mock registry
    mock_reg = MagicMock(spec=CityRegistry)
    # Set up default return values
    mock_reg.get_all_cities.return_value = []

    # Patch get_registry in the cities route module
    with patch("src.routes.cities.get_registry", return_value=mock_reg):
        yield mock_reg

def test_get_cities_endpoint_no_filter(mock_registry):
    # Setup mock data
    mock_registry.get_all_cities.return_value = [
        {"city_id": "city1", "name": "City 1", "is_eligible": True},
        {"city_id": "city2", "name": "City 2", "is_eligible": False},
    ]

    # Test without filter
    response = client.get("/cities/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    mock_registry.get_all_cities.assert_called_with(eligible_only=False)

def test_get_cities_endpoint_with_filter(mock_registry):
    # Setup mock data
    mock_registry.get_all_cities.return_value = [
        {"city_id": "city1", "name": "City 1", "is_eligible": True},
    ]

    # Test with filter
    response = client.get("/cities/?eligible=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    mock_registry.get_all_cities.assert_called_with(eligible_only=True)

def test_get_cities_endpoint_with_false_filter(mock_registry):
    response = client.get("/cities/?eligible=false")
    assert response.status_code == 200
    mock_registry.get_all_cities.assert_called_with(eligible_only=False)
