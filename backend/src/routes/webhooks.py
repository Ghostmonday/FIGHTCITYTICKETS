"""
Stripe Webhook Handler for Fight City Tickets.com

Handles Stripe webhook events for payment confirmation and appeal fulfillment.
Uses database for persistent storage and implements idempotent processing.
Includes in-memory idempotency cache to prevent duplicate processing.
"""

import logging
import os
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..models import AppealType, PaymentStatus, WebhookEvent
from ..services.database import get_db_service
from ..services.email_service import get_email_service
from ..services.mail import AppealLetterRequest, get_mail_service
from ..services.stripe_service import StripeService

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Admin authentication
ADMIN_SECRET_HEADER = "X-Admin-Secret"

# Webhook idempotency cache
# Format: {event_id: {processed: bool, timestamp: float, result: dict}}
_WEBHOOK_CACHE: dict[str, dict] = {}
_WEBHOOK_CACHE_TTL = 86400  # 24 hours
_WEBHOOK_CACHE_MAX_SIZE = 10000  # Max events to cache


def _generate_event_id(event_type: str, object_id: str) -> str:
    """Generate a unique event ID for idempotency tracking."""
    return f"{event_type}:{object_id}"


def _is_event_processed(event_id: str) -> tuple[bool, Optional[dict]]:
    """
    Check if an event has already been processed (database-backed).
    
    Returns:
        (is_processed, cached_result)
    """
    try:
        db_service = get_db_service()
        db = db_service.db
        
        # Check database for processed event
        event = db.query(WebhookEvent).filter(
            WebhookEvent.stripe_event_id == event_id,
            WebhookEvent.processed == True
        ).first()
        
        if event:
            return True, {"message": event.result_message}
        
        return False, None
    except Exception as e:
        logger.warning("Database idempotency check failed: %s, falling back to memory", e)
        # Fall back to memory cache on database errors
        return _is_event_processed_memory(event_id)


def _mark_event_processed(event_id: str, event_type: str, result: dict) -> None:
    """Mark an event as processed in the database."""
    try:
        db_service = get_db_service()
        db = db_service.db
        
        # Check if already exists
        existing = db.query(WebhookEvent).filter(
            WebhookEvent.stripe_event_id == event_id
        ).first()
        
        if existing:
            # Update existing record
            existing.processed = True
            existing.result_message = result.get("message", "")[:500]
            existing.updated_at = datetime.now(timezone.utc)
        else:
            # Create new record
            webhook_event = WebhookEvent(
                stripe_event_id=event_id,
                event_type=event_type,
                processed=True,
                result_message=result.get("message", "")[:500],
            )
            db.add(webhook_event)
        
        db.commit()
    except Exception as e:
        logger.warning("Failed to mark event processed in database: %s", e)
        # Fall back to memory cache
        _mark_event_processed_memory(event_id, result)


# Legacy in-memory functions (fallback)
def _is_event_processed_memory(event_id: str) -> tuple[bool, Optional[dict]]:
    """
    Check if an event has already been processed (in-memory fallback).
    """
    now = time.time()
    
    # Check if event exists and is not expired
    if event_id in _WEBHOOK_CACHE:
        cached = _WEBHOOK_CACHE[event_id]
        if now - cached.get("timestamp", 0) < _WEBHOOK_CACHE_TTL:
            return True, cached.get("result")
        else:
            # Remove expired entry
            del _WEBHOOK_CACHE[event_id]
    
    return False, None


