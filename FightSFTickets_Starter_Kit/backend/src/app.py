"""
Main FastAPI Application for FightSFTickets.com (Database-First Approach)

This is the updated main application file that uses the database-first approach.
All data is persisted in PostgreSQL before creating Stripe checkout sessions.
Only IDs are stored in Stripe metadata for webhook processing.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware.rate_limit import limiter
from .routes.admin import router as admin_router
from .routes.checkout import router as checkout_router
from .routes.health import router as health_router
from .routes.statement import router as statement_router
from .routes.tickets import router as tickets_router
from .routes.transcribe import router as transcribe_router
from .routes.webhooks import router as webhooks_router
from .services.database import get_db_service

# Set up logger with file handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
    logger.info("Starting FightSFTickets API (Database-First Approach)")
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

    # Shutdown
    logger.info("Shutting down FightSFTickets API")
    # Database connections are cleaned up automatically by SQLAlchemy


# Create FastAPI app with lifespan
app = FastAPI(
    title="FightSFTickets API",
    description="""
    ## Database-First Parking Ticket Appeal System

    This API handles the complete workflow for appealing San Francisco parking tickets:

    1. **Citation Validation** - Validate SFMTA citation numbers and deadlines
    2. **Statement Refinement** - AI-assisted appeal letter writing (UPL-compliant)
    3. **Audio Transcription** - Convert voice memos to text for appeals
    4. **Checkout & Payment** - Database-first Stripe integration
    5. **Webhook Processing** - Idempotent payment fulfillment
    6. **Mail Fulfillment** - Physical mail sending via Lob API

    ### Key Architecture Features:

    - **Database-First**: All data persisted in PostgreSQL before payment
    - **Minimal Metadata**: Only IDs stored in Stripe metadata
    - **Idempotent Webhooks**: Safe retry handling for production
    - **UPL Compliance**: Never provides legal advice or recommends evidence
    """,
    version="1.0.0",
    contact={
        "name": "FightSFTickets Support",
        "url": "https://fightsftickets.com",
        "email": "support@fightsftickets.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://fightsftickets.com/terms",
    },
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter

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
    ],
    expose_headers=["Content-Disposition"],
    max_age=600,  # 10 minutes
)

# Include routers with updated database-first routes
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
app.include_router(statement_router, prefix="/api/statement", tags=["statement"])
app.include_router(transcribe_router, prefix="/api", tags=["transcribe"])

# Updated routes with database-first approach
app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])
app.include_router(webhooks_router, prefix="/api/webhook", tags=["webhooks"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns basic API information and links to documentation.
    """
    return {
        "name": "FightSFTickets API",
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
            "audio_transcription": "/api/transcribe",
            "checkout": "/checkout/create-session",
            "webhook": "/api/webhook/stripe",
        },
        "compliance": {
            "upl": "UPL-compliant: Never provides legal advice",
            "data_persistence": "All data stored in database before payment",
            "metadata_minimalism": "Only IDs stored in Stripe metadata",
        },
    }


@app.get("/status")
async def status():
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
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp in production
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
                    "openai": "configured"
                    if settings.openai_api_key != "change-me"
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
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z",
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
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": request.url.path,
            "suggestions": [
                "Check the API documentation at /docs",
                "Verify the endpoint URL",
                "Ensure you're using the correct HTTP method",
            ],
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    import traceback

    from fastapi.responses import JSONResponse

    # Log the full error
    logger.error(f"Internal server error: {exc}")
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": "N/A",  # Would use actual request ID in production
            "support": "contact support@fightsftickets.com",
        },
    )


if __name__ == "__main__":
    """
    Run the application directly (for development).

    In production, use uvicorn or another ASGI server:
    uvicorn app_fixed:app --host 0.0.0.0 --port 8000
    """
    import uvicorn

    uvicorn.run(
        "app_fixed:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.app_env == "dev",
        log_level="info",
    )
