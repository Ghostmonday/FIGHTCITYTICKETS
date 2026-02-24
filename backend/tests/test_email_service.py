import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.email_service import EmailService
from src.middleware.resilience import CircuitBreaker, CircuitState

@pytest.fixture(autouse=True)
def reset_circuit_breakers():
    """Reset circuit breakers before and after each test."""
    CircuitBreaker._instances.clear()
    yield
    CircuitBreaker._instances.clear()

@pytest.fixture
def mock_settings():
    """Mock settings for EmailService."""
    with patch("src.services.email_service.settings") as mock:
        mock.sendgrid_api_key = "test-api-key"
        mock.service_email = "service@example.com"
        mock.support_email = "support@example.com"
        yield mock

@pytest.fixture
def email_service(mock_settings):
    """Create a fresh EmailService instance."""
    return EmailService()

@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient context manager."""
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None
        yield mock_client

@pytest.mark.asyncio
async def test_init_logging_mode(mock_settings):
    """Test initialization in logging mode (no API key)."""
    mock_settings.sendgrid_api_key = "change-me"
    service = EmailService()
    assert service.is_available is False
    assert service._circuit_breaker.name == "email"

@pytest.mark.asyncio
async def test_init_production_mode(mock_settings):
    """Test initialization in production mode (valid API key)."""
    mock_settings.sendgrid_api_key = "valid-key"
    service = EmailService()
    assert service.is_available is True

@pytest.mark.asyncio
async def test_render_template(email_service):
    """Test template rendering with variable substitution."""
    subject, body = await email_service._render_template(
        "payment_confirmation",
        citation_number="CIT-123",
        amount="$50.00",
        appeal_type="standard",
        clerical_id="CLER-456"
    )

    assert "CIT-123" in subject
    assert "CIT-123" in body
    assert "$50.00" in body
    assert "standard" in body
    assert "CLER-456" in body
    assert "support@example.com" in body  # Default support email

@pytest.mark.asyncio
async def test_render_template_defaults(email_service):
    """Test template rendering uses default values."""
    # Override support email in kwargs
    subject, body = await email_service._render_template(
        "payment_confirmation",
        citation_number="CIT-123",
        amount="$50.00",
        appeal_type="standard",
        clerical_id="CLER-456",
        support_email="custom@example.com"
    )

    assert "custom@example.com" in body

@pytest.mark.asyncio
async def test_send_payment_confirmation_logging(mock_settings):
    """Test sending payment confirmation in logging mode."""
    mock_settings.sendgrid_api_key = "change-me"
    service = EmailService()

    result = await service.send_payment_confirmation(
        email="user@example.com",
        citation_number="CIT-123",
        amount_paid=5000,
        appeal_type="standard"
    )

    assert result is True

@pytest.mark.asyncio
async def test_send_payment_confirmation_sendgrid(email_service, mock_httpx_client):
    """Test sending payment confirmation via SendGrid."""
    # Setup successful response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = await email_service.send_payment_confirmation(
        email="user@example.com",
        citation_number="CIT-123",
        amount_paid=5000,
        appeal_type="standard"
    )

    assert result is True
    mock_httpx_client.post.assert_called_once()

    # Verify payload structure
    call_args = mock_httpx_client.post.call_args
    assert call_args[0][0] == "https://api.sendgrid.com/v3/mail/send"
    payload = call_args[1]["json"]
    assert payload["personalizations"][0]["to"][0]["email"] == "user@example.com"
    assert payload["from"]["email"] == "service@example.com"

@pytest.mark.asyncio
async def test_send_appeal_mailed(email_service, mock_httpx_client):
    """Test sending appeal mailed notification."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = await email_service.send_appeal_mailed(
        email="user@example.com",
        citation_number="CIT-123",
        tracking_number="TRACK-789"
    )

    assert result is True
    mock_httpx_client.post.assert_called_once()
    payload = mock_httpx_client.post.call_args[1]["json"]
    assert "TRACK-789" in payload["content"][0]["value"]

@pytest.mark.asyncio
async def test_send_appeal_rejected(email_service, mock_httpx_client):
    """Test sending appeal rejected notification."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = await email_service.send_appeal_rejected(
        email="user@example.com",
        citation_number="CIT-123",
        reason="Invalid evidence"
    )

    assert result is True
    mock_httpx_client.post.assert_called_once()
    payload = mock_httpx_client.post.call_args[1]["json"]
    assert "Invalid evidence" in payload["content"][0]["value"]

@pytest.mark.asyncio
async def test_sendgrid_api_error(email_service, mock_httpx_client):
    """Test handling of SendGrid API errors."""
    # Simulate API error
    mock_httpx_client.post.side_effect = Exception("API Error")

    # Should log error and return True (fallback to logging mode behavior)
    # The public method returns True because logic is:
    # if self.is_available:
    #    success = await self._send_via_sendgrid(...)
    #    if success: return True
    #    logger.warning(...)
    # return True

    result = await email_service.send_payment_confirmation(
        email="user@example.com",
        citation_number="CIT-123",
        amount_paid=5000,
        appeal_type="standard"
    )

    assert result is True
    # Ensure daily count was not incremented (or reset/handled, but implementation increments only on success)
    assert email_service._daily_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_open(email_service, mock_httpx_client):
    """Test behavior when circuit breaker is open."""
    import time
    # Force circuit open and set recent failure time to prevent reset attempt
    email_service._circuit_breaker.metrics.state = CircuitState.OPEN
    email_service._circuit_breaker.metrics.last_failure_time = time.time()

    result = await email_service.send_payment_confirmation(
        email="user@example.com",
        citation_number="CIT-123",
        amount_paid=5000,
        appeal_type="standard"
    )

    # Should skip SendGrid call and return True
    assert result is True
    mock_httpx_client.post.assert_not_called()

@pytest.mark.asyncio
async def test_rate_limiting(email_service, mock_httpx_client):
    """Test daily count incrementing."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    assert email_service._daily_count == 0

    await email_service.send_payment_confirmation(
        email="user@example.com",
        citation_number="CIT-123",
        amount_paid=5000,
        appeal_type="standard"
    )

    assert email_service._daily_count == 1
