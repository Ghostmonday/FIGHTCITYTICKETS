import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.services.citation import CitationValidationResult

client = TestClient(app)

@pytest.fixture
def mock_stripe_service():
    with patch("src.routes.checkout.StripeService") as mock:
        yield mock

@pytest.fixture
def mock_db_service():
    with patch("src.routes.checkout.get_db_service") as mock:
        yield mock

@pytest.fixture
def mock_citation_validator():
    with patch("src.services.citation.CitationValidator.validate_citation") as mock:
        yield mock

def test_create_appeal_checkout_success(mock_stripe_service, mock_db_service, mock_citation_validator):
    # Setup mocks
    mock_citation_validator.return_value = CitationValidationResult(
        is_valid=True,
        citation_number="123456",
        agency="SFMTA",
        is_past_deadline=False
    )

    # Mock DB interaction
    mock_session = MagicMock()
    mock_db_service.return_value.get_session.return_value.__enter__.return_value = mock_session
    mock_db_service.return_value.get_intake_by_citation.return_value = None # No existing intake

    # Mock session.execute result for INSERT
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1,) # intake_id = 1
    mock_session.execute.return_value = mock_result

    # Mock Stripe
    mock_stripe_instance = mock_stripe_service.return_value
    mock_stripe_instance.create_session = AsyncMock(return_value={
        "id": "cs_test_123",
        "url": "https://checkout.stripe.com/test"
    })

    payload = {
        "citation_number": "123456",
        "city_id": "us-ca-san_francisco",
        "user_email": "test@example.com",
        "user_attestation": True
    }

    response = client.post("/checkout/create-appeal-checkout", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["checkout_url"] == "https://checkout.stripe.com/test"
    assert data["session_id"] == "cs_test_123"
    assert "clerical_id" in data
    assert data["clerical_id"].startswith("ND-")

def test_create_appeal_checkout_invalid_city():
    payload = {
        "citation_number": "123456",
        "city_id": "invalid_city", # Missing hyphen
        "user_email": "test@example.com",
        "user_attestation": True
    }
    response = client.post("/checkout/create-appeal-checkout", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid city ID format"

def test_create_appeal_checkout_blocked_state():
    payload = {
        "citation_number": "123456",
        "city_id": "us-tx-dallas", # TX is blocked
        "user_email": "test@example.com",
        "user_attestation": True
    }
    response = client.post("/checkout/create-appeal-checkout", json=payload)
    assert response.status_code == 403
    assert "legal restrictions" in response.json()["detail"]

def test_create_appeal_checkout_invalid_citation(mock_citation_validator):
    mock_citation_validator.return_value = CitationValidationResult(
        is_valid=False,
        citation_number="INVALID",
        agency="UNKNOWN",
        error_message="Invalid format"
    )

    payload = {
        "citation_number": "INVALID",
        "city_id": "us-ca-san_francisco",
        "user_email": "test@example.com",
        "user_attestation": True
    }
    response = client.post("/checkout/create-appeal-checkout", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid format"

def test_create_appeal_checkout_existing_paid_payment(mock_db_service, mock_citation_validator):
    mock_citation_validator.return_value = CitationValidationResult(
        is_valid=True,
        citation_number="123456",
        agency="SFMTA"
    )

    mock_session = MagicMock()
    mock_db_service.return_value.get_session.return_value.__enter__.return_value = mock_session

    # Mock existing intake
    mock_intake = MagicMock()
    mock_intake.id = 1
    mock_db_service.return_value.get_intake_by_citation.return_value = mock_intake

    # Mock existing paid payment
    mock_payment = MagicMock()
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_payment]

    payload = {
        "citation_number": "123456",
        "city_id": "us-ca-san_francisco",
        "user_email": "test@example.com",
        "user_attestation": True
    }
    response = client.post("/checkout/create-appeal-checkout", json=payload)
    assert response.status_code == 409
    assert "payment already exists" in response.json()["detail"]

def test_create_appeal_checkout_stripe_error(mock_stripe_service, mock_db_service, mock_citation_validator):
    mock_citation_validator.return_value = CitationValidationResult(
        is_valid=True,
        citation_number="123456",
        agency="SFMTA"
    )

    mock_session = MagicMock()
    mock_db_service.return_value.get_session.return_value.__enter__.return_value = mock_session
    mock_db_service.return_value.get_intake_by_citation.return_value = None
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1,)
    mock_session.execute.return_value = mock_result

    mock_stripe_instance = mock_stripe_service.return_value
    mock_stripe_instance.create_session = AsyncMock(side_effect=Exception("Stripe API Error"))

    payload = {
        "citation_number": "123456",
        "city_id": "us-ca-san_francisco",
        "user_email": "test@example.com",
        "user_attestation": True
    }
    response = client.post("/checkout/create-appeal-checkout", json=payload)
    assert response.status_code == 500
    assert "Failed to create checkout session" in response.json()["detail"]

def test_get_session_status_success(mock_stripe_service, mock_db_service):
    # Mock Stripe session
    mock_stripe_instance = mock_stripe_service.return_value
    mock_stripe_instance.get_session.return_value = {
        "status": "complete",
        "payment_status": "paid"
    }

    # Mock DB
    mock_session = MagicMock()
    mock_db_service.return_value.get_session.return_value.__enter__.return_value = mock_session

    # Mock raw SQL query for payment status
    mock_row = ("paid", "tracking_123")
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_session.execute.return_value = mock_result

    # Mock ORM queries for clerical_id
    mock_payment = MagicMock()
    mock_payment.intake_id = 1
    mock_intake = MagicMock()
    mock_intake.clerical_id = "ND-1234"

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter

    # We need to return mock_payment first, then mock_intake
    mock_filter.first.side_effect = [mock_payment, mock_intake]

    response = client.get("/checkout/session-status?session_id=cs_test_123")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["payment_status"] == "paid"
    assert data["mailing_status"] == "fulfilled"
    assert data["tracking_number"] == "tracking_123"
    assert data["clerical_id"] == "ND-1234"

def test_get_session_status_not_found(mock_stripe_service):
    mock_stripe_instance = mock_stripe_service.return_value
    mock_stripe_instance.get_session.return_value = None

    response = client.get("/checkout/session-status?session_id=invalid")
    assert response.status_code == 404
