import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app

client = TestClient(app)

# Helper classes for mocking
class MockIntake:
    def __init__(self, id=1, citation_number="123456"):
        self.id = id
        self.citation_number = citation_number
        self.user_address_line1 = "123 Main St"
        self.user_address_line2 = None
        self.user_city = "San Francisco"
        self.user_state = "CA"
        self.user_zip = "94102"

class MockPayment:
    def __init__(
        self,
        status="pending",
        is_fulfilled=False,
        appeal_type="standard",
        amount_total=1000,
        paid_at=None,
        fulfilled_at=None,
        lob_tracking_id=None
    ):
        self.status = MagicMock()
        self.status.value = status
        self.is_fulfilled = is_fulfilled
        self.appeal_type = MagicMock()
        self.appeal_type.value = appeal_type
        self.amount_total = amount_total
        self.paid_at = paid_at
        self.fulfilled_at = fulfilled_at
        self.lob_tracking_id = lob_tracking_id

@pytest.fixture
def mock_db_service():
    with patch("src.routes.status.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock

@pytest.fixture(autouse=True)
def disable_rate_limit():
    """Disable rate limiting for these tests, and restore afterwards."""
    from src.middleware.rate_limit import limiter
    # Also need to handle app.state.limiter if it exists
    app_limiter = None
    if hasattr(app.state, "limiter"):
        app_limiter = app.state.limiter

    original_enabled = limiter.enabled
    limiter.enabled = False
    if app_limiter:
        app_limiter.enabled = False

    yield

    limiter.enabled = original_enabled
    if app_limiter:
        app_limiter.enabled = original_enabled

def test_lookup_success(mock_db_service):
    """Test successful status lookup."""
    # Setup mocks
    mock_intake = MockIntake(citation_number="123456")
    mock_payment = MockPayment(status="paid", appeal_type="standard", amount_total=2500, paid_at=datetime.now(timezone.utc))

    mock_db_service.get_intake_by_email_and_citation.return_value = mock_intake
    mock_db_service.get_latest_payment.return_value = mock_payment

    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "123456"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["citation_number"] == "123456"
    assert data["payment_status"] == "paid"
    assert data["mailing_status"] == "processing" # paid but not fulfilled
    assert data["amount_total"] == 2500
    assert data["appeal_type"] == "standard"
    assert data["payment_date"] is not None
    assert data["mailed_date"] is None
    assert data["tracking_number"] is None

def test_lookup_intake_not_found(mock_db_service):
    """Test lookup when intake is not found."""
    mock_db_service.get_intake_by_email_and_citation.return_value = None

    response = client.post(
        "/status/lookup",
        json={"email": "notfound@example.com", "citation_number": "999999"}
    )

    assert response.status_code == 404
    # Expecting standard FastAPI error response for HTTPException
    data = response.json()
    if "detail" in data:
         # Standard FastAPI response
         pass
    elif "error" in data:
         # Custom error response
         assert data["status_code"] == 404
    else:
         pytest.fail(f"Unknown error format: {data}")

def test_lookup_payment_not_found(mock_db_service):
    """Test lookup when intake exists but payment is missing."""
    mock_intake = MockIntake()
    mock_db_service.get_intake_by_email_and_citation.return_value = mock_intake
    mock_db_service.get_latest_payment.return_value = None

    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "123456"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "error" in data

def test_lookup_mailing_status_variations(mock_db_service):
    """Test different mailing statuses based on payment state."""
    mock_intake = MockIntake()
    mock_db_service.get_intake_by_email_and_citation.return_value = mock_intake

    # Case 1: Pending Payment -> Pending Mailing
    mock_payment_pending = MockPayment(status="pending", is_fulfilled=False)
    mock_db_service.get_latest_payment.return_value = mock_payment_pending

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["mailing_status"] == "pending"

    # Case 2: Paid Payment -> Processing Mailing
    mock_payment_paid = MockPayment(status="paid", is_fulfilled=False)
    mock_db_service.get_latest_payment.return_value = mock_payment_paid

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["mailing_status"] == "processing"

    # Case 3: Fulfilled Payment -> Mailed
    mock_payment_fulfilled = MockPayment(
        status="paid",
        is_fulfilled=True,
        fulfilled_at=datetime.now(timezone.utc)
    )
    mock_db_service.get_latest_payment.return_value = mock_payment_fulfilled

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    data = response.json()
    assert data["mailing_status"] == "mailed"
    assert data["mailed_date"] is not None

def test_lookup_tracking_info(mock_db_service):
    """Test tracking number visibility for certified vs standard mail."""
    mock_intake = MockIntake()
    mock_db_service.get_intake_by_email_and_citation.return_value = mock_intake

    # Standard Mail -> No Tracking
    mock_payment_std = MockPayment(appeal_type="standard", lob_tracking_id="TRACK123")
    mock_db_service.get_latest_payment.return_value = mock_payment_std

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["tracking_number"] is None

    # Certified Mail -> Has Tracking
    mock_payment_cert = MockPayment(appeal_type="certified", lob_tracking_id="TRACK123")
    mock_db_service.get_latest_payment.return_value = mock_payment_cert

    response = client.post("/status/lookup", json={"email": "t@e.com", "citation_number": "123"})
    assert response.json()["tracking_number"] == "TRACK123"

def test_lookup_validation_error():
    """Test validation for invalid inputs."""
    # Invalid email
    response = client.post(
        "/status/lookup",
        json={"email": "not-an-email", "citation_number": "123456"}
    )
    assert response.status_code == 422

    # Citation too short
    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "12"}
    )
    assert response.status_code == 422

def test_lookup_internal_error(mock_db_service):
    """Test handling of internal server errors."""
    mock_db_service.get_intake_by_email_and_citation.side_effect = Exception("Database error")

    response = client.post(
        "/status/lookup",
        json={"email": "test@example.com", "citation_number": "123456"}
    )

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Failed to lookup appeal status"
