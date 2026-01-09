"""
Stripe Webhook Handler for FightCityTickets.com (Database-First Approach)

Handles Stripe webhook events for payment confirmation and appeal fulfillment.
Uses database for persistent storage and implements idempotent processing.
Integrates with mail service for automatic appeal fulfillment.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..models import AppealType, PaymentStatus
from ..services.database import get_db_service
from ..services.mail import AppealLetterRequest, get_mail_service
from ..services.stripe_service import StripeService
from ..services.email_service import get_email_service

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter - shared instance from app.py
# BACKLOG PRIORITY 1: Rate limiting integration
limiter = Limiter(key_func=get_remote_address)

# Admin authentication for retry endpoint
ADMIN_SECRET_HEADER = "X-Admin-Secret"

def verify_admin_secret(
    request: Request,
    x_admin_secret: str = Header(...),
):
    """
    Verify the admin secret header for protected endpoints.

    SECURITY: This endpoint can trigger real mail sending and charges,
    so it requires admin authentication.
    """
    admin_secret = os.getenv("ADMIN_SECRET")

    if not admin_secret:
        logger.error("ADMIN_SECRET environment variable not set - admin routes disabled")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured. Set ADMIN_SECRET environment variable.",
        )

    if x_admin_secret != admin_secret:
        client_ip = get_remote_address(request)
        logger.warning(
            f"Failed admin access attempt on retry-fulfillment - Invalid admin secret provided. "
            f"IP: {client_ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret",
        )

    logger.info("Admin access granted for retry-fulfillment")
    return x_admin_secret


async def handle_checkout_session_completed(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle checkout.session.completed webhook event.

    Args:
        session: Stripe session object

    Returns:
        Processing result dictionary
    """
    session_id = session.get("id")
    payment_status = session.get("payment_status")
    metadata = session.get("metadata", {})

    result = {
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

    try:
        # Initialize services
        db_service = get_db_service()

        # Get payment from database
        payment = db_service.get_payment_by_session(session_id)

        if not payment:
            # Try to find by payment ID from metadata
            payment_id = metadata.get("payment_id")
            if payment_id and payment_id.isdigit():
                # We need to implement get_payment_by_id or search by metadata
                logger.warning(
                    f"Payment not found by session {session_id}, trying metadata ID {payment_id}"
                )
                # For now, we'll skip if not found by session ID
                result["message"] = f"Payment not found for session {session_id}"
                return result
            else:
                result["message"] = (
                    "Payment not found and no valid payment ID in metadata"
                )
                return result

        # Idempotency check
        if payment.status == PaymentStatus.PAID and payment.is_fulfilled:
            result["processed"] = True
            result["message"] = "Already fulfilled (idempotent)"
            logger.info(f"Webhook already processed for payment {payment.id}")
            return result

        # Update payment status to PAID
        updated_payment = db_service.update_payment_status(
            stripe_session_id=session_id,
            status=PaymentStatus.PAID,
            stripe_payment_intent=session.get("payment_intent"),
            stripe_customer_id=session.get("customer"),
            receipt_url=session.get("receipt_url"),
            paid_at=datetime.utcnow(),
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

        # BACKLOG PRIORITY 4: Extract city_id from metadata or re-validate citation
        city_id = None
        section_id = None

        # Try to get from Stripe metadata first
        if metadata:
            city_id = metadata.get("city_id") or metadata.get("cityId")
            section_id = metadata.get("section_id") or metadata.get("sectionId")

        # If not in metadata, try to get from payment metadata
        if not city_id and payment.stripe_metadata:
            city_id = payment.stripe_metadata.get("city_id") or payment.stripe_metadata.get("cityId")
            section_id = payment.stripe_metadata.get("section_id") or payment.stripe_metadata.get("sectionId")

        # Fallback: re-validate citation to get city_id (if CityRegistry available)
        if not city_id:
            try:
                from ..services.citation import CitationValidator
                validator = CitationValidator()
                validation = validator.validate_citation(intake.citation_number)
                if validation and validation.city_id:
                    city_id = validation.city_id
                    section_id = validation.section_id
                    logger.info(f"Re-validated citation {intake.citation_number}: city_id={city_id}, section_id={section_id}")
            except Exception as e:
                logger.warning(f"Could not re-validate citation for city_id: {e}")

        # Prepare mail request
        mail_request = AppealLetterRequest(
            citation_number=intake.citation_number,
            appeal_type=payment.appeal_type.value,
            user_name=intake.user_name,
            user_address=intake.user_address_line1,
            user_city=intake.user_city,
            user_state=intake.user_state,
            user_zip=intake.user_zip,
            letter_text=draft.draft_text,
            selected_photos=None,  # Would need to be stored separately
            signature_data=intake.signature_data,
            city_id=city_id,  # BACKLOG PRIORITY 4: Multi-city support
            section_id=section_id,  # BACKLOG PRIORITY 4: Multi-city support
        )

        # Send appeal via mail service
        mail_service = get_mail_service()
        mail_result = await mail_service.send_appeal_letter(mail_request)

        # Update payment with fulfillment result
        if mail_result.success:
            fulfillment_result = db_service.mark_payment_fulfilled(
                stripe_session_id=session_id,
                lob_tracking_id=mail_result.tracking_number
                or f"LOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{payment.id}",
                lob_mail_type="certified"
                if payment.appeal_type == AppealType.CERTIFIED
                else "standard",
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
                    f"Successfully fulfilled appeal for payment {payment.id}, "
                    f"citation {intake.citation_number}, "
                    f"tracking: {mail_result.tracking_number}"
                )

                # Send email notifications
                email_service = get_email_service()
                if intake.user_email:
                    # Send payment confirmation (if not already sent)
                    await email_service.send_payment_confirmation(
                        email=intake.user_email,
                        citation_number=intake.citation_number,
                        amount_paid=payment.amount_total,
                        appeal_type=payment.appeal_type.value,
                        session_id=session_id,
                    )

                    # Send appeal mailed confirmation
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
                logger.error(f"Failed to mark payment {payment.id} as fulfilled")
        else:
            result["message"] = (
                f"Payment processed but mail failed: {mail_result.error_message}"
            )
            logger.error(
                f"Mail service failed for payment {payment.id}, "
                f"citation {intake.citation_number}: {mail_result.error_message}"
            )

            # BACKLOG PRIORITY 1: Suspend droplet on critical failure
            # Only suspend if this is a critical failure (not test mode issues)
            if settings.app_env == "production" and "test" not in mail_result.error_message.lower():
                try:
                    from ..services.hetzner import get_hetzner_service
                    hetzner_service = get_hetzner_service()
                    if hetzner_service.is_available:
                        droplet_name = getattr(settings, "hetzner_droplet_name", None)
                        if droplet_name:
                            # Use await since we're already in an async function
                            suspension_result = await hetzner_service.suspend_droplet_by_name(droplet_name)
                            if suspension_result.success:
                                logger.critical(
                                    f"Droplet {droplet_name} suspended due to mail service failure"
                                )
                            else:
                                logger.error(
                                    f"Failed to suspend droplet: {suspension_result.error_message}"
                                )
                except Exception as e:
                    logger.error(f"Error attempting droplet suspension: {e}")

    except Exception as e:
        logger.error(
            f"Error processing checkout.session.completed for session {session_id}: {e}"
        )
        result["message"] = f"Error processing payment: {str(e)}"

    return result


async def handle_payment_intent_succeeded(
    payment_intent: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Handle payment_intent.succeeded webhook event (backup).

    Args:
        payment_intent: Stripe payment intent object

    Returns:
        Processing result dictionary
    """
    result = {
        "event_type": "payment_intent.succeeded",
        "processed": True,
        "message": "Payment intent succeeded (logged)",
    }

    logger.info(f"Payment intent succeeded: {payment_intent.get('id')}")

    return result


async def handle_payment_intent_failed(
    payment_intent: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Handle payment_intent.payment_failed webhook event.

    Args:
        payment_intent: Stripe payment intent object

    Returns:
        Processing result dictionary
    """
    result = {
        "event_type": "payment_intent.payment_failed",
        "processed": False,
        "message": "Payment failed",
    }

    logger.warning(f"Payment intent failed: {payment_intent.get('id')}")

    return result


@router.post("/stripe")
@limiter.limit("100/minute")  # BACKLOG PRIORITY 1: Rate limiting for webhooks (higher limit for Stripe)
async def handle_stripe_webhook(request: Request):
    """
    Handle Stripe webhook events with database-first approach.

    Processes payment confirmations and triggers appeal fulfillment.
    Implements idempotency to handle duplicate events safely.
    """
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("stripe-signature")

        if not signature:
            logger.warning("Missing Stripe signature in webhook request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature",
            )

        # Initialize Stripe service and verify signature
        stripe_service = StripeService()
        if not stripe_service.verify_webhook_signature(body, signature):
            logger.warning("Invalid Stripe webhook signature")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
            )

        # Parse the event
        event_data = json.loads(body.decode("utf-8"))
        event_type = event_data.get("type")
        data = event_data.get("data", {})
        object_data = data.get("object", {})

        # Route to appropriate handler
        if event_type == "checkout.session.completed":
            result = await handle_checkout_session_completed(object_data)
        elif event_type == "payment_intent.succeeded":
            result = await handle_payment_intent_succeeded(object_data)
        elif event_type == "payment_intent.payment_failed":
            result = await handle_payment_intent_failed(object_data)
        else:
            result = {
                "event_type": event_type,
                "processed": False,
                "message": f"Event type {event_type} not handled",
            }
            logger.info(f"Unhandled webhook event type: {event_type}")

        # Log the result
        log_icon = "✅" if result.get("processed") else "ℹ️"
        logger.info(
            f"Stripe webhook processed: {result['event_type']} - "
            f"Status: {log_icon} - "
            f"Message: {result['message']}"
        )

        # Always return 200 to acknowledge receipt (idempotent)
        return {
            "status": "acknowledged",
            "event_type": result.get("event_type"),
            "processed": result.get("processed", False),
            "message": result.get("message", ""),
            "payment_id": result.get("payment_id"),
            "intake_id": result.get("intake_id"),
            "draft_id": result.get("draft_id"),
        }

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload"
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}")
        # Still return 200 to prevent retries on our end
        # Stripe will interpret as successful processing
        return {
            "status": "error",
            "message": "Internal error, but event acknowledged",
            "error": str(e),
        }


@router.post("/retry-fulfillment/{session_id}")
@limiter.limit("10/minute")  # Strict rate limit - this costs money
async def retry_fulfillment(
    request: Request,
    session_id: str,
    admin_secret: str = Depends(verify_admin_secret),
):
    """
    Manually retry fulfillment for a payment.

    SECURITY: This endpoint requires admin authentication and can trigger
    real mail sending (costs $0.60-$6.50 per letter). Protected by:
    - Admin secret header (X-Admin-Secret)
    - Rate limiting (10 requests/minute)
    - Session ID validation

    Args:
        session_id: Stripe checkout session ID (must start with cs_test_ or cs_live_)

    Returns:
        Result of retry attempt
    """
    # Validate session ID format to prevent injection/guessing attacks
    if not session_id.startswith(("cs_test_", "cs_live_")):
        logger.warning(f"Invalid session ID format attempted: {session_id[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format. Must start with 'cs_test_' or 'cs_live_'",
        )

    # Additional validation: session ID length (Stripe session IDs are ~60 chars)
    if len(session_id) < 20 or len(session_id) > 100:
        logger.warning(f"Suspicious session ID length: {len(session_id)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID length",
        )

    try:
        # Verify payment exists and is in a valid state for retry
        db_service = get_db_service()
        payment = db_service.get_payment_by_session(session_id)

        if not payment:
            logger.warning(f"Retry attempted for non-existent payment: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found for session {session_id}",
            )

        # Only allow retry if payment is PAID but not fulfilled
        if payment.status != PaymentStatus.PAID:
            logger.warning(
                f"Retry attempted for payment in invalid state: {payment.status} "
                f"(session: {session_id})"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot retry fulfillment for payment with status: {payment.status.value}",
            )

        if payment.is_fulfilled:
            logger.info(f"Payment already fulfilled, returning current status (session: {session_id})")
            return {
                "status": "already_fulfilled",
                "message": "Payment is already fulfilled",
                "session_id": session_id,
                "lob_tracking_id": payment.lob_tracking_id,
            }

        # Re-process the checkout session completion (same logic as webhook)
        logger.info(f"Admin retry fulfillment initiated for session {session_id}")
        result = await handle_checkout_session_completed(
            {
                "id": session_id,
                "payment_status": "paid",
                "metadata": {
                    "payment_id": str(payment.id),
                    "intake_id": str(payment.intake_id),
                },
                "payment_intent": payment.stripe_payment_intent,
                "customer": None,
                "receipt_url": payment.receipt_url,
            }
        )

        if result.get("processed"):
            logger.info(f"Admin retry successful for session {session_id}")
            return {
                "status": "success",
                "message": result.get("message", "Fulfillment retried successfully"),
                "session_id": session_id,
                "payment_id": result.get("payment_id"),
                "intake_id": result.get("intake_id"),
            }
        else:
            logger.warning(f"Admin retry failed for session {session_id}: {result.get('message')}")
            return {
                "status": "error",
                "message": result.get("message", "Fulfillment retry failed"),
                "session_id": session_id,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin retry fulfillment for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry fulfillment: {str(e)}",
        ) from e


@router.get("/health")
async def webhook_health():
    """
    Health check endpoint for webhook service.

    Returns basic status information.
    """
    try:
        db_service = get_db_service()
        db_healthy = db_service.health_check()

        mail_service = get_mail_service()
        mail_available = mail_service.is_available

        return {
            "status": "healthy",
            "database": "connected" if db_healthy else "disconnected",
            "mail_service": "available" if mail_available else "unavailable",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
