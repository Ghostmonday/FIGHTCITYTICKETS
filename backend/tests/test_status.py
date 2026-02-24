import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import status module FIRST to capture the local limiter instance
# before app.py overwrites it with the global one.
from src.routes import status
# We capture this instance because it's the one trapped in the route decorator
original_limiter_instance = status.limiter

from src.app import app

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(autouse=True)
def bypass_rate_limit():
    """Bypass rate limiting by disabling the limiter instance used by the route."""
    # Store original state
    was_enabled = original_limiter_instance.enabled

    # Disable limiter
    original_limiter_instance.enabled = False

    yield

    # Restore state
    original_limiter_instance.enabled = was_enabled

@pytest.fixture
def mock_db_service():
    with patch("src.routes.status.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

# --- Mocks ---

class MockIntake:
    def __init__(self, id=1, citation_number="123456"):
        self.id = id
        self.citation_number = citation_number

class MockPaymentStatus:
    def __init__(self, value):
        self.value = value

class MockAppealType:
    def __init__(self, value):
        self.value = value

class MockPayment:
    def __init__(self,
                 status="pending",
                 is_fulfilled=False,
                 amount_total=5000,
                 appeal_type="standard",
                 paid_at=None,
                 fulfilled_at=None,
                 lob_tracking_id=None):
        self.status = MockPaymentStatus(status)
        self.is_fulfilled = is_fulfilled
        self.amount_total = amount_total
        self.appeal_type = MockAppealType(appeal_type)
        self.paid_at = paid_at
        self.fulfilled_at = fulfilled_at
        self.lob_tracking_id = lob_tracking_id

# --- Tests ---

def test_lookup_success(mock_db_service):
    """Test successful status lookup for a standard appeal."""
    # Setup
    citation = "123456"
    email = "test@example.com"
    intake = MockIntake(citation_number=citation)
    payment = MockPayment(status="pending", appeal_type="standard")

    mock_db_service.get_intake_by_email_and_citation.return_value = intake
    mock_db_service.get_latest_payment.return_value = payment

    # Execute
    response = client.post("/status/lookup", json={
        "email": email,
        "citation_number": citation
    })

    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["citation_number"] == citation
    assert data["payment_status"] == "pending"
    assert data["mailing_status"] == "pending"
    assert data["tracking_number"] is None
    assert data["amount_total"] == 5000
    assert data["appeal_type"] == "standard"

def test_lookup_intake_not_found(mock_db_service):
    """Test lookup when intake is not found."""
    mock_db_service.get_intake_by_email_and_citation.return_value = None

    response = client.post("/status/lookup", json={
        "email": "notfound@example.com",
        "citation_number": "000000"
    })

    assert response.status_code == 404
    # Check 'message' instead of 'detail' because of custom error handler
    assert response.json()["message"] == "No appeal found with that email and citation number"

def test_lookup_payment_not_found(mock_db_service):
    """Test lookup when payment is not found for an existing intake."""
    intake = MockIntake()
    mock_db_service.get_intake_by_email_and_citation.return_value = intake
    mock_db_service.get_latest_payment.return_value = None

    response = client.post("/status/lookup", json={
        "email": "test@example.com",
        "citation_number": "123456"
    })

    assert response.status_code == 404
    assert response.json()["message"] == "No payment found for this appeal"

def test_lookup_mailing_status_variations(mock_db_service):
    """Test different mailing statuses based on payment state."""
    citation = "123456"
    intake = MockIntake(citation_number=citation)
    mock_db_service.get_intake_by_email_and_citation.return_value = intake

    # Case 1: Paid but not fulfilled -> processing
    paid_date = datetime.now(timezone.utc)
    payment_paid = MockPayment(
        status="paid",
        is_fulfilled=False,
        paid_at=paid_date
    )
    mock_db_service.get_latest_payment.return_value = payment_paid

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": citation})
    assert response.json()["mailing_status"] == "processing"
    assert response.json()["payment_date"] == paid_date.isoformat()

    # Case 2: Fulfilled -> mailed
    fulfilled_date = datetime.now(timezone.utc)
    payment_mailed = MockPayment(
        status="paid",
        is_fulfilled=True,
        paid_at=paid_date,
        fulfilled_at=fulfilled_date
    )
    mock_db_service.get_latest_payment.return_value = payment_mailed

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": citation})
    assert response.json()["mailing_status"] == "mailed"
    assert response.json()["mailed_date"] == fulfilled_date.isoformat()

def test_lookup_tracking_info(mock_db_service):
    """Test tracking number is returned only for certified mail."""
    citation = "123456"
    intake = MockIntake(citation_number=citation)
    mock_db_service.get_intake_by_email_and_citation.return_value = intake

    # Case 1: Standard mail (should allow None tracking)
    payment_standard = MockPayment(appeal_type="standard", lob_tracking_id="TRACK123")
    mock_db_service.get_latest_payment.return_value = payment_standard

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": citation})
    assert response.json()["tracking_number"] is None

    # Case 2: Certified mail (should return tracking)
    payment_certified = MockPayment(appeal_type="certified", lob_tracking_id="TRACK123")
    mock_db_service.get_latest_payment.return_value = payment_certified

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": citation})
    assert response.json()["tracking_number"] == "TRACK123"

def test_lookup_validation_error(mock_db_service):
    """Test input validation."""
    # Invalid email
    response = client.post("/status/lookup", json={
        "email": "invalid-email",
        "citation_number": "123456"
    })
    assert response.status_code == 422

    # Citation too short
    response = client.post("/status/lookup", json={
        "email": "test@example.com",
        "citation_number": "12"
    })
    assert response.status_code == 422

def test_lookup_internal_error(mock_db_service):
    """Test handling of internal server errors."""
    mock_db_service.get_intake_by_email_and_citation.side_effect = Exception("Database failure")

    response = client.post("/status/lookup", json={
        "email": "test@example.com",
        "citation_number": "123456"
    })

    assert response.status_code == 500
    # HTTPException(500) returns 'detail' unless intercepted by a custom handler that changes it
    assert response.json()["detail"] == "Failed to lookup appeal status"
