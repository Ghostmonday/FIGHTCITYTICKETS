import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.middleware.rate_limit import get_rate_limit_for_endpoint, RATE_LIMITS

def test_checkout_rate_limit():
    """Test rate limits for checkout endpoints."""
    assert get_rate_limit_for_endpoint("/checkout/create-session") == RATE_LIMITS["checkout"]
    assert get_rate_limit_for_endpoint("/api/checkout/status") == RATE_LIMITS["checkout"]

def test_webhook_rate_limit():
    """Test rate limits for webhook endpoints."""
    assert get_rate_limit_for_endpoint("/webhook/stripe") == RATE_LIMITS["webhook"]
    assert get_rate_limit_for_endpoint("/api/webhook/stripe") == RATE_LIMITS["webhook"]

def test_admin_rate_limit():
    """Test rate limits for admin endpoints."""
    assert get_rate_limit_for_endpoint("/admin/users") == RATE_LIMITS["admin"]
    assert get_rate_limit_for_endpoint("/api/admin/dashboard") == RATE_LIMITS["admin"]

def test_api_rate_limit():
    """Test rate limits for general API endpoints."""
    assert get_rate_limit_for_endpoint("/api/users") == RATE_LIMITS["api"]
    assert get_rate_limit_for_endpoint("/api/v1/something") == RATE_LIMITS["api"]

def test_default_rate_limit():
    """Test rate limits for other endpoints."""
    assert get_rate_limit_for_endpoint("/public/info") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/") == RATE_LIMITS["default"]
    assert get_rate_limit_for_endpoint("/health") == RATE_LIMITS["default"]

def test_precedence():
    """Test precedence rules for rate limits."""
    # Checkout beats everything else
    assert get_rate_limit_for_endpoint("/api/checkout") == RATE_LIMITS["checkout"]

    # Webhook beats Admin (if path contains both)
    # Based on implementation: elif "/webhook" ... then elif "/admin"
    assert get_rate_limit_for_endpoint("/admin/webhook") == RATE_LIMITS["webhook"]

    # Webhook beats API (if path contains both)
    assert get_rate_limit_for_endpoint("/api/webhook") == RATE_LIMITS["webhook"]

    # Admin beats API
    assert get_rate_limit_for_endpoint("/api/admin") == RATE_LIMITS["admin"]
