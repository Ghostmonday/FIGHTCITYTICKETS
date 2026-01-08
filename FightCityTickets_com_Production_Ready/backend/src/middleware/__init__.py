"""
Middleware package for FightSFTickets.com

COORDINATION NOTE: AI Assistant #1 (Auto) created request_id and rate_limit modules.
The other AI should integrate these into app.py when ready.

This package contains middleware components for:
- Request ID tracking ✅ (created, needs integration)
- Rate limiting ✅ (created, needs integration)
- Other cross-cutting concerns
"""

from .request_id import RequestIDMiddleware, get_request_id

# Rate limiting imports - commented out until slowapi is added to requirements.txt
# COORDINATION: Uncomment these after adding slowapi to requirements.txt
# from .rate_limit import (
#     get_rate_limiter,
#     get_rate_limit_for_endpoint,
#     RATE_LIMITS,
#     _rate_limit_exceeded_handler,
#     RateLimitExceeded,
# )

__all__ = [
    "RequestIDMiddleware",
    "get_request_id",
    # Add rate limiting exports after slowapi is installed
]

