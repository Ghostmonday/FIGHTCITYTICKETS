"""
Stripe Payment Service for FightCityTickets.com

Handles Stripe checkout session creation, webhook verification, and payment status.
Integrates with citation validation and mail fulfillment.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import stripe

from ..config import settings
from .appeal_storage import AppealData, get_appeal_storage

# Import mail service for triggering letter after payment
from .mail import AppealLetterRequest, send_appeal_letter


@dataclass
class CheckoutRequest:
    """Complete checkout request data."""

    citation_number: str
    appeal_type: str  # "standard" or "certified"
    user_name: str
    user_address_line1: str
    user_address_line2: Optional[str] = None
    user_city: str = ""
    user_state: str = ""
    user_zip: str = ""
    violation_date: str = ""
    vehicle_info: str = ""
    appeal_reason: str = ""
    email: Optional[str] = None
    license_plate: Optional[str] = None
    city_id: Optional[str] = None  # BACKLOG PRIORITY 3: Multi-city support
    section_id: Optional[str] = None  # BACKLOG PRIORITY 3: Multi-city support
    # AUDIT FIX: Database-first - IDs from pre-created records
    payment_id: Optional[int] = None
    intake_id: Optional[int] = None
    draft_id: Optional[int] = None
    # CYCLE 3: Chargeback prevention - user acknowledgment of service terms
    user_attestation: bool = False


@dataclass
class CheckoutResponse:
    """Checkout session response."""

    checkout_url: str
    session_id: str
    amount_total: int
    currency: str = "usd"
    status: str = "created"


@dataclass
class SessionStatus:
    """Payment session status."""

    session_id: str
    payment_status: str  # "paid", "unpaid", "no_payment_required"
    amount_total: int
    currency: str
    citation_number: Optional[str] = None
    appeal_type: Optional[str] = None
    user_email: Optional[str] = None


class StripeService:
    """Handles all Stripe payment operations."""

    def __init__(self):
        """Initialize Stripe with API key from settings."""
        stripe.api_key = settings.stripe_secret_key

        # Determine if we're in test or live mode
        self.is_live_mode = settings.stripe_secret_key.startswith("sk_live_")
        self.mode = "live" if self.is_live_mode else "test"

        # Get price IDs based on mode
        self.price_ids = {
            "standard": settings.stripe_price_standard,
            "certified": settings.stripe_price_certified,
        }

        # Base URLs for redirects
        self.base_url = settings.app_url.rstrip("/")

    def get_price_id(self, appeal_type: str) -> str:
        """
        Get Stripe price ID for appeal type.

        Args:
            appeal_type: "standard" or "certified"

        Returns:
            Stripe price ID
        """
        appeal_type = appeal_type.lower()
        if appeal_type not in self.price_ids:
            raise ValueError(
                "Invalid appeal type: {appeal_type}. Must be 'standard' or 'certified'"
            )

        return self.price_ids[appeal_type]

    def validate_checkout_request(
        self, request: CheckoutRequest
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate checkout request data.

        Args:
            request: CheckoutRequest object

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate citation number
        validation = CitationValidator.validate_citation(
            request.citation_number, request.violation_date, request.license_plate
        )

        if not validation.is_valid:
            return False, validation.error_message

        # Check if past deadline
        if validation.is_past_deadline:
            return False, "Appeal deadline has passed"

        # Validate appeal type
        if request.appeal_type not in ["standard", "certified"]:
            return False, "Appeal type must be 'standard' or 'certified'"

        # Validate required user fields
        if not request.user_name.strip():
            return False, "Name is required"

        if not request.user_address_line1.strip():
            return False, "Address is required"

        if not request.user_city.strip():
            return False, "City is required"

        if not request.user_state.strip():
            return False, "State is required"

        if not request.user_zip.strip():
            return False, "ZIP code is required"

        # Validate state format (2 letters)
        if len(request.user_state.strip()) != 2:
            return False, "State must be 2-letter code (e.g., CA)"

        # Validate ZIP code format
        zip_clean = request.user_zip.strip()
        if not (zip_clean.isdigit() and len(zip_clean) == 5):
            return False, "ZIP code must be 5 digits"

        return True, None

    def create_checkout_session(self, request: CheckoutRequest) -> CheckoutResponse:
        """
        Create a Stripe checkout session for appeal payment.

        Args:
            request: Complete checkout request data

        Returns:
            CheckoutResponse with session details
        """
        # Validate request
        is_valid, error_msg = self.validate_checkout_request(request)
        if not is_valid:
            raise ValueError("Invalid checkout request: {error_msg}")

        # Get price ID for appeal type
        price_id = self.get_price_id(request.appeal_type)

        # Prepare metadata for webhook
        # AUDIT FIX: Database-first - store only IDs in metadata, not full data
        # CYCLE 3: Chargeback prevention - add dispute armor metadata
        metadata = {
            # Only store IDs for webhook lookup (database-first approach)
            "payment_id": str(request.payment_id) if request.payment_id else "",
            "intake_id": str(request.intake_id) if request.intake_id else "",
            "draft_id": str(request.draft_id) if request.draft_id else "",
            # Minimal citation info for logging/debugging
            "citation_number": request.citation_number[:100],
            "appeal_type": request.appeal_type,
            # BACKLOG PRIORITY 3: Multi-city support - store city_id in metadata
            "city_id": (request.city_id or "")[:50],
            "section_id": (request.section_id or "")[:50],
            # CYCLE 3: DISPUTE ARMOR - Evidence for chargeback defense
            "service_type": "clerical_document_preparation",
            "user_attestation": "true" if request.user_attestation else "false",
            "delivery_method": "physical_mail_via_lob",
        }

        try:
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                metadata=metadata,
                success_url=f"{self.base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{self.base_url}/appeal",
                customer_email=request.email,
                billing_address_collection="required",
                shipping_address_collection={
                    "allowed_countries": ["US"],
                },
            )

            return CheckoutResponse(
                checkout_url=session.url,
                session_id=session.id,
                amount_total=session.amount_total,
                currency=session.currency,
            )

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error creating checkout session: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Error creating checkout session: {str(e)}") from e

    def get_session_status(self, session_id: str) -> SessionStatus:
        """
        Get status of a checkout session.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            SessionStatus object
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            return SessionStatus(
                session_id=session.id,
                payment_status=session.payment_status,
                amount_total=session.amount_total,
                currency=session.currency,
                citation_number=session.metadata.get("citation_number"),
                appeal_type=session.metadata.get("appeal_type"),
                user_email=session.customer_email,
            )

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error retrieving session: {str(e)}") from e

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature.

        Args:
            payload: Raw request body
            signature: Stripe signature header

        Returns:
            True if signature is valid
        """
        try:
            stripe.Webhook.construct_event(
                payload, signature, settings.stripe_webhook_secret
            )
            return True
        except stripe.error.SignatureVerificationError:
            return False
        except Exception:
            return False

    async def handle_webhook_event(self, event: Dict) -> Dict:
        """
        Handle Stripe webhook event.

        Args:
            event: Stripe event object

        Returns:
            Dictionary with processing result
        """
        event_type = event.get("type")
        data = event.get("data", {})
        object_data = data.get("object", {})

        result = {
            "event_type": event_type,
            "processed": False,
            "message": "",
            "metadata": {},
        }

        # Handle checkout.session.completed event
        if event_type == "checkout.session.completed":
            session = object_data
            session_id = session.get("id")

            # Extract metadata for fulfillment
            metadata = session.get("metadata", {})
            payment_status = session.get("payment_status")
            intake_id = metadata.get("intake_id")

            if payment_status == "paid":
                # IDEMPOTENCY CHECK: Prevent duplicate processing if Stripe retries webhook
                storage = get_appeal_storage()
                if intake_id:
                    existing_appeal = storage.get_appeal(intake_id)
                    if existing_appeal and existing_appeal.payment_status in [
                        "paid",
                        "processing",
                        "mailed",
                    ]:
                        result["processed"] = True
                        result["message"] = (
                            f"Duplicate webhook: Appeal {intake_id} already {existing_appeal.payment_status}"
                        )
                        return result

                result["processed"] = True
                result["message"] = "Payment successful, triggering mail fulfillment"
                result["metadata"] = metadata

                # Update payment status in storage
                if intake_id:
                    storage.update_payment_status(intake_id, session_id, "paid")

                # TRIGGER MAIL SERVICE: Send appeal letter after successful payment
                if intake_id and existing_appeal:
                    try:
                        print(f"Triggering mail service for intake {intake_id}...")

                        # Build AppealLetterRequest from stored appeal data
                        mail_request = AppealLetterRequest(
                            citation_number=existing_appeal.citation_number,
                            appeal_type=existing_appeal.appeal_type,
                            user_name=existing_appeal.user_name,
                            user_address=existing_appeal.user_address,
                            user_city=existing_appeal.user_city,
                            user_state=existing_appeal.user_state,
                            user_zip=existing_appeal.user_zip,
                            letter_text=existing_appeal.appeal_letter_text,
                        )

                        # Send to Lob
                        mail_result = await send_appeal_letter(mail_request)
                        print(
                            f"SUCCESS: Letter queued for intake {intake_id}, Lob ID: {mail_result.letter_id}"
                        )

                        # Update status to processing
                        storage.update_payment_status(
                            intake_id, session_id, "processing"
                        )

                    except Exception as e:
                        # CRITICAL FAILURE: Money taken, letter failed
                        error_msg = f"CRITICAL: Payment received but letter failed for {intake_id}: {str(e)}"
                        print(error_msg)
                        result["message"] = error_msg
                        # TODO: Alert via Sentry/PagerDuty

            else:
                result["message"] = f"Payment not completed: {payment_status}"

        # Handle payment_intent.succeeded (backup)
        elif event_type == "payment_intent.succeeded":
            result["processed"] = True
            result["message"] = "Payment intent succeeded"

        # Handle payment_intent.payment_failed
        elif event_type == "payment_intent.payment_failed":
            result["message"] = "Payment failed"

        return result


# Helper function for quick checkout
def create_checkout_link(
    citation_number: str,
    appeal_type: str = "standard",
    user_name: str = "",
    user_address: str = "",
    user_city: str = "",
    user_state: str = "",
    user_zip: str = "",
    violation_date: str = "",
    vehicle_info: str = "",
    appeal_reason: str = "",
    email: Optional[str] = None,
) -> Optional[str]:
    """
    Quick helper function to create checkout link.

    Args:
        Same as CheckoutRequest fields

    Returns:
        Stripe checkout URL or None on error
    """
    try:
        service = StripeService()

        request = CheckoutRequest(
            citation_number=citation_number,
            appeal_type=appeal_type,
            user_name=user_name,
            user_address_line1=user_address,
            user_city=user_city,
            user_state=user_state,
            user_zip=user_zip,
            violation_date=violation_date,
            vehicle_info=vehicle_info,
            appeal_reason=appeal_reason,
            email=email,
        )

        response = service.create_checkout_session(request)
        return response.checkout_url

    except Exception as e:
        print(f"Error creating checkout link: {e}")
        return None


# Test function
if __name__ == "__main__":
    print("🧪 Testing Stripe Service")
    print("=" * 50)

    # Note: This requires Stripe API keys to be set
    try:
        service = StripeService()
        print(f"✅ Stripe service initialized (mode: {service.mode})")

        # Test price IDs
        standard_price = service.get_price_id("standard")
        certified_price = service.get_price_id("certified")
        print(
            f"✅ Price IDs loaded - Standard: {standard_price[:20]}..., Certified: {certified_price[:20]}..."
        )

        print("\n⚠️  Note: Full testing requires valid Stripe API keys")
        print("   Set STRIPE_SECRET_KEY in .env file to test checkout creation")

    except Exception as e:
        print(f"❌ Error initializing Stripe service: {e}")
        print("   Make sure stripe package is installed: pip install stripe")

    print("\n" + "=" * 50)
    print("✅ Stripe Service Test Complete")
