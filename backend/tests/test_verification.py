import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import jwt
import time
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.config import settings
from src.routes.appeals import verify_appeal_token

client = TestClient(app)

class MockIntake:
    def __init__(self, id, email=None):
        self.id = id
        self.user_email = email
        self.email_verified = False
        self.citation_number = "TEST-CITATION"
        self.status = "draft"
        self.created_at = None
        self.updated_at = None

@pytest.fixture
def mock_db_service():
    with patch("src.routes.verification.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

@pytest.fixture
def mock_email_service():
    with patch("src.routes.verification.get_email_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        service_mock.send_verification_email = AsyncMock(return_value=True)
        yield service_mock

@pytest.fixture(autouse=True)
def override_auth():
    """Override auth dependency to skip token verification."""
    app.dependency_overrides[verify_appeal_token] = lambda: None
    yield
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def disable_rate_limit():
    """Disable rate limiting for tests."""
    with patch("src.middleware.rate_limit.limiter.enabled", False):
        yield

def test_send_verification_email_success(mock_db_service, mock_email_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "test@example.com")

    # Mock get_intake
    mock_db_service.get_intake.return_value = mock_intake

    response = client.post(
        f"/verification/{intake_id}/send",
        json={}  # Use default email from intake
    )

    assert response.status_code == 200, f"Response: {response.text}"
    assert response.json()["message"] == "Verification email sent"

    # Verify email service called
    mock_email_service.send_verification_email.assert_called_once()
    args, _ = mock_email_service.send_verification_email.call_args
    assert args[0] == "test@example.com"
    assert "token=" in args[1]

def test_send_verification_email_with_new_email(mock_db_service, mock_email_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "old@example.com")

    mock_db_service.get_intake.return_value = mock_intake

    new_email = "new@example.com"
    response = client.post(
        f"/verification/{intake_id}/send",
        json={"email": new_email}
    )

    assert response.status_code == 200

    # Verify email service called with NEW email
    args, _ = mock_email_service.send_verification_email.call_args
    assert args[0] == new_email

def test_confirm_verification_success(mock_db_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "test@example.com")

    # Mock DB session
    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # Generate a valid token
    payload = {
        "sub": str(intake_id),
        "email": "test@example.com",
        "type": "email_verification",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

    response = client.get(f"/verification/confirm?token={token}", follow_redirects=False)

    assert response.status_code == 307  # Redirect
    assert "verified=true" in response.headers["location"]

    # Verify DB update
    assert mock_intake.email_verified is True
    mock_session.commit.assert_called_once()

def test_confirm_verification_update_email(mock_db_service):
    intake_id = 123
    mock_intake = MockIntake(intake_id, "old@example.com")

    mock_session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = mock_intake

    # Token with NEW email
    payload = {
        "sub": str(intake_id),
        "email": "new@example.com",
        "type": "email_verification",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

    client.get(f"/verification/confirm?token={token}", follow_redirects=False)

    # Verify email updated
    assert mock_intake.user_email == "new@example.com"
    assert mock_intake.email_verified is True

def test_confirm_verification_invalid_token():
    response = client.get("/verification/confirm?token=invalid_token")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid verification token"

def test_confirm_verification_wrong_type(mock_db_service):
    # Token with wrong type
    payload = {
        "sub": "123",
        "type": "access_token",  # Wrong type
        "iat": int(time.time())
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

    response = client.get(f"/verification/confirm?token={token}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token type"
