import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Patch Rate Limiter BEFORE importing app ---
limiter_patcher = patch("slowapi.Limiter")
MockLimiter = limiter_patcher.start()
MockLimiter.return_value.limit.side_effect = lambda *args, **kwargs: lambda func: func

from src.app import app

client = TestClient(app)

# --- Mocks ---

class MockStatus:
    def __init__(self, value):
        self.value = value

class MockAppealType:
    def __init__(self, value):
        self.value = value

class MockPayment:
    def __init__(self, status="paid", is_fulfilled=False, amount_total=5000,
                 appeal_type="standard", paid_at=None, fulfilled_at=None,
                 lob_tracking_id=None):
        self.status = MockStatus(status)
        self.is_fulfilled = is_fulfilled
        self.amount_total = amount_total
        self.appeal_type = MockAppealType(appeal_type)
        self.paid_at = paid_at
        self.fulfilled_at = fulfilled_at
        self.lob_tracking_id = lob_tracking_id
        self.lob_mail_type = None

class MockIntake:
    def __init__(self, id, citation_number, email="test@example.com"):
        self.id = id
        self.citation_number = citation_number
        self.email = email
        self.user_address_line1 = "123 Main St"
        self.user_address_line2 = None
        self.user_city = "San Francisco"
        self.user_state = "CA"
        self.user_zip = "94105"
        self.status = "submitted"
        self.created_at = datetime.now(timezone.utc)
        self.violation_date = "2023-01-01"
        self.vehicle_info = "Toyota Camry"
        self.user_name = "Test User"
        self.user_phone = "555-555-5555"
        self.drafts = []
        self.payments = []

@pytest.fixture
def mock_db_service():
    with patch("src.routes.status.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

# --- Tests ---

def test_lookup_success(mock_db_service):
    """Test successful status lookup for standard mail, paid but not mailed."""
    # Setup
    intake = MockIntake(1, "12345", "test@example.com")
    payment = MockPayment(
        status="paid",
        is_fulfilled=False,
        amount_total=5000,
        appeal_type="standard",
        paid_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        fulfilled_at=None
    )

    mock_db_service.get_intake_by_email_and_citation.return_value = intake
    mock_db_service.get_latest_payment.return_value = payment

    # Execute
    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "12345"}
    )

    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["citation_number"] == "12345"
    assert data["payment_status"] == "paid"
    assert data["mailing_status"] == "processing"
    assert data["tracking_number"] is None
    assert data["expected_delivery"] is None
    assert data["amount_total"] == 5000
    assert data["appeal_type"] == "standard"
    assert data["payment_date"] == "2023-01-01T12:00:00+00:00"
    assert data["mailed_date"] is None

def test_lookup_intake_not_found(mock_db_service):
    """Test lookup when intake is not found."""
    mock_db_service.get_intake_by_email_and_citation.return_value = None

    response = client.post(
        "/status/lookup",
        json={"email": "notfound@example.com", "citation_number": "12345"}
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"

def test_lookup_payment_not_found(mock_db_service):
    """Test lookup when intake exists but payment is not found."""
    intake = MockIntake(1, "12345")
    mock_db_service.get_intake_by_email_and_citation.return_value = intake
    mock_db_service.get_latest_payment.return_value = None

    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "12345"}
    )

    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"

def test_lookup_mailing_status_variations(mock_db_service):
    """Test different mailing statuses based on payment state."""
    intake = MockIntake(1, "12345")
    mock_db_service.get_intake_by_email_and_citation.return_value = intake

    # Case 1: Mailed (is_fulfilled=True)
    payment_mailed = MockPayment(
        status="paid",
        is_fulfilled=True,
        fulfilled_at=datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    )
    mock_db_service.get_latest_payment.return_value = payment_mailed

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["mailing_status"] == "mailed"
    assert response.json()["mailed_date"] == "2023-01-02T12:00:00+00:00"

    # Case 2: Pending (not paid, not fulfilled)
    payment_pending = MockPayment(status="unpaid", is_fulfilled=False)
    mock_db_service.get_latest_payment.return_value = payment_pending

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["mailing_status"] == "pending"

def test_lookup_tracking_info(mock_db_service):
    """Test that tracking number is returned only for certified mail."""
    intake = MockIntake(1, "12345")
    mock_db_service.get_intake_by_email_and_citation.return_value = intake

    # Case 1: Certified Mail
    payment_certified = MockPayment(
        appeal_type="certified",
        lob_tracking_id="TRACK123"
    )
    mock_db_service.get_latest_payment.return_value = payment_certified

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["tracking_number"] == "TRACK123"

    # Case 2: Standard Mail (should hide tracking even if present)
    payment_standard = MockPayment(
        appeal_type="standard",
        lob_tracking_id="TRACK456" # Should be hidden
    )
    mock_db_service.get_latest_payment.return_value = payment_standard

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["tracking_number"] is None

def test_lookup_validation_error():
    """Test validation errors for invalid input."""
    # Invalid Email
    response = client.post(
        "/status/lookup",
        json={"email": "invalid-email", "citation_number": "12345"}
    )
    assert response.status_code == 422

    # Citation too short
    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "12"}
    )
    assert response.status_code == 422

def test_lookup_internal_error(mock_db_service):
    """Test 500 error when DB service fails."""
    mock_db_service.get_intake_by_email_and_citation.side_effect = Exception("DB Error")

    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "12345"}
    )

    assert response.status_code == 500
    data = response.json()
    # Check for either standard FastAPI error (detail) or custom app error (error)
    if "error" in data:
        assert data["error"] == "INTERNAL_ERROR"
    else:
        assert data["detail"] == "Failed to lookup appeal status"
