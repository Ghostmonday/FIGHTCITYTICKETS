"""
Stripe Payment Service for FIGHTCITYTICKETS.com

Handles Stripe checkout session creation, webhook verification, and payment status.
Integrates with citation validation and mail fulfillment.
"""

from dataclasses import dataclass
from typing import Any

import stripe

from ..config import settings
from .appeal_storage import get_appeal_storage
from .citation import CitationValidator
from .mail import AppealLetterRequest, send_appeal_letter

# Constants for magic numbers
ZIP_CODE_LENGTH = 5
STATE_CODE_LENGTH = 2


@dataclass
class CheckoutRequest:
    """Complete checkout request data."""

    # Required fields (no defaults) must come first
    citation_number: str
    user_name: str
    user_address_line1: str
    
    # Optional fields with defaults
    # CERTIFIED-ONLY MODEL: All appeals use Certified Mail with tracking
    # No subscription, no standard option - single $14.50 transaction
    appeal_type: str = "certified"
    user_address_line2: str | None = None
    user_city: str = ""
    user_state: str = ""
    user_zip: str = ""
    violation_date: str = ""
    vehicle_info: str = ""
    appeal_reason: str = ""
    email: str | None = None
    license_plate: str | None = None
    city_id: str | None = None  # BACKLOG PRIORITY 3: Multi-city support
    section_id: str | None = None  # BACKLOG PRIORITY 3: Multi-city support
    # AUDIT FIX: Database-first - IDs from pre-created records
    payment_id: int | None = None
    intake_id: int | None = None
    draft_id: int | None = None
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
    citation_number: str | None = None
    appeal_type: str | None = None
    user_email: str | None = None


