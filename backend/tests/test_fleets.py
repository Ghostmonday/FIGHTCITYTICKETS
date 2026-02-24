import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app
from src.models import Fleet

# Mock dependencies
@pytest.fixture
def mock_db_service():
    with patch("src.routes.fleets.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock

        session_mock = MagicMock()
        service_mock.get_session.return_value.__enter__.return_value = session_mock

        yield service_mock

@pytest.fixture
def mock_stripe_service():
    with patch("src.routes.fleets.StripeService") as mock_cls:
        service_mock = AsyncMock()
        mock_cls.return_value = service_mock

        # Setup sync method mocks on the instance
        service_mock.verify_connect_webhook_signature = MagicMock()

        yield service_mock

client = TestClient(app)

def test_create_fleet_new(mock_db_service, mock_stripe_service):
    """Test creating a new fleet."""
    # Setup mocks
    session_mock = mock_db_service.get_session.return_value.__enter__.return_value
    session_mock.query.return_value.filter.return_value.first.return_value = None

    # Mock refresh to populate ID
    def side_effect_refresh(obj):
        obj.id = 1
    session_mock.refresh.side_effect = side_effect_refresh

    mock_stripe_service.create_connected_account.return_value = {"id": "acct_123"}
    mock_stripe_service.create_account_link.return_value = {"url": "http://stripe.com/onboard"}

    response = client.post("/fleets", json={"name": "Test Fleet", "email": "fleet@test.com"})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Fleet"
    assert data["stripe_account_id"] == "acct_123"
    assert data["onboarding_url"] == "http://stripe.com/onboard"

    # Verify DB calls
    session_mock.add.assert_called_once()
    session_mock.commit.assert_called_once()

def test_create_fleet_existing(mock_db_service, mock_stripe_service):
    """Test creating a fleet that already exists."""
    # Setup mocks
    session_mock = mock_db_service.get_session.return_value.__enter__.return_value
    existing_fleet = Fleet(
        id=1,
        name="Existing Fleet",
        email="fleet@test.com",
        stripe_account_id="acct_old",
        stripe_account_status="pending"
    )
    session_mock.query.return_value.filter.return_value.first.return_value = existing_fleet

    mock_stripe_service.create_account_link.return_value = {"url": "http://stripe.com/resume"}

    response = client.post("/fleets", json={"name": "New Name", "email": "fleet@test.com"})

    assert response.status_code == 200
    data = response.json()
    assert data["stripe_account_id"] == "acct_old"
    # Ensure no new account creation
    mock_stripe_service.create_connected_account.assert_not_called()

def test_get_onboarding_link(mock_db_service, mock_stripe_service):
    """Test getting onboarding link."""
    session_mock = mock_db_service.get_session.return_value.__enter__.return_value
    fleet = Fleet(id=1, name="Fleet", email="f@t.com", stripe_account_id="acct_123", stripe_account_status="pending")
    session_mock.query.return_value.filter.return_value.first.return_value = fleet

    mock_stripe_service.get_account.return_value = {"details_submitted": False}
    mock_stripe_service.create_account_link.return_value = {"url": "http://link"}

    response = client.get("/fleets/1/onboarding")

    assert response.status_code == 200
    assert response.json()["onboarding_url"] == "http://link"

def test_get_onboarding_link_active(mock_db_service, mock_stripe_service):
    """Test getting onboarding link for active account."""
    session_mock = mock_db_service.get_session.return_value.__enter__.return_value
    fleet = Fleet(id=1, name="Fleet", email="f@t.com", stripe_account_id="acct_123", stripe_account_status="pending")
    session_mock.query.return_value.filter.return_value.first.return_value = fleet

    mock_stripe_service.get_account.return_value = {"details_submitted": True}
    # Mock create_account_link to fail or succeed (Express accounts can have links generated even if active, but let's test logic)
    mock_stripe_service.create_account_link.return_value = {"url": "http://login"}

    response = client.get("/fleets/1/onboarding")

    assert response.status_code == 200
    assert fleet.stripe_account_status == "active"
    assert response.json()["onboarding_url"] == "http://login"

def test_webhook_connect(mock_db_service, mock_stripe_service):
    """Test Connect webhook processing."""
    session_mock = mock_db_service.get_session.return_value.__enter__.return_value
    fleet = Fleet(id=1, stripe_account_id="acct_123", stripe_account_status="pending")
    session_mock.query.return_value.filter.return_value.first.return_value = fleet

    # Mock signature verification
    mock_stripe_service.verify_connect_webhook_signature.return_value = True

    payload = {
        "type": "account.updated",
        "data": {
            "object": {
                "id": "acct_123",
                "details_submitted": True
            }
        }
    }

    response = client.post("/fleets/webhook", json=payload, headers={"stripe-signature": "valid"})

    assert response.status_code == 200
    assert fleet.stripe_account_status == "active"
    session_mock.commit.assert_called_once()
