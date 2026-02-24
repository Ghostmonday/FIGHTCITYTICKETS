import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.services.citation import CitationValidationResult

client = TestClient(app)

@pytest.fixture
def mock_citation_validator():
    # Patching where it is defined because it is imported locally inside the function
    with patch("src.services.citation.CitationValidator") as mock:
        yield mock

@pytest.fixture
def mock_db_service():
    # Patching in the checkout module
    with patch("src.routes.checkout.get_db_service") as mock:
        service = MagicMock()
        mock.return_value = service
        yield service

@pytest.fixture
def mock_stripe_service():
    # Patching in the checkout module
    with patch("src.routes.checkout.StripeService") as mock:
        service_instance = MagicMock()
        # Mock create_session as async method
        service_instance.create_session = AsyncMock()
        # Mock get_session as regular method (it seems it was synchronous in original code but check!)
        # Wait, if create_session is async, likely get_session is too?
        # Checking checkout.py:
        # session = stripe_svc.get_session(session_id)
        # It is NOT awaited in get_session_status.
        service_instance.get_session = MagicMock()

        mock.return_value = service_instance
        yield service_instance

def test_create_appeal_checkout_success(mock_citation_validator, mock_db_service, mock_stripe_service):
    # Setup - mock validation success
    # CitationValidator.validate_citation returns a CitationValidationResult object
    mock_citation_validator.validate_citation.return_value = CitationValidationResult(
        is_valid=True,
        citation_number="123456",
        agency="SFMTA",
        city_id="us-ca-san_francisco",
        section_id="sfmta"
    )

    # Mock DB
    session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session
    mock_db_service.get_intake_by_citation.return_value = None

    # Mock Stripe
    mock_stripe_service.create_session.return_value = {
        "url": "http://checkout.url",
        "id": "cs_test_123"
    }

    response = client.post("/checkout/create-appeal-checkout", json={
        "citation_number": "123456",
        "city_id": "us-ca-san_francisco",
        "user_attestation": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["checkout_url"] == "http://checkout.url"
    assert data["session_id"] == "cs_test_123"
    assert "clerical_id" in data

def test_create_appeal_checkout_invalid_city():
    response = client.post("/checkout/create-appeal-checkout", json={
        "citation_number": "123456",
        "city_id": "invalidcity",
        "user_attestation": True
    })
    assert response.status_code == 400
    assert "Invalid city ID format" in response.json()["detail"]

def test_create_appeal_checkout_blocked_state():
    response = client.post("/checkout/create-appeal-checkout", json={
        "citation_number": "123456",
        "city_id": "us-tx-dallas", # TX is blocked by default
        "user_attestation": True
    })
    assert response.status_code == 403
    assert "cannot process appeals" in response.json()["detail"]

def test_create_appeal_checkout_invalid_citation(mock_citation_validator):
    mock_citation_validator.validate_citation.return_value = CitationValidationResult(
        is_valid=False,
        citation_number="BAD123",
        agency="UNKNOWN",
        error_message="Bad citation"
    )

    response = client.post("/checkout/create-appeal-checkout", json={
        "citation_number": "BAD123",
        "city_id": "us-ca-san_francisco",
        "user_attestation": True
    })

    assert response.status_code == 400
    assert "Bad citation" in response.json()["detail"]

def test_create_appeal_checkout_existing_payment(mock_citation_validator, mock_db_service):
    mock_citation_validator.validate_citation.return_value = CitationValidationResult(
        is_valid=True,
        citation_number="PAID123",
        agency="SFMTA"
    )

    session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session

    # Mock existing intake
    mock_intake = MagicMock()
    mock_intake.id = 1
    mock_db_service.get_intake_by_citation.return_value = mock_intake

    # Mock payment query result
    mock_payment = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = [mock_payment]

    response = client.post("/checkout/create-appeal-checkout", json={
        "citation_number": "PAID123",
        "city_id": "us-ca-san_francisco",
        "user_attestation": True
    })

    assert response.status_code == 409
    assert "payment already exists" in response.json()["detail"]

def test_create_appeal_checkout_stripe_error(mock_citation_validator, mock_db_service, mock_stripe_service):
    mock_citation_validator.validate_citation.return_value = CitationValidationResult(
        is_valid=True,
        citation_number="123456",
        agency="SFMTA"
    )

    session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session
    mock_db_service.get_intake_by_citation.return_value = None

    mock_stripe_service.create_session.side_effect = Exception("Stripe down")

    response = client.post("/checkout/create-appeal-checkout", json={
        "citation_number": "123456",
        "city_id": "us-ca-san_francisco",
        "user_attestation": True
    })

    assert response.status_code == 500
    assert "Failed to create checkout session" in response.json()["detail"]

def test_get_session_status_success(mock_stripe_service, mock_db_service):
    mock_stripe_service.get_session.return_value = {
        "status": "complete",
        "payment_status": "paid"
    }

    session = MagicMock()
    mock_db_service.get_session.return_value.__enter__.return_value = session

    # Mock payment status query
    session.execute.return_value.fetchone.return_value = ("paid", "TRACK123")

    # Mock payment object query for clerical_id
    mock_payment = MagicMock()
    mock_payment.intake_id = 1

    mock_intake = MagicMock()
    mock_intake.clerical_id = "CL-123"

    query_mock = MagicMock()
    session.query.return_value = query_mock
    filter_mock = MagicMock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.side_effect = [mock_payment, mock_intake]

    response = client.get("/checkout/session-status?session_id=cs_test_123")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["payment_status"] == "paid"
    assert data["mailing_status"] == "fulfilled"
    assert data["tracking_number"] == "TRACK123"
    assert data["clerical_id"] == "CL-123"

def test_get_session_status_not_found(mock_stripe_service):
    mock_stripe_service.get_session.return_value = None

    response = client.get("/checkout/session-status?session_id=invalid")

    assert response.status_code == 404
    # app.py's error handler uses "message" for generic 404, or details if provided.
    # HTTPException(404, detail="Session not found")
    # The handler maps detail to message
    assert "Session not found" in response.json()["message"]
