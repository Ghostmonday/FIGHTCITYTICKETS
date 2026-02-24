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
from starlette.concurrency import run_in_threadpool

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


def _is_event_processed_db(event_id: str) -> tuple[bool, Optional[dict]]:
    """Blocking database check for processed event."""
    try:
        db_service = get_db_service()
        # Use proper context manager for session
        with db_service.get_session() as session:
            # Check database for processed event
            event = session.query(WebhookEvent).filter(
                WebhookEvent.stripe_event_id == event_id,
                WebhookEvent.processed == True
            ).first()

            if event:
                return True, {"message": event.result_message}

            return False, None
    except Exception as e:
        logger.warning("Database idempotency check failed: %s", e)
        return False, None


async def _is_event_processed(event_id: str) -> tuple[bool, Optional[dict]]:
    """
    Check if an event has already been processed (async, database-backed).
    
    Returns:
        (is_processed, cached_result)
    """
    # Check database first (in thread)
    is_processed, result = await run_in_threadpool(_is_event_processed_db, event_id)
    if is_processed:
        return True, result

    # Check memory cache as fallback
    return _is_event_processed_memory(event_id)


def _mark_event_processed_db(event_id: str, event_type: str, result: dict) -> None:
    """Mark an event as processed in the database (blocking)."""
    try:
        db_service = get_db_service()
        with db_service.get_session() as session:
            # Check if already exists
            existing = session.query(WebhookEvent).filter(
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
                session.add(webhook_event)

            session.commit()
    except Exception as e:
        logger.warning("Failed to mark event processed in database: %s", e)


async def _mark_event_processed(event_id: str, event_type: str, result: dict) -> None:
    """Mark an event as processed (async, database + memory)."""
    # Update database (in thread)
    await run_in_threadpool(_mark_event_processed_db, event_id, event_type, result)

    # Update memory cache (sync)
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


def _process_payment_data_sync(
    session_id: str,
    payment_intent: str,
    customer: str,
    receipt_url: str,
    metadata: dict,
    event_id: str,
) -> tuple[dict, bool, Optional[AppealLetterRequest], Optional[int], Optional[str], Optional[str], Optional[str]]:
    """
    Synchronously process payment data and prepare for fulfillment.

    Returns:
        (result, should_continue, mail_request, payment_id, citation_number, user_email, appeal_type_str)
    """
    result: dict[str, Any] = {
        "event_type": "checkout.session.completed",
        "processed": False,
        "message": "",
        "payment_id": metadata.get("payment_id"),
        "intake_id": metadata.get("intake_id"),
        "draft_id": metadata.get("draft_id"),
        "fulfillment_result": None,
    }

    try:
        db_service = get_db_service()
        payment = db_service.get_payment_by_session(session_id)
        
        # Check database for existing payment status
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
                # Cache the result
                _mark_event_processed_db(event_id, "checkout.session.completed", result)
                return result, False, None, payment.id, None, None, None
        
        if not payment:
            logger.warning("Payment not found for session %s", session_id)
            result["message"] = f"Payment not found for session {session_id}"
            # Cache the result
            _mark_event_processed_db(event_id, "checkout.session.completed", result)
            return result, False, None, None, None, None, None

        # Update payment status to PAID
        now = datetime.now(timezone.utc)
        updated_payment = db_service.update_payment_status(
            stripe_session_id=session_id,
            status=PaymentStatus.PAID,
            stripe_payment_intent=payment_intent,
            stripe_customer_id=customer,
            receipt_url=receipt_url,
            paid_at=now,
            stripe_metadata=metadata,
        )

        if not updated_payment:
            result["message"] = "Failed to update payment status"
            return result, False, None, payment.id, None, None, None

        # Get intake and draft
        intake = db_service.get_intake(payment.intake_id)
        if not intake:
            result["message"] = f"Intake {payment.intake_id} not found"
            return result, False, None, payment.id, None, None, None

        draft = db_service.get_latest_draft(payment.intake_id)
        if not draft:
            result["message"] = f"Draft for intake {payment.intake_id} not found"
            return result, False, None, payment.id, intake.citation_number, intake.user_email, None

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

        appeal_type_str = (
            payment.appeal_type.value
            if hasattr(payment.appeal_type, "value")
            else str(payment.appeal_type)
        )

        # Prepare mail request
        mail_request = AppealLetterRequest(
            citation_number=intake.citation_number,
            user_name=intake.user_name,
            user_address_line_1=intake.user_address_line1,
            user_address_line_2=intake.user_address_line2,
            user_city=intake.user_city,
            user_state=intake.user_state,
            user_zip=intake.user_zip,
            user_email=intake.user_email or "",
            letter_text=draft.draft_text,
            agency_name=city_id or "unknown",
            agency_address="",
            appeal_type=appeal_type_str,
            signature_data=intake.signature_data,
            city_id=city_id,
            section_id=section_id,
        )

        return result, True, mail_request, payment.id, intake.citation_number, intake.user_email, appeal_type_str

    except Exception as e:
        logger.exception("Error in _process_payment_data_sync")
        result["message"] = f"Error processing payment data: {str(e)}"
        return result, False, None, None, None, None, None


def _handle_mail_failure_sync(payment_id: int) -> None:
    """Mark payment as failed fulfillment (blocking)."""
    try:
        db_service = get_db_service()
        with db_service.get_session() as session:
             payment = session.query(Payment).filter(Payment.id == payment_id).first()
             if payment:
                 # Note: 'failed_fulfillment' is not in PaymentStatus enum, using 'failed' instead
                 # or falling back to string if flexible.
                 # Replicating intent of original code but being safer.
                 payment.status = PaymentStatus.FAILED
             session.commit()
    except Exception as e:
        logger.error("Failed to mark payment failure: %s", e)


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

    # Check cache (Async now)
    try:
        is_processed, cached_result = await _is_event_processed(event_id)
        if is_processed and cached_result:
             logger.info("Returning cached result for event %s", event_id)
             return cached_result
    except Exception as e:
         logger.warning("Idempotency check failed: %s", e)

    # Process payment data (DB intensive)
    payment_intent = session.get("payment_intent") or ""
    customer = session.get("customer") or ""
    receipt_url = session.get("receipt_url") or ""

    (
        process_result,
        should_continue,
        mail_request,
        payment_id,
        citation_number,
        user_email,
        appeal_type_str
    ) = await run_in_threadpool(
        _process_payment_data_sync,
        session_id=session_id,
        payment_intent=payment_intent,
        customer=customer,
        receipt_url=receipt_url,
        metadata=metadata,
        event_id=event_id,
    )

    # Merge process_result into result
    result.update(process_result)

    if not should_continue:
        return result

    if not mail_request or not payment_id:
        # Should not happen if should_continue is True
        result["message"] = "Internal error: Missing mail request data"
        return result

    try:
        # Send appeal via mail service (Async)
        mail_service = get_mail_service()
        # mail_request is not None if should_continue is True
        mail_result = await mail_service.send_appeal_letter(mail_request)

        # Update payment with fulfillment result
        if mail_result.success:
            tracking_id = (
                mail_result.tracking_number
                or f"LOB_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{payment_id}"
            )
            mail_type = "standard"
            if appeal_type_str == AppealType.CERTIFIED.value:
                 mail_type = "certified"

            # Mark fulfilled (Blocking DB)
            db_service = get_db_service()
            fulfillment_result = await run_in_threadpool(
                db_service.mark_payment_fulfilled,
                stripe_session_id=session_id,
                lob_tracking_id=tracking_id,
                lob_mail_type=mail_type,
            )

            if fulfillment_result:
                 # Update result dict
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
                    payment_id,
                    citation_number,
                    mail_result.tracking_number,
                )

                 # Send email notifications (Async)
                 email_service = get_email_service()
                 if user_email:
                      await email_service.send_payment_confirmation(
                          email=user_email,
                          citation_number=citation_number or "",
                          amount_paid=fulfillment_result.amount_total,
                          appeal_type=appeal_type_str or "standard",
                          session_id=session_id,
                      )

                      await email_service.send_appeal_mailed(
                          email=user_email,
                          citation_number=citation_number or "",
                          tracking_number=mail_result.tracking_number or "",
                          expected_delivery=mail_result.expected_delivery,
                      )
            else:
                 result["message"] = (
                    "Payment marked as paid but failed to mark as fulfilled"
                 )
                 logger.error("Failed to mark payment %s as fulfilled", payment_id)
        else:
             # Mail failed
             error_msg = mail_result.error_message or "Unknown mail error"
             result["message"] = f"Payment processed but mail failed: {error_msg}"
             logger.error(
                "Mail service failed for payment %s, citation %s: %s",
                payment_id,
                citation_number,
                error_msg,
             )

             # Handle failure (Blocking DB update)
             await run_in_threadpool(_handle_mail_failure_sync, payment_id)

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

    # Cache result (Async)
    await _mark_event_processed(event_id, "checkout.session.completed", result)
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
