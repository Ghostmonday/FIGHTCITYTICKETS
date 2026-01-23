"""
Request ID Middleware for FIGHTCITYTICKETS.com

Generates and tracks unique request IDs for better observability and debugging.
Adds X-Request-ID header to all requests and responses.
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates a unique request ID for each request.

    The request ID is:
    - Generated if not present in X-Request-ID header
    - Stored in request.state for access in handlers
    - Added to response headers as X-Request-ID
    - Used in error handlers for correlation
    """

    async def dispatch(self, request: Request, call_next):
        # Check if request ID is already provided in header
        request_id = request.headers.get("X-Request-ID")

        # Generate new request ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in request state for access in handlers and error handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


def get_request_id(request: Request) -> str:
    """
    Helper function to get request ID from request state.

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string, or "N/A" if not set
    """
    return getattr(request.state, "request_id", "N/A")


