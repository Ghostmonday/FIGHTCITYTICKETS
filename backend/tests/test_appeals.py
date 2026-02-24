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
        self.section_id = None
        self.status = "draft"
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    return mock_session

@pytest.fixture
def mock_db_service(mock_db_session):
    with patch("src.routes.appeals.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        service_mock.get_session.return_value.__enter__.return_value = mock_db_session
        yield service_mock

@pytest.fixture
def override_auth():
    app.dependency_overrides[verify_appeal_token] = lambda: None
    yield
    app.dependency_overrides = {}

def test_update_appeal_success(mock_db_service, mock_db_session, override_auth):
    """Test successful update of an appeal."""
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-123")

    # Setup mock query return
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_intake

    update_data = {
        "citation_number": "UPDATED-123",
        "appeal_reason": "New reason",
        "user_email": "new@example.com",
        "user_phone": "123-456-7890",
        "user_city": "New City"
    }

    response = client.put(f"/api/appeals/{intake_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Intake updated successfully"
    assert data["intake_id"] == intake_id

    # Verify attributes were updated on the mock object
    assert mock_intake.citation_number == "UPDATED-123"
    assert mock_intake.appeal_reason == "New reason"
    assert mock_intake.user_email == "new@example.com"
    assert mock_intake.user_phone == "123-456-7890"
    assert mock_intake.user_city == "New City"

    # Verify DB interactions
    mock_db_session.flush.assert_called_once()

def test_update_appeal_not_found(mock_db_service, mock_db_session, override_auth):
    """Test update when intake is not found."""
    intake_id = 999

    # Setup mock query return - None indicates not found
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = {
        "appeal_reason": "New reason"
    }

    response = client.put(f"/api/appeals/{intake_id}", json=update_data)

    assert response.status_code == 404
    # The app uses a custom 404 handler that returns a structured error
    data = response.json()
    assert data["error"] == "NOT_FOUND"
    assert "The requested resource was not found" in data["message"]

def test_update_appeal_no_updates(mock_db_service, mock_db_session, override_auth):
    """Test update when no data is provided."""
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-123")

    # Setup mock query return
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # Send request with no fields
    response = client.put(f"/api/appeals/{intake_id}", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No updates provided"

    # Verify no flush occurred
    mock_db_session.flush.assert_not_called()

def test_update_appeal_extra_fields_ignored(mock_db_service, mock_db_session, override_auth):
    """Test that extra fields in the request are ignored."""
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-123")
    original_status = mock_intake.status

    # Setup mock query return
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # Send request with extra fields that should be ignored
    update_data = {
        "appeal_reason": "New reason",
        "status": "paid",  # Should be ignored (not in Pydantic model)
        "id": 999,         # Should be ignored (not in Pydantic model)
        "random_field": "random" # Should be ignored (not in Pydantic model)
    }

    response = client.put(f"/api/appeals/{intake_id}", json=update_data)

    assert response.status_code == 200

    # Verify allowed field was updated
    assert mock_intake.appeal_reason == "New reason"

    # Verify ignored fields were NOT updated
    assert mock_intake.status == original_status
    assert mock_intake.id == intake_id
    assert not hasattr(mock_intake, "random_field")

def test_update_appeal_db_error(mock_db_service, mock_db_session, override_auth):
    """Test handling of database errors."""
    intake_id = 123
    mock_intake = MockIntake(intake_id, "TEST-123")

    # Setup mock query return
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # Simulate DB error on flush
    mock_db_session.flush.side_effect = Exception("Database connection failed")

    update_data = {
        "appeal_reason": "New reason"
    }

    response = client.put(f"/api/appeals/{intake_id}", json=update_data)

    assert response.status_code == 500
    # The app returns a structured error for 500
    data = response.json()
    if "detail" in data:
         # Standard HTTPException response
         assert "Failed to update intake" in data["detail"]
    else:
         # Structured error response
         assert data["error"] == "INTERNAL_ERROR"
         assert "Failed to update intake" in data["message"]
