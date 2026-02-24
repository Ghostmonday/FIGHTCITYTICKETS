import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.routes.admin import limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Disable rate limiting for all tests in this module."""
    limiter.enabled = False
    yield
    limiter.enabled = True

@pytest.fixture
def mock_validator():
    # Patch get_address_validator where it is imported in admin.py
    # Since we haven't modified admin.py yet, this patch target might be tricky if we test before implementation.
    # But patching the module where it's defined (src.services.address_validator.get_address_validator) usually works if it's called via that function.
    # However, if admin.py does `from ... import get_address_validator`, we need to patch `src.routes.admin.get_address_validator`.
    # Let's assume we'll import it in admin.py as `from ..services.address_validator import get_address_validator`.

    with patch("src.services.address_validator.get_address_validator") as mock:
        validator_instance = MagicMock()
        mock.return_value = validator_instance
        yield validator_instance

@pytest.fixture
def mock_env_secret():
    with patch.dict(os.environ, {"ADMIN_SECRET": "secret123"}):
        yield

def test_override_address_success(mock_env_secret, mock_validator):
    mock_validator.update_city_address.return_value = True

    payload = {
        "city_id": "us-ny-new_york",
        "address_text": "New Address, NY 10001"
    }

    # We need to patch where it is used in the route handler.
    # If the route imports `get_address_validator` from services, patching `src.services.address_validator.get_address_validator` should affect it IF it calls the function inside the handler.
    # If it calls it at module level (unlikely for a service getter), then we'd have issues.
    # Safest is to patch the import in `src.routes.admin`.
    with patch("src.routes.admin.get_address_validator") as route_mock:
        route_mock.return_value = mock_validator

        response = client.post(
            "/admin/address/override",
            json=payload,
            headers={"X-Admin-Secret": "secret123"}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_validator.update_city_address.assert_called_with(
            "us-ny-new_york",
            "New Address, NY 10001",
            None
        )

def test_override_address_with_dict(mock_env_secret, mock_validator):
    mock_validator.update_city_address.return_value = True

    payload = {
        "city_id": "us-ny-new_york",
        "address_components": {
            "address1": "123 St",
            "city": "NY",
            "state": "NY",
            "zip": "10001"
        }
    }

    with patch("src.routes.admin.get_address_validator") as route_mock:
        route_mock.return_value = mock_validator

        response = client.post(
            "/admin/address/override",
            json=payload,
            headers={"X-Admin-Secret": "secret123"}
        )

        assert response.status_code == 200
        mock_validator.update_city_address.assert_called_with(
            "us-ny-new_york",
            payload["address_components"],
            None
        )

def test_override_address_fail(mock_env_secret, mock_validator):
    mock_validator.update_city_address.return_value = False

    payload = {
        "city_id": "invalid-city",
        "address_text": "addr"
    }

    with patch("src.routes.admin.get_address_validator") as route_mock:
        route_mock.return_value = mock_validator

        response = client.post(
            "/admin/address/override",
            json=payload,
            headers={"X-Admin-Secret": "secret123"}
        )

        assert response.status_code == 400
        assert "Failed to update" in response.json()["detail"]

def test_override_address_missing_data(mock_env_secret):
    payload = {
        "city_id": "us-ny-new_york"
        # Missing address info
    }

    response = client.post(
        "/admin/address/override",
        json=payload,
        headers={"X-Admin-Secret": "secret123"}
    )

    assert response.status_code == 422
    assert "Either address_text or address_components must be provided" in response.json()["detail"]
