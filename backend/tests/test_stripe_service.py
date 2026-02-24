import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
import stripe
from src.services.stripe_service import StripeService

@pytest.fixture
def stripe_service():
    """Fixture for StripeService instance."""
    # We mock settings to avoid relying on env vars during initialization
    with patch("src.services.stripe_service.settings") as mock_settings:
        mock_settings.stripe_secret_key = "sk_test_dummy"
        mock_settings.stripe_price_standard = "price_standard_dummy"
        mock_settings.stripe_price_certified = "price_certified_dummy"
        mock_settings.app_url = "http://test.com"

        # also mock create_stripe_circuit so we don't need real circuit breaker logic interfering
        with patch("src.services.stripe_service.create_stripe_circuit") as mock_circuit:
            mock_circuit.return_value = MagicMock()
            service = StripeService()
            yield service

class TestStripeServiceRetry:

    def test_with_retry_success(self, stripe_service):
        """Test _with_retry succeeds on first attempt."""
        mock_func = MagicMock(return_value="success")
        result = stripe_service._with_retry(mock_func, "arg1", key="value")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", key="value")

    @patch("time.sleep")
    def test_with_retry_rate_limit_error(self, mock_sleep, stripe_service):
        """Test _with_retry retries on RateLimitError."""
        error = stripe.error.RateLimitError("Rate limit exceeded", http_status=429)
        mock_func = MagicMock(side_effect=[error, "success"])

        result = stripe_service._with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once() # Should sleep once

    @patch("time.sleep")
    def test_with_retry_api_connection_error(self, mock_sleep, stripe_service):
        """Test _with_retry retries on APIConnectionError."""
        error = stripe.error.APIConnectionError("Connection failed")
        mock_func = MagicMock(side_effect=[error, error, "success"])

        result = stripe_service._with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("time.sleep")
    def test_with_retry_api_error(self, mock_sleep, stripe_service):
        """Test _with_retry retries on APIError."""
        error = stripe.error.APIError("API Error", http_status=500)
        mock_func = MagicMock(side_effect=[error, "success"])

        result = stripe_service._with_retry(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once()

    @patch("time.sleep")
    def test_with_retry_exhausted(self, mock_sleep, stripe_service):
        """Test _with_retry raises exception after max retries."""
        error = stripe.error.APIError("API Error", http_status=500)
        mock_func = MagicMock(side_effect=error)

        # StripeService.RETRY_COUNT is 3
        with pytest.raises(stripe.error.APIError):
            stripe_service._with_retry(mock_func)

        assert mock_func.call_count == stripe_service.RETRY_COUNT
        assert mock_sleep.call_count == stripe_service.RETRY_COUNT - 1

    def test_with_retry_other_exception(self, stripe_service):
        """Test _with_retry raises immediately on non-retryable exception."""
        mock_func = MagicMock(side_effect=ValueError("Invalid value"))

        with pytest.raises(ValueError):
            stripe_service._with_retry(mock_func)

        assert mock_func.call_count == 1


    @pytest.mark.asyncio
    async def test_with_retry_async_success_coroutine(self, stripe_service):
        """Test _with_retry_async succeeds with async function."""
        async def async_func(arg):
            return f"async_{arg}"

        result = await stripe_service._with_retry_async(async_func, "test")
        assert result == "async_test"

    @pytest.mark.asyncio
    async def test_with_retry_async_success_sync_func(self, stripe_service):
        """Test _with_retry_async succeeds with sync function (offloaded)."""
        def sync_func(arg):
            return f"sync_{arg}"

        # Verify it runs in executor
        # We rely on the fact that run_in_executor returns a future that awaits to result
        result = await stripe_service._with_retry_async(sync_func, "test")
        assert result == "sync_test"

    @pytest.mark.asyncio
    @patch("asyncio.sleep")
    async def test_with_retry_async_retry_logic(self, mock_sleep, stripe_service):
        """Test _with_retry_async retries on error."""
        error = stripe.error.RateLimitError("Rate limit", http_status=429)
        mock_func = AsyncMock(side_effect=[error, "success"])

        result = await stripe_service._with_retry_async(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("asyncio.sleep")
    async def test_with_retry_async_exhausted(self, mock_sleep, stripe_service):
        """Test _with_retry_async raises after max retries."""
        error = stripe.error.APIError("API Error", http_status=500)
        mock_func = AsyncMock(side_effect=error)

        with pytest.raises(stripe.error.APIError):
            await stripe_service._with_retry_async(mock_func)

        assert mock_func.call_count == stripe_service.RETRY_COUNT
        assert mock_sleep.await_count == stripe_service.RETRY_COUNT - 1
