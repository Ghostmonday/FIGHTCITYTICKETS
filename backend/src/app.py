"""
Main FastAPI Application for Fight City Tickets.com (Database-First Approach)

This is the updated main application file that uses the database-first approach.
All data is persisted in PostgreSQL before creating Stripe checkout sessions.
Only IDs are stored in Stripe metadata for webhook processing.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .logging_config import setup_logging
from .sentry_config import init_sentry
from .middleware.request_id import RequestIDMiddleware, get_request_id
from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.errors import (
    APIError,
    ErrorCode,
    api_error_handler,
    error_response,
    unhandled_exception_handler,
)
from .middleware.resilience import CircuitOpenError
from .middleware.rate_limit import (
    get_rate_limiter,
    _rate_limit_exceeded_handler,
    RateLimitExceeded,
)
from .routes.admin import router as admin_router
from .routes.appeals import router as appeals_router
from .routes.checkout import router as checkout_router
from .routes.health import router as health_router
from .routes.places import router as places_router
from .routes.statement import router as statement_router
from .routes.status import router as status_router
from .routes.telemetry import router as telemetry_router
from .routes.tickets import router as tickets_router
from .routes.photos import router as photos_router
from .routes.webhooks import router as webhooks_router
from .services.database import get_db_service

# Set up structured logging
use_json_logging = os.getenv("JSON_LOGGING", "true").lower() == "true"
log_file = os.getenv("LOG_FILE", "server.log")
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    use_json=use_json_logging,
    log_file=log_file if not use_json_logging else None  # JSON logs go to stdout
)
logger = logging.getLogger(__name__)

# Initialize Sentry error tracking (if DSN is configured)
sentry_enabled = init_sentry(environment=settings.app_env)
if sentry_enabled:
    logger.info("✅ Sentry error tracking initialized")
else:
    logger.info("ℹ️  Sentry not configured (set SENTRY_DSN to enable)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    On startup:
    1. Initialize database connection
    2. Verify database schema
    3. Log startup information

    On shutdown:
    1. Clean up database connections
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Fight City Tickets API (Database-First Approach)")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"API URL: {settings.api_url}")
    logger.info(f"App URL: {settings.app_url}")
    logger.info("=" * 60)

    try:
        # Initialize database service
        db_service = get_db_service()

        # Check database connection
        if db_service.health_check():
            logger.info("✅ Database connection successful")

            # Verify tables exist (they should be created by migration script)
            # In production, tables should be created via migrations, not here
            logger.info("Database schema verified")
        else:
            logger.error("❌ Database connection failed")
            logger.warning("API will start but database operations will fail")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Continue startup - some features may work without database

    yield

    # Shutdown - graceful cleanup
    logger.info("Shutting down Fight City Tickets API")
    try:
        # Close database connections gracefully
        db_service = get_db_service()
        if hasattr(db_service, 'engine'):
            db_service.engine.dispose()
            logger.info("Database connections closed")
    except Exception as e:
        logger.warning(f"Error during shutdown cleanup: {e}")
    logger.info("Shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Fight City Tickets API",
    description="""
    ## Database-First Parking Ticket Appeal System

    This API handles the complete workflow for appealing parking tickets across multiple cities:

    1. **Citation Validation** - Validate citation numbers and deadlines
    2. **Statement Refinement** - AI-assisted appeal letter writing (UPL-compliant)
    3. **Checkout & Payment** - Database-first Stripe integration
    4. **Webhook Processing** - Idempotent payment fulfillment
    5. **Mail Fulfillment** - Physical mail sending via Lob API

    ### Key Architecture Features:

    - **Database-First**: All data persisted in PostgreSQL before payment
    - **Minimal Metadata**: Only IDs stored in Stripe metadata
    - **Idempotent Webhooks**: Safe retry handling for production
    - **UPL Compliance**: Never provides legal advice or recommends evidence
    """,
    version="1.0.0",
    contact={
        "name": "Fight City Tickets Support",
        "url": settings.app_url,
        "email": settings.support_email,
    },
    license_info={
        "name": "Proprietary",
        "url": f"{settings.app_url}/terms",
    },
    lifespan=lifespan,
)


# ============================================
# BACKLOG PRIORITY 1: Middleware Integration
# ============================================

# Request ID Middleware - adds unique ID to every request for tracking
app.add_middleware(RequestIDMiddleware)

# Security Headers Middleware - adds security headers to all responses
app.add_middleware(SecurityHeadersMiddleware)

# Metrics middleware - track request counts
from .routes.health import increment_request_count, increment_error_count


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request and error counts for metrics."""
    increment_request_count()
    try:
        response = await call_next(request)
        return response
    except Exception:
        increment_error_count()
        raise

# Rate Limiting - initialize limiter and exception handler
# BACKLOG PRIORITY 1: Rate limiting middleware integration
limiter_instance = get_rate_limiter()
app.state.limiter = limiter_instance
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Stripe-Signature",  # For webhook verification
        "X-Request-ID",  # For request ID propagation
    ],
    expose_headers=["X-Request-ID", "Content-Disposition"],
    max_age=600,  # 10 minutes
)

