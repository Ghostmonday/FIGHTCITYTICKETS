import sys
import os

# Add backend to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.middleware.rate_limit import get_rate_limit_for_endpoint, RATE_LIMITS

def test_checkout_rate_limit():
    """Test that checkout endpoints get the 'checkout' rate limit."""
    assert get_rate_limit_for_endpoint("/checkout/create-session") == RATE_LIMITS["checkout"]
    assert get_rate_limit_for_endpoint("/api/checkout/status") == RATE_LIMITS["checkout"]
    # Even if it contains 'api', 'checkout' should take precedence
    assert get_rate_limit_for_endpoint("/api/v1/checkout/finalize") == RATE_LIMITS["checkout"]

def test_webhook_rate_limit():
    """Test that webhook endpoints get the 'webhook' rate limit."""
    assert get_rate_limit_for_endpoint("/webhook/stripe") == RATE_LIMITS["webhook"]
    assert get_rate_limit_for_endpoint("/api/webhook/stripe") == RATE_LIMITS["webhook"]
    # Precedence over admin and api
    assert get_rate_limit_for_endpoint("/admin/webhook/logs") == RATE_LIMITS["webhook"]

def test_admin_rate_limit():
    """Test that admin endpoints get the 'admin' rate limit."""
    assert get_rate_limit_for_endpoint("/admin/dashboard") == RATE_LIMITS["admin"]
    assert get_rate_limit_for_endpoint("/admin/users/list") == RATE_LIMITS["admin"]
    # Admin should take precedence over api
    assert get_rate_limit_for_endpoint("/api/admin/settings") == RATE_LIMITS["admin"]

def test_api_rate_limit():
    """Test that general API endpoints get the 'api' rate limit."""
    assert get_rate_limit_for_endpoint("/api/users") == RATE_LIMITS["api"]
    assert get_rate_limit_for_endpoint("/api/v1/tickets") == RATE_LIMITS["api"]
    # Should not match checkout, webhook, or admin
    assert get_rate_limit_for_endpoint("/api/public/info") == RATE_LIMITS["api"]

def test_default_rate_limit():
    """Test that endpoints not matching specific patterns get the default rate limit."""
    assert get_rate_limit_for_endpoint("/") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/health") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/about") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/login") == RATE_LIMITS["default"]

def test_rate_limit_precedence():
    """
    Test the precedence rules:
    1. checkout
    2. webhook
    3. admin
    4. api
    5. default
    """
    # 1. Checkout beats everything
    assert get_rate_limit_for_endpoint("/checkout/webhook") == RATE_LIMITS["checkout"]
    assert get_rate_limit_for_endpoint("/admin/checkout") == RATE_LIMITS["checkout"]

    # 2. Webhook beats admin and api
    # (assuming checkout is not present)
    assert get_rate_limit_for_endpoint("/admin/webhook") == RATE_LIMITS["webhook"]
    assert get_rate_limit_for_endpoint("/api/webhook") == RATE_LIMITS["webhook"]

    # 3. Admin beats api
    # (assuming checkout and webhook are not present)
    assert get_rate_limit_for_endpoint("/api/admin") == RATE_LIMITS["admin"]

    # 4. Api beats default
    # (assuming checkout, webhook, admin are not present)
    assert get_rate_limit_for_endpoint("/api/something") == RATE_LIMITS["api"]