def _mark_event_processed_memory(event_id: str, result: dict) -> None:
    """Mark an event as processed in memory (fallback)."""
    # Proactively clean up expired entries if cache is getting large
    if len(_WEBHOOK_CACHE) >= _WEBHOOK_CACHE_MAX_SIZE * 0.8:
        _cleanup_expired_entries()
    
    # Clean up old entries if cache is still too large after cleanup
    if len(_WEBHOOK_CACHE) >= _WEBHOOK_CACHE_MAX_SIZE:
        sorted_items = sorted(_WEBHOOK_CACHE.items(), key=lambda x: x[1].get("timestamp", 0))
        for old_event_id in list(sorted_items)[:_WEBHOOK_CACHE_MAX_SIZE // 5]:
            if isinstance(old_event_id, tuple):
                _WEBHOOK_CACHE.pop(old_event_id[0], None)
    
    _WEBHOOK_CACHE[event_id] = {
        "processed": True,
        "timestamp": time.time(),
        "result": result,
    }


def _cleanup_expired_entries() -> int:
    """Remove expired entries from the cache."""
    now = time.time()
    expired_keys = [
        event_id for event_id, data in _WEBHOOK_CACHE.items()
        if now - data.get("timestamp", 0) >= _WEBHOOK_CACHE_TTL
    ]
    for key in expired_keys:
        del _WEBHOOK_CACHE[key]
    return len(expired_keys)


def verify_admin_secret(
    request: Request,
    x_admin_secret: str = Header(...),
) -> str:
    """Verify admin secret for protected endpoints."""
    admin_secret = os.getenv("ADMIN_SECRET")

    if not admin_secret:
        logger.error("ADMIN_SECRET environment variable not set")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured.",
        )

    if not secrets.compare_digest(x_admin_secret.encode(), admin_secret.encode()):
        client_ip = get_remote_address(request)
        logger.warning("Failed admin access attempt from IP: %s", client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret",
        )

    logger.info("Admin access granted")
    return x_admin_secret


