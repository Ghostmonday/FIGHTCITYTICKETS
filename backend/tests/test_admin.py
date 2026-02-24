import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, mock_open
import os
import sys
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.models import Intake, Draft, Payment, PaymentStatus
from src.routes.admin import limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Disable rate limiting for all tests in this module."""
    limiter.enabled = False
    yield
    limiter.enabled = True

@pytest.fixture
def mock_db_service():
    with patch("src.routes.admin.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

@pytest.fixture
def mock_env_secret():
    with patch.dict(os.environ, {"ADMIN_SECRET": "secret123"}):
        yield

@pytest.fixture
def mock_env_allowed_ips():
    with patch.dict(os.environ, {"ADMIN_SECRET": "secret123", "ADMIN_ALLOWED_IPS": "127.0.0.1,testclient"}):
        yield

# --- Auth Tests ---

def test_admin_auth_missing_header(mock_env_secret):
    response = client.get("/admin/stats")
    assert response.status_code == 401  # Unauthorized (both header and cookie missing)

def test_admin_auth_invalid_header(mock_env_secret):
    response = client.get("/admin/stats", headers={"X-Admin-Secret": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid admin secret"

def test_admin_auth_no_env_var():
    # We need to ensure ADMIN_SECRET is not set.
    # We can use patch.dict to remove it.
    with patch.dict(os.environ):
        if "ADMIN_SECRET" in os.environ:
            del os.environ["ADMIN_SECRET"]
        response = client.get("/admin/stats", headers={"X-Admin-Secret": "secret123"})
        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]

def test_admin_auth_success(mock_env_secret, mock_db_service):
    # Mock DB health check to avoid 503 from endpoint logic
    mock_db_service.health_check.return_value = True
    # Mock session
    session_mock = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session_mock
    # Mock query results to return 0/empty
    session_mock.query.return_value.scalar.return_value = 0

    response = client.get("/admin/stats", headers={"X-Admin-Secret": "secret123"})
    assert response.status_code == 200

def test_admin_auth_ip_allowed(mock_env_allowed_ips, mock_db_service):
    mock_db_service.health_check.return_value = True
    session_mock = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session_mock
    session_mock.query.return_value.scalar.return_value = 0

    # TestClient usually sends requests from 'testclient' hostname
    # We added 'testclient' to allowed IPs in the fixture
    response = client.get("/admin/stats", headers={"X-Admin-Secret": "secret123"})
    assert response.status_code == 200

def test_admin_auth_ip_forbidden(mock_env_allowed_ips):
    # "testclient" IS in the allowed list for the fixture above.
    # Let's override it to something else where "testclient" is NOT allowed.
    with patch.dict(os.environ, {"ADMIN_SECRET": "secret123", "ADMIN_ALLOWED_IPS": "10.0.0.1"}):
        response = client.get("/admin/stats", headers={"X-Admin-Secret": "secret123"})
        assert response.status_code == 403
        assert "IP not authorized" in response.json()["detail"]

# --- Endpoint Tests ---

def test_get_system_stats(mock_env_secret, mock_db_service):
    mock_db_service.health_check.return_value = True
    session_mock = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session_mock

    # Configure scalars for query chain
    query_mock = session_mock.query.return_value
    query_mock.filter.return_value = query_mock
    query_mock.scalar.side_effect = [10, 5, 8, 3, 5]

    response = client.get("/admin/stats", headers={"X-Admin-Secret": "secret123"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_intakes"] == 10
    assert data["total_drafts"] == 5
    assert data["total_payments"] == 8
    assert data["pending_fulfillments"] == 3
    assert data["fulfilled_count"] == 5
    assert data["db_status"] == "connected"

def test_get_recent_activity(mock_env_secret, mock_db_service):
    mock_db_service.health_check.return_value = True
    session_mock = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session_mock

    # Mock Intakes
    mock_intake = MagicMock(spec=Intake)
    mock_intake.id = 1
    mock_intake.created_at = datetime.now(timezone.utc)
    mock_intake.citation_number = "CIT123"
    mock_intake.status = "submitted"

    # Mock payment on intake
    mock_payment = MagicMock(spec=Payment)
    mock_payment.status = PaymentStatus.PAID
    mock_payment.amount_total = 1000
    mock_payment.lob_tracking_id = "TRACK123"

    mock_intake.payments = [mock_payment]

    # Mock query chain
    query_mock = session_mock.query.return_value
    query_mock.options.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_intake]

    response = client.get("/admin/activity", headers={"X-Admin-Secret": "secret123"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["citation_number"] == "CIT123"
    assert data[0]["payment_status"] == "paid"
    assert data[0]["amount"] == 10.0  # 1000 / 100
    assert data[0]["lob_tracking_id"] == "TRACK123"

def test_get_intake_detail(mock_env_secret, mock_db_service):
    mock_db_service.health_check.return_value = True
    session_mock = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session_mock

    mock_intake = MagicMock(spec=Intake)
    mock_intake.id = 1
    mock_intake.created_at = datetime.now(timezone.utc)
    mock_intake.citation_number = "CIT123"
    mock_intake.status = "submitted"
    mock_intake.user_name = "John Doe"
    mock_intake.user_email = "john@example.com"
    mock_intake.user_phone = "555-1234"
    mock_intake.user_address_line1 = "123 Main St"
    mock_intake.user_address_line2 = None
    mock_intake.user_city = "City"
    mock_intake.user_state = "ST"
    mock_intake.user_zip = "12345"
    mock_intake.violation_date = "2023-01-01"
    mock_intake.vehicle_info = "Car"

    # Mock Drafts
    mock_draft = MagicMock(spec=Draft)
    mock_draft.created_at = datetime.now(timezone.utc)
    mock_draft.draft_text = "Dear Sir/Madam..."
    mock_intake.drafts = [mock_draft]

    # Mock Payments
    mock_payment = MagicMock(spec=Payment)
    mock_payment.created_at = datetime.now(timezone.utc)
    mock_payment.status = PaymentStatus.PAID
    mock_payment.amount_total = 5000
    mock_payment.lob_tracking_id = "TRACK456"
    mock_payment.lob_mail_type = "certified"
    mock_payment.is_fulfilled = True
    mock_intake.payments = [mock_payment]

    session_mock.query.return_value.options.return_value.filter.return_value.first.return_value = mock_intake

    response = client.get("/admin/intake/1", headers={"X-Admin-Secret": "secret123"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "John Doe"
    assert data["draft_text"] == "Dear Sir/Madam..."
    assert data["payment_status"] == "paid"
    assert data["amount_total"] == 50.0
    assert data["is_fulfilled"] == True

def test_get_intake_detail_not_found(mock_env_secret, mock_db_service):
    mock_db_service.health_check.return_value = True
    session_mock = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session_mock
    session_mock.query.return_value.options.return_value.filter.return_value.first.return_value = None

    response = client.get("/admin/intake/999", headers={"X-Admin-Secret": "secret123"})
    assert response.status_code == 404
    # 404 is handled by custom handler in app.py which maps 'detail' to 'message'
    # The default 404 handler returns generic message
    assert response.json()["message"] == "The requested resource was not found"

def test_get_server_logs(mock_env_secret):
    # Mock os.path.exists and open
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("builtins.open", mock_open(read_data="log line 1\nlog line 2\n")) as mock_file:
            response = client.get("/admin/logs", headers={"X-Admin-Secret": "secret123"})
            assert response.status_code == 200
            assert response.json()["logs"] == "log line 1\nlog line 2\n"

def test_get_server_logs_not_found(mock_env_secret):
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        response = client.get("/admin/logs", headers={"X-Admin-Secret": "secret123"})
        assert response.status_code == 200
        assert "not found" in response.json()["logs"]
