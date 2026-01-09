"""
Rate Limiting Middleware for FightSFTickets.com

Provides rate limiting protection against:
- Brute force attacks
- DDoS attacks
- API abuse
- Cost implications from excessive API calls
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Initialize rate limiter
# Uses client IP address as the key for rate limiting
limiter = Limiter(key_func=get_remote_address)


def get_rate_limiter() -> Limiter:
    """
    Get the rate limiter instance.

    Returns:
        Limiter instance configured for the application
    """
    return limiter


# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    "checkout": "10/minute",  # Payment endpoints - prevent abuse
    "webhook": "100/minute",  # Webhooks - higher limit for Stripe
    "admin": "30/minute",  # Admin endpoints - moderate limit
    "api": "60/minute",  # General API endpoints
    "default": "100/minute",  # Default for other endpoints
}


def get_rate_limit_for_endpoint(endpoint_path: str) -> str:
    """
    Get appropriate rate limit for an endpoint based on its path.

    Args:
        endpoint_path: The path of the endpoint (e.g., "/checkout/create-session")

    Returns:
        Rate limit string (e.g., "10/minute")
    """
    if "/checkout" in endpoint_path:
        return RATE_LIMITS["checkout"]
    elif "/webhook" in endpoint_path or "/api/webhook" in endpoint_path:
        return RATE_LIMITS["webhook"]
    elif "/admin" in endpoint_path:
        return RATE_LIMITS["admin"]
    elif "/api" in endpoint_path:
        return RATE_LIMITS["api"]
    else:
        return RATE_LIMITS["default"]


__all__ = [
    "limiter",
    "get_rate_limiter",
    "get_rate_limit_for_endpoint",
    "RATE_LIMITS",
    "_rate_limit_exceeded_handler",
    "RateLimitExceeded",
]
