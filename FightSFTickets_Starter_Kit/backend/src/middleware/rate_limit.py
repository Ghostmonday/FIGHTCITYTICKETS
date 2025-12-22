"""
Rate Limiting Middleware for FastAPI

Protects API endpoints from abuse and DoS attacks.
"""

import logging
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    "default": "100/minute",  # General API endpoints
    "auth": "5/minute",  # Authentication endpoints
    "payment": "10/minute",  # Payment-related endpoints
    "webhook": "60/minute",  # Webhook endpoints (Stripe sends many)
    "health": "30/minute",  # Health check endpoints
}


def get_rate_limit(route_name: str = "default") -> str:
    """
    Get rate limit string for a route.

    Args:
        route_name: Name of the route category

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    return RATE_LIMITS.get(route_name, RATE_LIMITS["default"])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)} "
        f"on {request.url.path}"
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": exc.retry_after,
        },
        headers={"Retry-After": str(exc.retry_after) if exc.retry_after else "60"},
    )


# Register the custom handler
limiter._rate_limit_exceeded_handler = rate_limit_exceeded_handler

