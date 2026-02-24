import sys
import os

# Add backend to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.middleware.rate_limit import get_rate_limit_for_endpoint, RATE_LIMITS

def test_checkout_rate_limit():
    """Test that checkout paths receive the correct rate limit."""
    # Direct checkout path
    assert get_rate_limit_for_endpoint("/checkout/create-session") == RATE_LIMITS["checkout"]
    # API checkout path
    assert get_rate_limit_for_endpoint("/api/checkout/status") == RATE_LIMITS["checkout"]

def test_webhook_rate_limit():
    """Test that webhook paths receive the correct rate limit."""
    # Direct webhook path
    assert get_rate_limit_for_endpoint("/webhook/stripe") == RATE_LIMITS["webhook"]
    # API webhook path
    assert get_rate_limit_for_endpoint("/api/webhook/stripe") == RATE_LIMITS["webhook"]

def test_admin_rate_limit():
    """Test that admin paths receive the correct rate limit."""
    # Direct admin path
    assert get_rate_limit_for_endpoint("/admin/users") == RATE_LIMITS["admin"]
    # API admin path
    assert get_rate_limit_for_endpoint("/api/admin/dashboard") == RATE_LIMITS["admin"]

def test_api_rate_limit():
    """Test that general API paths receive the correct rate limit."""
    assert get_rate_limit_for_endpoint("/api/users") == RATE_LIMITS["api"]
    assert get_rate_limit_for_endpoint("/api/v1/something") == RATE_LIMITS["api"]

def test_default_rate_limit():
    """Test that other paths receive the default rate limit."""
    assert get_rate_limit_for_endpoint("/public/info") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/health") == RATE_LIMITS["default"]

def test_precedence():
    """Test precedence rules for overlapping paths."""
    # Checkout beats everything else if logic is: if "/checkout" in endpoint_path
    # Since "/checkout" is checked first, it should take precedence.
    assert get_rate_limit_for_endpoint("/api/checkout") == RATE_LIMITS["checkout"]

    # Webhook vs Admin
    # Webhook is checked second: elif "/webhook" in ...
    # Admin is checked third: elif "/admin" in ...

    # If path contains both webhook and admin, webhook should win if checked earlier.
    # Case: /admin/webhook -> contains /webhook -> webhook limit
    assert get_rate_limit_for_endpoint("/admin/webhook") == RATE_LIMITS["webhook"]

    # Case: /webhook/admin -> contains /webhook -> webhook limit
    assert get_rate_limit_for_endpoint("/webhook/admin") == RATE_LIMITS["webhook"]

    # Admin vs API
    # Admin is checked before API.
    # Case: /api/admin -> contains /admin -> admin limit
    assert get_rate_limit_for_endpoint("/api/admin") == RATE_LIMITS["admin"]