async def handle_checkout_session_completed(session: dict[str, Any]) -> dict[str, Any]:
    """
    Handle checkout.session.completed webhook event.

    Implements idempotent processing using in-memory cache.

    Args:
        session: Stripe session object

    Returns:
        Processing result dictionary
    """
    session_id = session.get("id") or ""
    payment_status = session.get("payment_status")
    metadata = session.get("metadata", {})

    result: dict[str, Any] = {
        "event_type": "checkout.session.completed",
        "processed": False,
        "message": "",
        "payment_id": metadata.get("payment_id"),
        "intake_id": metadata.get("intake_id"),
        "draft_id": metadata.get("draft_id"),
        "fulfillment_result": None,
    }

    # Only process paid sessions
    if payment_status != "paid":
        result["message"] = f"Payment not completed: {payment_status}"
        return result

    # Validate session_id
    if not session_id:
        result["message"] = "No session ID provided"
        return result

    # Idempotency check - check database first to avoid race conditions
    event_id = _generate_event_id("checkout.session.completed", session_id)
    
    try:
        db_service = get_db_service()
        payment = db_service.get_payment_by_session(session_id)
        
        # Check database for existing payment status before checking cache
        if payment:
            payment_status_value = (
                payment.status.value
                if hasattr(payment.status, "value")
                else str(payment.status)
            )
            is_paid = payment_status_value == PaymentStatus.PAID.value
            is_fulfilled = getattr(payment, "is_fulfilled", False)
            
            if is_paid and is_fulfilled:
                result["processed"] = True
                result["message"] = "Already fulfilled (idempotent)"
                logger.info("Webhook already processed for payment %s", payment.id)
                # Cache the result for future quick lookups
                _mark_event_processed(event_id, "checkout.session.completed", result)
                return result
        
        # Check cache only after database check to avoid race conditions
        is_processed, cached_result = _is_event_processed(event_id)
        if is_processed and cached_result:
            logger.info("Returning cached result for event %s", event_id)
            return cached_result

        if not payment:
            payment_id = metadata.get("payment_id")
            logger.warning("Payment not found for session %s", session_id)
            result["message"] = f"Payment not found for session {session_id}"
            # Cache the result to prevent retries
            _mark_event_processed(event_id, "checkout.session.completed", result)
            return result

        # Update payment status to PAID
        now = datetime.now(timezone.utc)
        updated_payment = db_service.update_payment_status(
            stripe_session_id=session_id,
            status=PaymentStatus.PAID,
            stripe_payment_intent=session.get("payment_intent") or "",
            stripe_customer_id=session.get("customer") or "",
            receipt_url=session.get("receipt_url") or "",
            paid_at=now,
            stripe_metadata=metadata,
        )

        if not updated_payment:
            result["message"] = "Failed to update payment status"
            return result

        # Get intake and draft for fulfillment
        intake = db_service.get_intake(payment.intake_id)
        if not intake:
            result["message"] = f"Intake {payment.intake_id} not found"
            return result

        draft = db_service.get_latest_draft(payment.intake_id)
        if not draft:
            result["message"] = f"Draft for intake {payment.intake_id} not found"
            return result

        # Extract city_id from metadata
        city_id: str | None = None
        section_id: str | None = None

        if metadata:
            city_id = metadata.get("city_id") or metadata.get("cityId")
            section_id = metadata.get("section_id") or metadata.get("sectionId")

        # Fallback: re-validate citation
        if not city_id:
            try:
                from ..services.citation import CitationValidator

                validator = CitationValidator()
                validation = validator.validate_citation(intake.citation_number)
                if validation and validation.city_id:
                    city_id = validation.city_id
                    section_id = validation.section_id
                    logger.info(
                        "Re-validated citation %s: city_id=%s, section_id=%s",
                        intake.citation_number,
                        city_id,
                        section_id,
                    )
            except Exception as e:
                logger.warning("Could not re-validate citation: %s", e)

        # Prepare mail request
        mail_request = AppealLetterRequest(
            citation_number=intake.citation_number,
            appeal_type=payment.appeal_type.value
            if hasattr(payment.appeal_type, "value")
            else str(payment.appeal_type),
            user_name=intake.user_name,
            user_address=intake.user_address_line1,
            user_city=intake.user_city,
            user_state=intake.user_state,
            user_zip=intake.user_zip,
            letter_text=draft.draft_text,
            signature_data=intake.signature_data,
            city_id=city_id,
            section_id=section_id,
        )

        # Send appeal via mail service
        mail_service = get_mail_service()
        mail_result = await mail_service.send_appeal_letter(mail_request)

        # Update payment with fulfillment result
        if mail_result.success:
            tracking_id = (
                mail_result.tracking_number
                or f"LOB_{now.strftime('%Y%m%d_%H%M%S')}_{payment.id}"
            )
            mail_type = (
                "certified"
                if payment.appeal_type == AppealType.CERTIFIED
                else "standard"
            )

            fulfillment_result = db_service.mark_payment_fulfilled(
                stripe_session_id=session_id,
                lob_tracking_id=tracking_id,
                lob_mail_type=mail_type,
            )

            if fulfillment_result:
                result["processed"] = True
                result["message"] = "Payment processed and appeal sent successfully"
                result["fulfillment_result"] = {
                    "success": True,
                    "tracking_number": mail_result.tracking_number,
                    "letter_id": mail_result.letter_id,
                    "expected_delivery": mail_result.expected_delivery,
                }

                logger.info(
                    "Successfully fulfilled appeal for payment %s, citation %s, tracking: %s",
                    payment.id,
                    intake.citation_number,
                    mail_result.tracking_number,
                )

                # Send email notifications
                email_service = get_email_service()
                if intake.user_email:
                    await email_service.send_payment_confirmation(
                        email=intake.user_email,
                        citation_number=intake.citation_number,
                        amount_paid=payment.amount_total,
                        appeal_type=str(payment.appeal_type),
                        session_id=session_id,
                    )

                    await email_service.send_appeal_mailed(
                        email=intake.user_email,
                        citation_number=intake.citation_number,
                        tracking_number=mail_result.tracking_number or "",
                        expected_delivery=mail_result.expected_delivery,
                    )
            else:
                result["message"] = (
                    "Payment marked as paid but failed to mark as fulfilled"
                )
                logger.error("Failed to mark payment %s as fulfilled", payment.id)
        else:
            error_msg = mail_result.error_message or "Unknown mail error"
            result["message"] = f"Payment processed but mail failed: {error_msg}"
            logger.error(
                "Mail service failed for payment %s, citation %s: %s",
                payment.id,
                intake.citation_number,
                error_msg,
            )

            # Mark payment as failed_fulfillment for retry
            payment.status = "failed_fulfillment"
            db_service.db.commit()
            
            # Alert admin via Sentry (already configured in app.py)
            # The /admin/retry endpoint can be used to retry failed mailings
            # DO NOT suspend the droplet - that would take the entire service offline

    except ValueError as e:
        # Specific error for missing data
        logger.error(
            "Validation error processing checkout.session.completed for session %s: %s",
            session_id,
            str(e),
        )
        result["message"] = f"Validation error: {str(e)}"
    except Exception as e:
        # Log specific error type and message for debugging
        error_type = type(e).__name__
        error_msg = str(e)
        logger.exception(
            "Error processing checkout.session.completed for session %s: %s (%s)",
            session_id,
            error_msg,
            error_type,
        )
        result["message"] = f"Error processing payment: {error_type}: {error_msg}"

    # Always cache the result for idempotency
    _mark_event_processed(event_id, "checkout.session.completed", result)
    
    return result


