"""
Health check endpoint for monitoring and load balancers.
Includes detailed health checks for all external services.
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..config import settings
from ..middleware.resilience import CircuitBreaker
from ..services.database import get_db_service
from ..services.email_service import get_email_service
from ..services.statement import get_statement_service

router = APIRouter()
logger = logging.getLogger(__name__)


def get_circuit_breaker_status() -> dict:
    """Get status of all circuit breakers."""
    status = {}
    for name, cb in CircuitBreaker.get_all_instances().items():
        status[name] = cb.get_status()
    return status


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
    Detailed health check with database and all external service status.
    Returns degraded states without crashing when third-party services are missing.
    Useful for monitoring and debugging.
    
    Checks:
    - Database connectivity with latency
    - SendGrid API with latency
    - DeepSeek AI API with latency
    - Stripe configuration status
    - Lob configuration status
    - Circuit breaker states
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.app_env,
        "response_time_ms": 0,
        "services": {}
    }
    
    # Check database - critical dependency
    db_start = time.time()
    try:
        db_service = get_db_service()
        db_healthy = db_service.health_check()
        db_latency_ms = int((time.time() - db_start) * 1000)
        
        # Get database circuit breaker status
        db_status = db_service.get_status()
        
        health_status["services"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "type": "PostgreSQL",
            "latency_ms": db_latency_ms,
            "circuit_state": db_status.get("circuit_state", "unknown"),
        }
        if not db_healthy:
            health_status["status"] = "degraded"
    except Exception as e:
        db_latency_ms = int((time.time() - db_start) * 1000)
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "type": "PostgreSQL",
            "latency_ms": db_latency_ms,
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check SendGrid API - non-critical but important
    sendgrid_start = time.time()
    try:
        email_service = get_email_service()
        email_status = email_service.get_status()
        
        health_status["services"]["sendgrid"] = {
            "status": "healthy" if email_status.get("healthy") else "degraded",
            "type": "SendGrid API",
            "latency_ms": int((time.time() - sendgrid_start) * 1000),
            "circuit_state": email_status.get("circuit_state", "unknown"),
            "daily_count": email_status.get("daily_count", 0),
        }
        
        # Optional: actual API ping (commented out to avoid rate limiting)
        # await _ping_sendgrid()
        
    except Exception as e:
        sendgrid_latency_ms = int((time.time() - sendgrid_start) * 1000)
        logger.warning(f"SendGrid health check failed: {e}")
        health_status["services"]["sendgrid"] = {
            "status": "unknown",
            "type": "SendGrid API",
            "latency_ms": sendgrid_latency_ms,
            "error": str(e)
        }
        # Don't mark as degraded for email issues - service can still operate
    
    # Check DeepSeek AI API - non-critical
    deepseek_start = time.time()
    try:
        statement_service = get_statement_service()
        deepseek_cb = statement_service._circuit_breaker
        
        health_status["services"]["deepseek"] = {
            "status": "healthy" if deepseek_cb.metrics.state.value == "closed" else "degraded",
            "type": "DeepSeek AI API",
            "latency_ms": int((time.time() - deepseek_start) * 1000),
            "circuit_state": deepseek_cb.metrics.state.value,
            "total_calls": deepseek_cb.metrics.total_calls,
            "failure_count": deepseek_cb.metrics.failure_count,
        }
        
    except Exception as e:
        deepseek_latency_ms = int((time.time() - deepseek_start) * 1000)
        logger.warning(f"DeepSeek health check failed: {e}")
        health_status["services"]["deepseek"] = {
            "status": "unknown",
            "type": "DeepSeek AI API",
            "latency_ms": deepseek_latency_ms,
            "error": str(e)
        }
        # Don't mark as degraded for AI issues - service can still operate
    
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
    
    # Check AI services - non-critical, graceful degradation
    try:
        deepseek_configured = (
            settings.deepseek_api_key
            and settings.deepseek_api_key != "sk_dummy"
            and settings.deepseek_api_key != "change-me"
        )
        health_status["services"]["ai"] = {
            "deepseek": "configured" if deepseek_configured else "not_configured",
        }
        # AI services not configured is not a failure - service can still operate
    except Exception as e:
        logger.warning(f"AI services health check failed: {e}")
        health_status["services"]["ai"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # Include circuit breaker status for all services
    health_status["circuit_breakers"] = get_circuit_breaker_status()
    
    # Check if any circuit breakers are open
    open_circuits = [
        name for name, status in get_circuit_breaker_status().items()
        if status["state"] == "open"
    ]
    if open_circuits:
        health_status["services"]["resilience"] = {
            "status": "degraded",
            "open_circuits": open_circuits
        }
        health_status["status"] = "degraded"
    
    # Calculate total response time
    health_status["response_time_ms"] = int((time.time() - start_time) * 1000)

    if health_status["status"] == "degraded":
        return JSONResponse(
            status_code=503,
            content=health_status
        )
    
    return health_status


async def _ping_sendgrid() -> bool:
    """Ping SendGrid API to verify connectivity."""
    try:
        email_service = get_email_service()
        if not email_service.api_key:
            return False
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.sendgrid.com/v3/api_keys",
                headers={
                    "Authorization": f"Bearer {email_service.api_key}",
                },
            )
            return response.status_code in (200, 401)  # 401 = valid key but wrong endpoint
    except Exception as e:
        logger.warning(f"SendGrid ping failed: {e}")
        return False


async def _ping_deepseek() -> bool:
    """Ping DeepSeek API to verify connectivity."""
    try:
        statement_service = get_statement_service()
        if not statement_service.api_key:
            return False
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                statement_service.API_URL,
                headers={
                    "Authorization": f"Bearer {statement_service.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                },
            )
            return response.status_code in (200, 400, 401)  # Various valid responses
    except Exception as e:
        logger.warning(f"DeepSeek ping failed: {e}")
        return False