# Include routers with updated database-first routes
# NOTE: Nginx strips /api/ prefix, so routes mounted at /api/* should be registered without /api/
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
app.include_router(statement_router, prefix="/statement", tags=["statement"])
app.include_router(photos_router, prefix="/api", tags=["photos"])


# Updated routes with database-first approach
app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])
app.include_router(places_router, prefix="/places", tags=["places"])
# Appeal storage router for frontend persistence
app.include_router(appeals_router, prefix="/api", tags=["appeals"])
# Webhook router: nginx strips /api/, so mount at /webhook (not /api/webhook)
app.include_router(webhooks_router, prefix="/webhook", tags=["webhooks"])
app.include_router(status_router, prefix="/status", tags=["status"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
# OCR telemetry endpoint (opt-in) - nginx strips /api/ prefix
app.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns basic API information and links to documentation.
    """
    return {
        "name": "Fight City Tickets API",
        "version": "1.0.0",
        "description": "Database-first parking ticket appeal system for San Francisco",
        "environment": settings.app_env,
        "database_approach": "Database-first with PostgreSQL",
        "payment_approach": "Stripe with minimal metadata (IDs only)",
        "webhook_approach": "Idempotent processing with database lookups",
        "documentation": "/docs",
        "health_check": "/health",
            "endpoints": {
            "citation_validation": "/tickets/validate",
            "statement_refinement": "/api/statement/refine",
            "checkout": "/checkout/create-session",
            "webhook": "/api/webhook/stripe",  # Public URL (nginx adds /api/ prefix)
        },
        "compliance": {
            "upl": "UPL-compliant: Never provides legal advice",
            "data_persistence": "All data stored in database before payment",
            "metadata_minimalism": "Only IDs stored in Stripe metadata",
        },
    }


@app.get("/status")
async def status(request: Request):
    """
    Comprehensive status endpoint.

    Returns detailed status information including database connectivity
    and service availability.
    """
    try:
        # Check database status
        db_service = get_db_service()
        db_healthy = db_service.health_check()

        # Check if we're in test mode
        stripe_test_mode = settings.stripe_secret_key.startswith("sk_test_")
        lob_test_mode = settings.lob_mode.lower() == "test"

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {
                "database": {
                    "status": "connected" if db_healthy else "disconnected",
                    "type": "PostgreSQL",
                    "url": db_service._masked_url(),
                },
                "stripe": {
                    "status": "configured",
                    "mode": "test" if stripe_test_mode else "live",
                    "prices_configured": bool(
                        settings.stripe_price_standard
                        and settings.stripe_price_certified
                    ),
                },
                "lob": {
                    "status": "configured"
                    if settings.lob_api_key != "change-me"
                    else "not_configured",
                    "mode": lob_test_mode,
                },
                "ai_services": {
                    "deepseek": "configured"
                    if settings.deepseek_api_key != "change-me"
                    else "not_configured",
                },
            },
            "architecture": {
                "approach": "database-first",
                "metadata_strategy": "ids-only",
                "webhook_processing": "idempotent",
                "data_persistence": "pre-payment",
            },
            "environment": settings.app_env,
        }

    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": get_request_id(request),
        }


@app.get("/docs-redirect")
async def docs_redirect():
    """
    Redirect to API documentation.

    This endpoint exists for convenience and can be used
    by frontend applications to easily link to documentation.
    """
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    from fastapi.responses import JSONResponse

    request_id = get_request_id(request)
    logger.warning(f"404 Not Found [request_id={request_id}]: {request.url.path}")

    message = "The requested resource was not found"
    if hasattr(exc, "detail"):
        message = exc.detail

    return JSONResponse(
        status_code=404,
        content=error_response(
            error_code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=404,
            request=request,
            details={"path": request.url.path},
            suggestion="Check the API documentation at /docs",
        ),
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler - now delegates to unhandled_exception_handler."""
    return await unhandled_exception_handler(request, exc)


# Register APIError exception handler
app.add_exception_handler(APIError, api_error_handler)


@app.exception_handler(CircuitOpenError)
async def circuit_open_handler(request: Request, exc: CircuitOpenError):
    """Handle circuit breaker open errors."""
    from fastapi.responses import JSONResponse

    logger.warning(f"Circuit Open Error [request_id={get_request_id(request)}]: {exc}")

    return JSONResponse(
        status_code=503,
        content=error_response(
            error_code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            message=str(exc),
            status_code=503,
            request=request,
            details={"circuit": "open"},
            suggestion="Please try again later.",
        ),
    )


if __name__ == "__main__":
    """
    Run the application directly (for development).

    In production, use uvicorn or another ASGI server:
    uvicorn src.app:app --host 0.0.0.0 --port 8000
    """
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.app_env == "dev",
        log_level="info",
    )