"""
Error Handling Middleware for Fight City Tickets.com

Provides structured error responses and error codes for the API.
"""

import logging
import traceback
from enum import Enum
from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from .request_id import get_request_id

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standardized error codes for the API."""

    # Authentication errors
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_EXPIRED_TOKEN = "AUTH_EXPIRED_TOKEN"
    AUTH_MISSING_TOKEN = "AUTH_MISSING_TOKEN"

    # Authorization errors
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"

    # External service errors
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"

    # Payment errors
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_VERIFICATION_FAILED = "PAYMENT_VERIFICATION_FAILED"

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"


class APIError(Exception):
    """Base exception for API errors with structured response."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.suggestion = suggestion
        super().__init__(message)


def create_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int,
    request: Optional[Request] = None,
    details: Optional[dict[str, Any]] = None,
    suggestion: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a structured error response.

    Args:
        error_code: Standardized error code
        message: Human-readable error message
        status_code: HTTP status code
        request: Optional request for request_id
        details: Optional additional details
        suggestion: Optional suggestion for the user

    Returns:
        Structured error response dictionary
    """
    response = {
        "error": error_code.value,
        "message": message,
        "code": error_code.value,
        "status_code": status_code,
    }

    if request:
        response["request_id"] = get_request_id(request)

    if details:
        response["details"] = details

    if suggestion:
        response["suggestion"] = suggestion

    return response


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handle APIError exceptions and return structured responses.

    Args:
        request: The incoming request
        exc: The APIError exception

    Returns:
        JSONResponse with structured error
    """
    logger.warning(
        f"API Error [request_id={get_request_id(request)}]: "
        f"{exc.error_code.value}: {exc.message}"
    )

    response_data = create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        request=request,
        details=exc.details,
        suggestion=exc.suggestion,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unhandled exceptions and return structured responses.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse with error details
    """
    request_id = get_request_id(request)

    logger.error(
        f"Unhandled exception [request_id={request_id}]: {exc}"
    )
    logger.error(traceback.format_exc())

    response_data = create_error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
        status_code=500,
        request=request,
        details={"exception_type": type(exc).__name__},
        suggestion=f"Contact support with request ID: {request_id}",
    )

    return JSONResponse(
        status_code=500,
        content=response_data,
    )


def error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int,
    request: Optional[Request] = None,
    details: Optional[dict[str, Any]] = None,
    suggestion: Optional[str] = None,
) -> dict[str, Any]:
    """
    Helper function to create structured error responses outside exception handlers.

    Args:
        error_code: Standardized error code
        message: Human-readable error message
        status_code: HTTP status code
        request: Optional request for request_id
        details: Optional additional details
        suggestion: Optional suggestion for the user

    Returns:
        Structured error response dictionary
    """
    return create_error_response(
        error_code=error_code,
        message=message,
        status_code=status_code,
        request=request,
        details=details,
        suggestion=suggestion,
    )
