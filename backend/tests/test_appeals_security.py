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
        self.status = "draft"  # Initial status
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

@pytest.fixture
def mock_db_service():
    with patch("src.routes.appeals.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

def test_mass_assignment_protection(mock_db_service):
    # Setup mock data
    intake_id = 123
    citation = "TEST-SEC-001"
    mock_intake = MockIntake(intake_id, citation)

    # Configure mock responses
    mock_db_service.create_intake.return_value = mock_intake
    mock_db_service.get_intake.return_value = mock_intake

    # Mock session for update
    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # 1. Create Intake to get token
    response = client.post("/api/appeals", json={
        "citation_number": citation,
        "violation_date": "2023-01-01",
        "license_plate": "ABC1234",
        "city": "sf"
    })
    token = response.json()["token"]

    # 2. Attempt to update 'status' to 'paid' (or anything else)
    # This field is NOT exposed in AppealUpdateRequest, so Pydantic should ignore it.
    # Even if it wasn't ignored, our whitelist should block it.
    update_payload = {
        "appeal_reason": "Updated reason",
        "status": "paid",  # Malicious attempt
        "section_id": "admin_override" # Another potential target
    }

    response = client.put(
        f"/api/appeals/{intake_id}",
        json=update_payload,
        headers={"X-Appeal-Token": token}
    )

    assert response.status_code == 200, f"Update failed: {response.text}"

    # Verify database object was NOT updated with status
    # In a real DB we would check the record. Here we check setattr calls on the mock.

    # Check that 'status' was NOT set on the intake object
    assert mock_intake.status == "draft", "Status was incorrectly updated!"

    # Check that 'appeal_reason' WAS updated
    assert mock_intake.appeal_reason == "Updated reason"

    # Verify logic in appeals.py filtered it out
    # We can inspect the calls to setattr if needed, but checking the object state is sufficient.

def test_idor_prevention(mock_db_service):
    """Test that users cannot access appeals they don't own."""
    # Setup mock data for two different intakes
    intake_id_1 = 123
    intake_id_2 = 456

    mock_intake_1 = MockIntake(intake_id_1, "TEST-SEC-001")

    # Configure mock
    mock_db_service.create_intake.return_value = mock_intake_1
    mock_db_service.get_intake.return_value = mock_intake_1

    # 1. Get token for Intake 1
    response = client.post("/api/appeals", json={
        "citation_number": "TEST-SEC-001",
        "violation_date": "2023-01-01",
        "license_plate": "ABC1234",
        "city": "sf"
    })
    token_1 = response.json()["token"]

    # 2. Try to access Intake 2 using Token 1 (IDOR attempt)
    response = client.get(
        f"/api/appeals/{intake_id_2}",
        headers={"X-Appeal-Token": token_1}
    )

    # Should be Forbidden
    assert response.status_code == 403
    assert "Token invalid for this intake" in response.json()["detail"]

    # 3. Try to update Intake 2 using Token 1 (IDOR attempt)
    response = client.put(
        f"/api/appeals/{intake_id_2}",
        json={"appeal_reason": "Hacked"},
        headers={"X-Appeal-Token": token_1}
    )

    # Should be Forbidden
    assert response.status_code == 403
    assert "Token invalid for this intake" in response.json()["detail"]
