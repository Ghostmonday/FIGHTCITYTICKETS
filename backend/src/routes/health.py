"""
Health check endpoint for monitoring and load balancers.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..services.database import get_db_service
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def health():
    """
    Basic liveness check endpoint.
    Returns 200 if service is running (does not check dependencies).
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@router.get("/ready")
async def readiness():
    """
    Readiness check endpoint.
    Returns 200 only if critical dependencies (database) are available.
    Returns 503 if not ready to accept traffic.
    """
    try:
        db_service = get_db_service()
        db_healthy = db_service.health_check()
        
        if db_healthy:
            return {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "reason": "Database unavailable",
                }
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "reason": f"Database check failed: {str(e)}",
            }
        )


@router.get("/detailed")
async def health_detailed():
    """
    Detailed health check with database and service status.
    Returns degraded states without crashing when third-party services are missing.
    Useful for monitoring and debugging.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.app_env,
        "services": {}
    }
    
    # Check database - critical dependency
    try:
        db_service = get_db_service()
        db_healthy = db_service.health_check()
        health_status["services"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "type": "PostgreSQL"
        }
        if not db_healthy:
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Stripe configuration - non-critical, graceful degradation
    try:
        stripe_configured = (
            settings.stripe_secret_key 
            and settings.stripe_secret_key != "sk_live_dummy"
            and settings.stripe_secret_key != "change-me"
            and settings.stripe_secret_key.startswith("sk_")
        )
        health_status["services"]["stripe"] = {
            "status": "configured" if stripe_configured else "not_configured",
            "mode": "test" if settings.stripe_secret_key.startswith("sk_test_") else "live" if stripe_configured else "unknown"
        }
        # Stripe not configured is not a failure - service can still operate
    except Exception as e:
        logger.warning(f"Stripe health check failed: {e}")
        health_status["services"]["stripe"] = {
            "status": "unknown",
            "error": str(e)
        }
        # Don't mark as degraded for Stripe issues
    
    # Check Lob configuration - non-critical, graceful degradation
    try:
        lob_configured = (
            settings.lob_api_key 
            and settings.lob_api_key != "test_dummy"
            and settings.lob_api_key != "change-me"
        )
        health_status["services"]["lob"] = {
            "status": "configured" if lob_configured else "not_configured",
            "mode": settings.lob_mode
        }
        # Lob not configured is not a failure - service can still operate
    except Exception as e:
        logger.warning(f"Lob health check failed: {e}")
        health_status["services"]["lob"] = {
            "status": "unknown",
            "error": str(e)
        }
        # Don't mark as degraded for Lob issues
    
    # Check AI services - non-critical, graceful degradation
    try:
        deepseek_configured = (
            settings.deepseek_api_key
            and settings.deepseek_api_key != "sk_dummy"
            and settings.deepseek_api_key != "change-me"
        )
        openai_configured = (
            settings.openai_api_key
            and settings.openai_api_key != "sk_dummy"
            and settings.openai_api_key != "change-me"
        )
        health_status["services"]["ai"] = {
            "deepseek": "configured" if deepseek_configured else "not_configured",
            "openai": "configured" if openai_configured else "not_configured",
        }
        # AI services not configured is not a failure - service can still operate
    except Exception as e:
        logger.warning(f"AI services health check failed: {e}")
        health_status["services"]["ai"] = {
            "status": "unknown",
            "error": str(e)
        }
        # Don't mark as degraded for AI service issues
    
    # Determine overall status - only degraded if critical dependencies fail
    if health_status["status"] == "degraded":
        return JSONResponse(
            status_code=503,
            content=health_status
        )
    
    return health_status
