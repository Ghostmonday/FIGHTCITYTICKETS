import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.routes.appeals import verify_appeal_token, create_access_token

client = TestClient(app)

@pytest.fixture
def mock_db_service():
    with patch("src.routes.appeals.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

@pytest.fixture
def mock_email_service():
    with patch("src.routes.appeals.get_email_service") as mock:
        service_mock = MagicMock()
        service_mock.send_save_progress_link = AsyncMock(return_value=True)
        mock.return_value = service_mock
        yield service_mock

@pytest.fixture(autouse=True)
def override_auth():
    """Override auth dependency to skip token verification."""
    # We want to test the endpoint logic, assuming auth passed.
    # In integration tests we would test auth, but here we mock it.
    app.dependency_overrides[verify_appeal_token] = lambda: None
    yield
    app.dependency_overrides = {}

def test_send_resume_link_success(mock_db_service, mock_email_service):
    intake_id = 123
    mock_intake = MagicMock()
    mock_intake.id = intake_id
    mock_intake.citation_number = "TEST-RESUME-001"

    mock_db_service.get_intake.return_value = mock_intake

    response = client.post(
        f"/api/appeals/{intake_id}/send-link",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Resume link sent successfully"}

    # Verify email service was called
    mock_email_service.send_save_progress_link.assert_called_once()
    call_args = mock_email_service.send_save_progress_link.call_args
    assert call_args.kwargs["email"] == "test@example.com"
    assert call_args.kwargs["citation_number"] == "TEST-RESUME-001"
    assert "resume_link" in call_args.kwargs
    assert f"intake_id={intake_id}" in call_args.kwargs["resume_link"]
    assert "token=" in call_args.kwargs["resume_link"]

def test_send_resume_link_not_found(mock_db_service, mock_email_service):
    intake_id = 999
    mock_db_service.get_intake.return_value = None

    response = client.post(
        f"/api/appeals/{intake_id}/send-link",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["message"] == f"Intake {intake_id} not found"

def test_send_resume_link_email_failure(mock_db_service, mock_email_service):
    intake_id = 123
    mock_intake = MagicMock()
    mock_db_service.get_intake.return_value = mock_intake

    # Simulate email service failure
    mock_email_service.send_save_progress_link.side_effect = Exception("Email failed")

    response = client.post(
        f"/api/appeals/{intake_id}/send-link",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 500
    assert "Failed to send resume link" in response.json()["detail"]