async def handle_payment_intent_succeeded(
    payment_intent: dict[str, Any],
) -> dict[str, Any]:
    """Handle payment_intent.succeeded event."""
    return {
        "event_type": "payment_intent.succeeded",
        "processed": True,
        "message": "Payment intent succeeded",
        "payment_intent_id": payment_intent.get("id"),
    }


async def handle_payment_intent_failed(
    payment_intent: dict[str, Any],
) -> dict[str, Any]:
    """Handle payment_intent.failed event."""
    return {
        "event_type": "payment_intent.failed",
        "processed": True,
        "message": "Payment failed",
        "payment_intent_id": payment_intent.get("id"),
        "error": payment_intent.get("last_payment_error", {}).get("message"),
    }


@router.post("")
async def handle_stripe_webhook(request: Request) -> dict[str, Any]:
    """
    Main webhook endpoint for Stripe events.

    This endpoint:
    1. Verifies the webhook signature
    2. Routes to appropriate handler based on event type
    3. Returns processing result
    """
    body = await request.body()
    signature = request.headers.get("stripe-signature", "")

    stripe_service = StripeService()

    if not stripe_service.verify_webhook_signature(body, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        event_data = await request.json()
        event_type = event_data.get("type")
        event_payload = event_data.get("data", {}).get("object", {})

        handlers = {
            "checkout.session.completed": handle_checkout_session_completed,
            "payment_intent.succeeded": handle_payment_intent_succeeded,
            "payment_intent.payment_failed": handle_payment_intent_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            result = await handler(event_payload)
            return result
        else:
            logger.info("Unhandled event type: %s", event_type)
            return {
                "event_type": event_type,
                "processed": False,
                "message": "Unhandled event",
            }

    except Exception as e:
        logger.exception("Error processing webhook")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/retry")
@limiter.limit("100/day;20/hour")
async def retry_fulfillment(
    request: Request,
    admin_secret: str = Depends(verify_admin_secret),
) -> dict[str, Any]:
    """
    Admin endpoint to retry fulfillment for failed payments.

    SECURITY: Requires admin authentication via X-Admin-Secret header.
    """
    try:
        body = await request.json()
        session_id = body.get("session_id")

        if not session_id:
            return {"success": False, "message": "session_id required"}

        # Re-verify admin secret (double-check for high-value operation)
        verify_admin_secret(request, admin_secret)

        logger.info("Admin retry fulfillment for session: %s", session_id)

        # Get session data from Stripe
        stripe_service = StripeService()
        try:
            session = stripe_service.stripe.checkout.Session.retrieve(session_id)
        except Exception as stripe_err:
            logger.error("Failed to retrieve session from Stripe: %s", stripe_err)
            return {"success": False, "message": "Session not found in Stripe"}

        # Re-process
        result = await handle_checkout_session_completed(session)

        return {
            "success": result.get("processed", False),
            "message": result.get("message"),
            "fulfillment_result": result.get("fulfillment_result"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in retry_fulfillment")
        return {"success": False, "message": str(e)}


@router.get("/health")
async def webhook_health() -> dict[str, Any]:
    """Health check endpoint for webhook service."""
    # Clean up expired entries occasionally
    cleaned = _cleanup_expired_entries()
    
    return {
        "status": "healthy",
        "service": "stripe-webhooks",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache": {
            "size": len(_WEBHOOK_CACHE),
            "max_size": _WEBHOOK_CACHE_MAX_SIZE,
            "ttl_seconds": _WEBHOOK_CACHE_TTL,
            "cleaned_expired": cleaned,
        },
    }


@router.get("/cache/stats")
async def webhook_cache_stats() -> dict[str, Any]:
    """Get webhook idempotency cache statistics."""
    return {
        "cache_size": len(_WEBHOOK_CACHE),
        "max_size": _WEBHOOK_CACHE_MAX_SIZE,
        "ttl_seconds": _WEBHOOK_CACHE_TTL,
        "oldest_entry": min(
            (data["timestamp"] for data in _WEBHOOK_CACHE.values()),
            default=None
        ),
        "newest_entry": max(
            (data["timestamp"] for data in _WEBHOOK_CACHE.values()),
            default=None
        ),
    }