class StripeService:
    """Handles all Stripe payment operations with timeout and retry handling."""

    # Timeout configuration (in seconds)
    DEFAULT_TIMEOUT = 30
    RETRY_COUNT = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self) -> None:
        """Initialize Stripe with API key from settings."""
        stripe.api_key = settings.stripe_secret_key

        # Set default timeout for all Stripe requests
        stripe.default_http_client = stripe.http_client.HTTPClient(
            timeout=self.DEFAULT_TIMEOUT
        )

        # Determine if we're in test or live mode
        self.is_live_mode: bool = settings.stripe_secret_key.startswith("sk_live_")
        self.mode: str = "live" if self.is_live_mode else "test"

        # Get price IDs based on mode
        self.price_ids: dict[str, str] = {
            "standard": settings.stripe_price_standard,
            "certified": settings.stripe_price_certified,
        }

        # Base URLs for redirects
        self.base_url: str = settings.app_url.rstrip("/")

    def _with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic for transient failures.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the function

        Raises:
            Exception: After all retries are exhausted
        """
        import time

        last_exception = None
        for attempt in range(self.RETRY_COUNT):
            try:
                return func(*args, **kwargs)
            except stripe.error.RateLimitError as e:
                # Retry on rate limits
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
            except stripe.error.APIConnectionError as e:
                # Retry on network issues
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
            except stripe.error.APIError as e:
                # Retry on Stripe API errors (500-503)
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
            except Exception as e:
                # Don't retry other errors
                raise e

        # All retries exhausted
        raise last_exception

    def get_price_id(self, appeal_type: str = "certified") -> str:
        """
        Get Stripe price ID for certified appeals only.

        Args:
            appeal_type: Ignored - only certified is supported

        Returns:
            Stripe price ID for certified service
        """
        # CERTIFIED-ONLY: Always return certified price
        return self.price_ids.get("certified")

    def validate_checkout_request(
        self, request: CheckoutRequest
    ) -> tuple[bool, str | None]:
        """
        Validate checkout request data.

        Args:
            request: CheckoutRequest object

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate citation number
        validator = CitationValidator()
        validation = validator.validate_citation(
            request.citation_number, request.violation_date, request.license_plate
        )

        if not validation.is_valid:
            return False, validation.error_message

        # Check if past deadline
        if validation.is_past_deadline:
            return False, "Appeal deadline has passed"

        # CERTIFIED-ONLY: No validation needed - always certified
        # All appeals use Certified Mail with Electronic Return Receipt

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
        state_clean = request.user_state.strip()
        if len(state_clean) != STATE_CODE_LENGTH:
            return False, "State must be 2-letter code (e.g., CA)"

        # Validate ZIP code format
        zip_clean = request.user_zip.strip()
        if not (zip_clean.isdigit() and len(zip_clean) == ZIP_CODE_LENGTH):
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
            msg = f"Invalid checkout request: {error_msg}"
            raise ValueError(msg)

        # CERTIFIED-ONLY: Always use certified price
        price_id = self.get_price_id()

        # Prepare metadata for webhook
        # AUDIT FIX: Database-first - store only IDs in metadata, not full data
        # CYCLE 3: Chargeback prevention - add dispute armor metadata
        metadata: dict[str, str] = {
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
            # Create Stripe checkout session with retry logic
            def create_session():
                return stripe.checkout.Session.create(
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
                    customer_email=request.email or None,
                    billing_address_collection="required",
                    shipping_address_collection={
                        "allowed_countries": ["US"],
                    },
                )

            session = self._with_retry(create_session)

            return CheckoutResponse(
                checkout_url=session.url or "",
                session_id=session.id,
                amount_total=session.amount_total or 0,
                currency=session.currency or "usd",
            )

        except stripe.error.StripeError as e:
            msg = f"Stripe error creating checkout session: {str(e)}"
            raise Exception(msg) from e
        except Exception as e:
            msg = f"Error creating checkout session: {str(e)}"
            raise Exception(msg) from e

    def get_session_status(self, session_id: str) -> SessionStatus:
        """
        Get status of a checkout session.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            SessionStatus object
        """
        try:
            # Retrieve session with retry logic
            def retrieve_session():
                return stripe.checkout.Session.retrieve(session_id)

            session = self._with_retry(retrieve_session)

            return SessionStatus(
                session_id=session.id,
                payment_status=session.payment_status,
                amount_total=session.amount_total or 0,
                currency=session.currency or "usd",
                citation_number=session.metadata.get("citation_number")
                if session.metadata
                else None,
                # CERTIFIED-ONLY: appeal_type is always "certified"
                appeal_type="certified",
                user_email=session.customer_email,
            )

        except stripe.error.StripeError as e:
            msg = f"Stripe error retrieving session: {str(e)}"
            raise Exception(msg) from e

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

    async def handle_webhook_event(self, event: dict[str, Any]) -> dict[str, Any]:
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

        result: dict[str, Any] = {
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
                existing_appeal = None
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
    user_name: str = "",
    user_address: str = "",
    user_city: str = "",
    user_state: str = "",
    user_zip: str = "",
    violation_date: str = "",
    vehicle_info: str = "",
    appeal_reason: str = "",
    email: str | None = None,
) -> str | None:
    """
    Quick helper function to create checkout link.

    Args:
        citation_number: The citation number to appeal
        user_*: User address and personal info
        violation_date, vehicle_info, appeal_reason: Appeal details
        email: User email for receipts

    Returns:
        Stripe checkout URL or None on error
    """
    try:
        service = StripeService()

        request = CheckoutRequest(
            citation_number=citation_number,
            appeal_type="certified",
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
    print("Testing Stripe Service")
    print("=" * 50)

    # Note: This requires Stripe API keys to be set
    try:
        service = StripeService()
        print(f"Stripe service initialized (mode: {service.mode})")

        # CERTIFIED-ONLY: Only test certified price
        certified_price = service.get_price_id()
        print(
            f"Price ID loaded - Certified: {certified_price[:20] if certified_price else 'NOT SET'}..."
        )

        print("\nNote: Full testing requires valid Stripe API keys")
        print("   Set STRIPE_SECRET_KEY in .env file to test checkout creation")

    except Exception as e:
        print(f"Error initializing Stripe service: {e}")
        print("   Make sure stripe package is installed: pip install stripe")

    print("\n" + "=" * 50)
    print("Stripe Service Test Complete")
