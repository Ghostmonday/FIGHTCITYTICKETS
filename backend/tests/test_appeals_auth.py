import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.models import Intake

client = TestClient(app)

# Mock Intake object
class MockIntake:
    def __init__(self, id, citation_number):
        self.id = id
        self.citation_number = citation_number
        self.violation_date = "2023-01-01"
        self.vehicle_info = "Toyota Camry"
        self.license_plate = "ABC1234"
        self.user_name = "Test User"
        self.user_address_line1 = "123 Main St"
        self.user_address_line2 = None
        self.user_city = "San Francisco"
        self.user_state = "CA"
        self.user_zip = "94102"
        self.user_email = "test@example.com"
        self.user_phone = "555-555-5555"
        self.appeal_reason = "Test reason"
        self.selected_evidence = []
        self.signature_data = None
        self.city = "sf"
        self.status = "draft"
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

@pytest.fixture
def mock_db_service():
    with patch("src.routes.appeals.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

def test_secure_appeal_access(mock_db_service):
    # Setup mock data
    intake_id = 123
    citation = "TEST-AUTH-001"
    mock_intake = MockIntake(intake_id, citation)

    # Configure mock responses
    mock_db_service.create_intake.return_value = mock_intake
    mock_db_service.get_intake.return_value = mock_intake

    # Mock session for update
    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # 1. Create Intake (POST /appeals)
    # This should return a token
    response = client.post("/api/appeals", json={
        "citation_number": citation,
        "violation_date": "2023-01-01",
        "license_plate": "ABC1234",
        "city": "sf"
    })

    assert response.status_code == 200, f"Failed to create intake: {response.text}"
    data = response.json()

    assert "token" in data, "Token missing from response"
    assert "intake_id" in data
    assert data["intake_id"] == intake_id

    token = data["token"]

    # 2. Get Intake with Token (GET /appeals/{id})
    # Should succeed
    response = client.get(
        f"/api/appeals/{intake_id}",
        headers={"X-Appeal-Token": token}
    )
    assert response.status_code == 200, f"Failed to access with token: {response.text}"
    assert response.json()["citation_number"] == citation

    # 3. Get Intake with Token in Query Param (GET /appeals/{id}?token=...)
    # Should succeed
    response = client.get(f"/api/appeals/{intake_id}?token={token}")
    assert response.status_code == 200, "Failed to access with query token"

    # 4. Get Intake WITHOUT Token
    # IMPORTANT: We must ensure app_env is NOT "dev" for this test, as dev mode might allow it.
    # We patch settings.app_env to "test"
    with patch("src.config.settings.app_env", "test"):
        response = client.get(f"/api/appeals/{intake_id}")
        assert response.status_code == 401, "Should fail without token"

    # 5. Get Intake with INVALID Token
    with patch("src.config.settings.app_env", "test"):
        response = client.get(
            f"/api/appeals/{intake_id}",
            headers={"X-Appeal-Token": "invalid_token"}
        )
        assert response.status_code == 401, "Should fail with invalid token"

    # 6. Get Intake with Token for DIFFERENT ID
    # Use the valid token (for ID 123) to access ID 456
    with patch("src.config.settings.app_env", "test"):
        response = client.get(
            f"/api/appeals/456",
            headers={"X-Appeal-Token": token}
        )
        # Should be 403 Forbidden (Token valid but not for this resource)
        # OR 401 depending on implementation, but verify_appeal_token implementation returns 403
        assert response.status_code == 403, "Should fail with token for wrong resource"

    # 7. Update Intake with Token (PUT /appeals/{id})
    response = client.put(
        f"/api/appeals/{intake_id}",
        json={"appeal_reason": "Updated reason"},
        headers={"X-Appeal-Token": token}
    )
    assert response.status_code == 200, f"Failed to update with token: {response.text}"

    # 8. Update Intake WITHOUT Token
    with patch("src.config.settings.app_env", "test"):
        response = client.put(
            f"/api/appeals/{intake_id}",
            json={"appeal_reason": "Updated reason"}
        )
        assert response.status_code == 401, "Should fail update without token"
