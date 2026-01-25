"""
Middleware package for Fight City Tickets.com

Provides cross-cutting concerns for the API:
|- Request ID tracking
|- Rate limiting
|- Error handling
"""

from .errors import (
    APIError,
    ErrorCode,
    api_error_handler,
    create_error_response,
    error_response,
    unhandled_exception_handler,
)
from .rate_limit import (
    RATE_LIMITS,
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
    get_rate_limit_for_endpoint,
    get_rate_limiter,
)
from .request_id import RequestIDMiddleware, get_request_id

__all__ = [
    "RequestIDMiddleware",
    "get_request_id",
    "get_rate_limiter",
    "get_rate_limit_for_endpoint",
    "RATE_LIMITS",
    "_rate_limit_exceeded_handler",
    "RateLimitExceeded",
    "APIError",
    "ErrorCode",
    "api_error_handler",
    "unhandled_exception_handler",
    "create_error_response",
    "error_response",
]
