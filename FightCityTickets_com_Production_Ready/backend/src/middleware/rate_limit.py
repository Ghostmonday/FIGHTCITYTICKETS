"""
Rate Limiting Middleware for FightSFTickets.com

IMPORTANT: This file was created by AI Assistant #1 (Auto) working backwards through audit items.
The other AI is currently editing app.py - DO NOT integrate this into app.py until they're done.
See coordination comments below.

This middleware provides rate limiting protection against:
- Brute force attacks
- DDoS attacks
- API abuse
- Cost implications from excessive API calls

AUDIT ITEM: Issue #5 - Missing Rate Limiting (HIGH PRIORITY)
STATUS: Middleware created, NOT YET INTEGRATED into app.py
TODO: Add to requirements.txt: slowapi==0.1.9
TODO: Integrate into app.py after other AI finishes their work
TODO: Apply to sensitive endpoints (checkout, webhooks, admin)
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

    COORDINATION NOTE: This function returns the limiter that needs to be
    integrated into app.py. The other AI should:
    1. Import this: from ..middleware.rate_limit import get_rate_limiter
    2. Add to app: app.state.limiter = get_rate_limiter()
    3. Add exception handler: app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    4. Apply decorators to routes: @limiter.limit("10/minute")

    Returns:
        Limiter instance configured for the application
    """
    return limiter


# Rate limit configurations for different endpoint types
# COORDINATION: These are suggested limits - adjust based on your needs
RATE_LIMITS = {
    "checkout": "10/minute",  # Payment endpoints - prevent abuse
    "webhook": "100/minute",  # Webhooks - higher limit for Stripe
    "admin": "30/minute",     # Admin endpoints - moderate limit
    "api": "60/minute",       # General API endpoints
    "default": "100/minute",  # Default for other endpoints
}


def get_rate_limit_for_endpoint(endpoint_path: str) -> str:
    """
    Get appropriate rate limit for an endpoint based on its path.

    COORDINATION: This helps apply appropriate limits to different routes.
    The other AI can use this when applying rate limits to routes.

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


# Export the exception handler for app.py integration
__all__ = [
    "limiter",
    "get_rate_limiter",
    "get_rate_limit_for_endpoint",
    "RATE_LIMITS",
    "_rate_limit_exceeded_handler",
    "RateLimitExceeded",
]


