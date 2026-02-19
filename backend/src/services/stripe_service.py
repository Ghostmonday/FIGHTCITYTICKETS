"""
Stripe Payment Service for Fight City Tickets

Handles Stripe checkout session creation, webhook verification, and payment status.
Integrates with citation validation.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional
import time
import logging

import stripe

from ..config import settings
from ..middleware.resilience import CircuitBreaker, create_stripe_circuit
from .citation import CitationValidator

logger = logging.getLogger(__name__)

# Constants for magic numbers
ZIP_CODE_LENGTH = 5
STATE_CODE_LENGTH = 2

# Circuit breaker configuration
STRIPE_CIRCUIT_FAILURE_THRESHOLD = 5
STRIPE_CIRCUIT_TIMEOUT = 300  # 5 minutes


@dataclass
class CheckoutRequest:
    """
    Complete checkout request data.
    DEPRECATED: Use individual parameters in create_session instead.
    """

    # Required fields (no defaults) must come first
    citation_number: str
    user_name: str
    user_address_line1: str
    
    # Optional fields with defaults
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
    city_id: str | None = None
    section_id: str | None = None
    payment_id: int | None = None
    intake_id: int | None = None
    draft_id: int | None = None
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

    # Circuit breaker configuration
    CIRCUIT_FAILURE_THRESHOLD = 5
    CIRCUIT_TIMEOUT = 300  # 5 minutes

    def __init__(self) -> None:
        """Initialize Stripe with API key from settings."""
        stripe.api_key = settings.stripe_secret_key

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

        # Circuit breaker for Stripe API resilience
        self._circuit_breaker = create_stripe_circuit(fallback=self._stripe_fallback)

    def _stripe_fallback(self) -> dict[str, Any]:
        """Fallback when Stripe circuit is open."""
        return {
            "status": "degraded",
            "message": "Stripe service temporarily unavailable. Please try again later.",
            "fallback": True,
        }

    def _with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic for transient failures (Synchronous).
        """
        last_exception = None
        for attempt in range(self.RETRY_COUNT):
            try:
                return func(*args, **kwargs)
            except stripe.error.RateLimitError as e:
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
            except stripe.error.APIConnectionError as e:
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
            except stripe.error.APIError as e:
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
            except Exception as e:
                raise e

        raise last_exception

    async def _with_retry_async(self, func, *args, **kwargs):
        """
        Execute a function with retry logic for transient failures (Asynchronous).
        """
        last_exception = None
        for attempt in range(self.RETRY_COUNT):
            try:
                # If func is async, await it. If sync, just call it?
                # Usually we pass a sync function to run, or async coroutine?
                # create_session passes a sync function `_create`.
                # So we call it, but if it fails, we await sleep.
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except stripe.error.RateLimitError as e:
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
            except stripe.error.APIConnectionError as e:
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
            except stripe.error.APIError as e:
                last_exception = e
                if attempt < self.RETRY_COUNT - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
            except Exception as e:
                raise e

        raise last_exception

    def get_price_id(self, appeal_type: str = "certified") -> str:
        """Get Stripe price ID for certified appeals only."""
        return self.price_ids.get("certified")

    def validate_checkout_request(
        self, request: CheckoutRequest
    ) -> tuple[bool, str | None]:
        """
        Validate checkout request data.
        DEPRECATED: Use explicit validation in route handlers.
        """
        validator = CitationValidator()
        validation = validator.validate_citation(
            request.citation_number, request.violation_date, request.license_plate
        )

        if not validation.is_valid:
            return False, validation.error_message

        if validation.is_past_deadline:
            return False, "Appeal deadline has passed"

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

        state_clean = request.user_state.strip()
        if len(state_clean) != STATE_CODE_LENGTH:
            return False, "State must be 2-letter code (e.g., CA)"

        zip_clean = request.user_zip.strip().replace("-", "").replace(" ", "")
        if len(zip_clean) == 5:
            if not zip_clean.isdigit():
                return False, "ZIP code must be 5 digits"
        elif len(zip_clean) == 9:
            if not zip_clean.isdigit():
                return False, "ZIP code must be 5 digits or 5+4 format"
        else:
            return False, "ZIP code must be 5 digits or 5+4 format"

        return True, None

    async def create_session(
        self,
        amount: int,
        currency: str,
        success_url: str,
        cancel_url: str,
        metadata: dict[str, str],
        customer_email: Optional[str] = None,
        payment_description: Optional[str] = None,
        line_items: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe checkout session with explicit parameters.
        Uses circuit breaker and retry logic.
        """
        def _create():
            args = {
                "mode": "payment",
                "payment_method_types": ["card"],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": metadata,
                "billing_address_collection": "required",
                "shipping_address_collection": {"allowed_countries": ["US"]},
            }
            if customer_email:
                args["customer_email"] = customer_email

            if line_items:
                args["line_items"] = line_items
            else:
                args["line_items"] = [{
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": payment_description or "Legal Service Fee",
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }]

            return stripe.checkout.Session.create(**args)

        async def _create_with_retry():
            return await self._with_retry_async(_create)

        # Use call (async) because _create_with_retry is async
        return await self._circuit_breaker.call(_create_with_retry)

    def create_checkout_session_legacy(self, request: CheckoutRequest) -> CheckoutResponse:
        """
        Create a Stripe checkout session for appeal payment.
        DEPRECATED: Use create_session instead.
        """
        is_valid, error_msg = self.validate_checkout_request(request)
        if not is_valid:
            msg = f"Invalid checkout request: {error_msg}"
            raise ValueError(msg)

        price_id = self.get_price_id()

        metadata: dict[str, str] = {
            "payment_id": str(request.payment_id) if request.payment_id else "",
            "intake_id": str(request.intake_id) if request.intake_id else "",
            "draft_id": str(request.draft_id) if request.draft_id else "",
            "citation_number": request.citation_number[:100],
            "appeal_type": request.appeal_type,
            "city_id": (request.city_id or "")[:50],
            "section_id": (request.section_id or "")[:50],
            "service_type": "clerical_document_preparation",
            "user_attestation": "true" if request.user_attestation else "false",
            "delivery_method": "physical_mail_via_lob",
        }

        try:
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
        """
        try:
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
                appeal_type="certified",
                user_email=session.customer_email,
            )

        except stripe.error.StripeError as e:
            msg = f"Stripe error retrieving session: {str(e)}"
            raise Exception(msg) from e

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature.
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
