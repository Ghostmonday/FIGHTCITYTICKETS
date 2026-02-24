import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
import httpx
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app

client = TestClient(app)

@pytest.fixture
def mock_places_api_key():
    with patch("src.routes.places.GOOGLE_PLACES_API_KEY", "test-api-key"):
        yield

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_client_cls.return_value = mock_instance
        # Async context manager methods need to return the instance
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        yield mock_instance

def test_autocomplete_success(mock_places_api_key, mock_httpx_client):
    # Mock successful response from Google
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [
            {"description": "123 Main St, San Francisco, CA, USA", "place_id": "place_123"}
        ],
        "status": "OK"
    }

    # Configure the mock instance to return the response
    mock_httpx_client.get.return_value = mock_response

    response = client.get("/places/autocomplete", params={"input": "123 Main St"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert len(data["predictions"]) == 1
    assert data["predictions"][0]["place_id"] == "place_123"

def test_autocomplete_missing_api_key():
    # Patch API key to be empty
    with patch("src.routes.places.GOOGLE_PLACES_API_KEY", ""):
        response = client.get("/places/autocomplete", params={"input": "123 Main St"})
        assert response.status_code == 503
        assert response.json()["detail"] == "Address autocomplete service not configured"

def test_autocomplete_input_too_short(mock_places_api_key):
    response = client.get("/places/autocomplete", params={"input": "ab"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Input must be at least 3 characters"

def test_autocomplete_google_api_error(mock_places_api_key, mock_httpx_client):
    # Mock Google API returning error status code
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_httpx_client.get.return_value = mock_response

    response = client.get("/places/autocomplete", params={"input": "123 Main St"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Address autocomplete service unavailable"

def test_autocomplete_timeout(mock_places_api_key, mock_httpx_client):
    # Mock timeout exception
    mock_httpx_client.get.side_effect = httpx.TimeoutException("Timeout")

    response = client.get("/places/autocomplete", params={"input": "123 Main St"})

    assert response.status_code == 504
    assert response.json()["detail"] == "Address autocomplete service timeout"

def test_autocomplete_internal_error(mock_places_api_key, mock_httpx_client):
    # Mock generic exception
    mock_httpx_client.get.side_effect = Exception("Generic Error")

    response = client.get("/places/autocomplete", params={"input": "123 Main St"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to process address autocomplete request"

# --- Details Tests ---

def test_details_success(mock_places_api_key, mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "formatted_address": "123 Main St, San Francisco, CA, USA"
        },
        "status": "OK"
    }
    mock_httpx_client.get.return_value = mock_response

    response = client.get("/places/details", params={"place_id": "place_123"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["result"]["formatted_address"] == "123 Main St, San Francisco, CA, USA"

def test_details_missing_api_key():
    with patch("src.routes.places.GOOGLE_PLACES_API_KEY", ""):
        response = client.get("/places/details", params={"place_id": "place_123"})
        assert response.status_code == 503
        assert response.json()["detail"] == "Address service not configured"

def test_details_missing_place_id(mock_places_api_key):
    response = client.get("/places/details", params={"place_id": ""})
    # Query(..., ...) implies required, but if we send empty string it might pass pydantic validation as string but fail custom check
    # Check implementation: if not place_id: raise 400
    assert response.status_code == 400
    assert response.json()["detail"] == "Place ID is required"

def test_details_google_api_error(mock_places_api_key, mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_httpx_client.get.return_value = mock_response

    response = client.get("/places/details", params={"place_id": "place_123"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Address details service unavailable"

def test_details_google_api_status_not_ok(mock_places_api_key, mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "ZERO_RESULTS"
    }
    mock_httpx_client.get.return_value = mock_response

    response = client.get("/places/details", params={"place_id": "place_123"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Address lookup failed: ZERO_RESULTS"

def test_details_timeout(mock_places_api_key, mock_httpx_client):
    mock_httpx_client.get.side_effect = httpx.TimeoutException("Timeout")

    response = client.get("/places/details", params={"place_id": "place_123"})

    assert response.status_code == 504
    assert response.json()["detail"] == "Address details service timeout"

def test_details_internal_error(mock_places_api_key, mock_httpx_client):
    mock_httpx_client.get.side_effect = Exception("Generic Error")

    response = client.get("/places/details", params={"place_id": "place_123"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to process address details request"
