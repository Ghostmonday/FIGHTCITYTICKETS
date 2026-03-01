import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.routes.appeals import verify_appeal_token

client = TestClient(app)

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
        self.email_verified = False
        self.user_phone = "555-555-5555"
        self.appeal_reason = "Test reason"
        self.selected_evidence = []
        self.signature_data = None
        self.city = "sf"
        self.section_id = None
        self.status = "draft"
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

@pytest.fixture
def mock_db_service():
    with patch("src.routes.appeals.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

@pytest.fixture(autouse=True)
def override_auth():
    """Override auth dependency to skip token verification."""
    app.dependency_overrides[verify_appeal_token] = lambda: None
    yield
    app.dependency_overrides = {}

def test_update_appeal_success(mock_db_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-UPDATE-001")

    # Mock DB session and query
    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    update_data = {
        "citation_number": "UPDATED-123",
        "appeal_reason": "Updated reason",
        "user_email": "updated@example.com",
        "section_id": "section-456"
    }

    response = client.put(f"/api/appeals/{intake_id}", json=update_data)

    assert response.status_code == 200, f"Update failed: {response.text}"
    assert response.json()["message"] == "Intake updated successfully"
    assert response.json()["intake_id"] == intake_id

    # Verify intake object was updated
    assert mock_intake.citation_number == "UPDATED-123"
    assert mock_intake.appeal_reason == "Updated reason"
    assert mock_intake.user_email == "updated@example.com"
    assert mock_intake.section_id == "section-456"

    # Verify DB flush was called
    mock_session.flush.assert_called_once()

def test_update_appeal_not_found(mock_db_service):
    intake_id = 999

    # Mock DB session to return None
    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None

    response = client.put(f"/api/appeals/{intake_id}", json={"appeal_reason": "test"})

    assert response.status_code == 404
    # The application uses a custom error handler that returns "message" instead of "detail"
    data = response.json()
    assert "message" in data
    assert "not found" in data["message"].lower()

def test_update_appeal_no_updates(mock_db_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-NO-UPDATE")

    # Mock DB session
    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session

    response = client.put(f"/api/appeals/{intake_id}", json={})

    assert response.status_code == 200
    assert response.json()["message"] == "No updates provided"

    # Verify DB query was NOT called (optimization check)
    mock_session.query.assert_not_called()

def test_update_appeal_allowed_columns_only(mock_db_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-ALLOWED")

    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    response = client.put(f"/api/appeals/{intake_id}", json={
        "citation_number": "VALID-123",
        "invalid_field": "SHOULD_BE_IGNORED"
    })

    assert response.status_code == 200
    assert mock_intake.citation_number == "VALID-123"
    # Ensure invalid field was not set on the object
    assert not hasattr(mock_intake, "invalid_field")

def test_update_appeal_db_error(mock_db_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-ERROR")

    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # Simulate DB error on flush
    mock_session.flush.side_effect = Exception("DB Connection Lost")

    response = client.put(f"/api/appeals/{intake_id}", json={"appeal_reason": "test"})

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Failed to update intake" in data["detail"]
