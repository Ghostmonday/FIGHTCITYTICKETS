import os
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client_with_mock():
    # Patch the API key in the module
    with patch("src.routes.places.GOOGLE_PLACES_API_KEY", "test-key"):
        with TestClient(app) as client:
            # Mock the get method of the shared client
            mock_get = AsyncMock()

            # Save original method
            original_get = app.state.client.get
            app.state.client.get = mock_get

            yield client, mock_get

            # Restore original method
            app.state.client.get = original_get

def test_google_places_autocomplete(client_with_mock):
    client, mock_get = client_with_mock

    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [
            {"description": "Test Place, CA, USA", "place_id": "123"}
        ],
        "status": "OK"
    }
    mock_get.return_value = mock_response

    response = client.get("/places/autocomplete?input=Test")

    assert response.status_code == 200
    data = response.json()
    assert data["predictions"][0]["description"] == "Test Place, CA, USA"

    # Verify shared client was used
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    assert kwargs["params"]["input"] == "Test"
    assert kwargs["params"]["key"] == "test-key"

def test_google_places_details(client_with_mock):
    client, mock_get = client_with_mock

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "formatted_address": "Test Address",
            "address_components": []
        },
        "status": "OK"
    }
    mock_get.return_value = mock_response

    response = client.get("/places/details?place_id=123")

    assert response.status_code == 200
    data = response.json()
    assert data["result"]["formatted_address"] == "Test Address"

    mock_get.assert_called_once()

def test_google_places_api_error(client_with_mock):
    client, mock_get = client_with_mock

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    response = client.get("/places/autocomplete?input=Test")

    assert response.status_code == 502
    assert response.json()["detail"] == "Address autocomplete service unavailable"

def test_google_places_missing_key():
    with patch("src.routes.places.GOOGLE_PLACES_API_KEY", ""):
        with TestClient(app) as client:
            response = client.get("/places/autocomplete?input=Test")
            assert response.status_code == 503
