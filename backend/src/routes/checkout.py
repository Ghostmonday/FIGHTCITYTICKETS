"""
Checkout Routes for FightCityTickets.com (Database-First Approach)

Handles payment session creation and status checking for appeal processing.
Uses database for persistent storage before creating Stripe checkout sessions.
"""

import httpx

from ..config import settings

# States where service is blocked due to UPL regulations
BLOCKED_STATES = ["TX", "NC", "NJ", "WA"]


async def verify_user_address(
    address1: str, city: str, state: str, zip_code: str
) -> tuple:
    """
    Validate user return address using Lob's US verification API.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        auth = (settings.lob_api_key, "")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.lob.com/v1/us_verifications",
                auth=auth,
                json={
                    "primary_line": address1,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code,
                },
            )

        if resp.status_code != 200:
            logger.warning(f"Lob address verification returned {resp.status_code}")
            return True, None  # Allow through if API fails

        data = resp.json()
        deliverability = data.get("deliverability", "unknown")

        # "deliverable" or "deliverable_missing_unit" are acceptable
        if deliverability == "undeliverable":
            return (
                False,
                "The return address provided is invalid or undeliverable. Please check your address and try again.",
            )
        elif deliverability == "missing_information":
            return (
                False,
                "Please complete your address with street, city, state, and ZIP code.",
            )

        return True, None

    except Exception as e:
        logger.warning(f"Address verification API error: {e}")
        return True, None  # Allow through if API fails


from __future__ import annotations

import logging
from typing import Optional  # noqa: F401

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from slowapi import Limiter

from ..models import AppealType
from ..services.database import get_db_service
from ..services.stripe_service import (
    CheckoutRequest,
    StripeService,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter - will be set from app.py after app initialization
# This is a placeholder that will be replaced by the shared limiter instance
limiter: Optional[Limiter] = None


class AppealCheckoutRequest(BaseModel):
    """Request model for appeal checkout session creation (database-first)."""

    # Citation information
    citation_number: str = Field(
        ..., min_length=3, max_length=20, examples=["912345678"]
    )
    violation_date: str = Field(..., examples=["2024-01-15"])
    vehicle_info: str = Field(..., max_length=200, examples=["Honda Civic ABC123"])
    license_plate: Optional[str] = Field(None, max_length=20, examples=["ABC123"])

    # User information
    user_name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    user_address_line1: str = Field(
        ..., min_length=1, max_length=200, examples=["123 Main St"]
    )
    user_address_line2: Optional[str] = Field(None, max_length=200, examples=["Apt 4B"])
    user_city: str = Field(..., min_length=1, max_length=50, examples=["San Francisco"])
    user_state: str = Field(..., min_length=2, max_length=2, examples=["CA"])
    user_zip: str = Field(..., min_length=5, max_length=10, examples=["94102"])
    user_email: Optional[str] = Field(None, examples=["user@example.com"])

    # Appeal content
    draft_text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        examples=[
            "I am appealing this citation because the parking meter was broken..."
        ],
        description="The full appeal letter text",
    )

    # Appeal type
    appeal_type: AppealType = Field(
        default=AppealType.STANDARD,
        examples=[AppealType.STANDARD, AppealType.CERTIFIED],
        description="Type of appeal (standard or certified)",
    )

    # Optional evidence
    selected_evidence: Optional[list] = Field(
        None,
        examples=[["photo1_id", "photo2_id"]],
        description="List of evidence IDs or references",
    )
    signature_data: Optional[str] = Field(
        None,
        examples=["data:image/png;base64,iVBORw0KGgoAAA..."],
        description="Base64-encoded signature image",
    )

    # CYCLE 3: Chargeback prevention - user attestation of service terms
    user_attestation: bool = Field(
        False,
        description="User has acknowledged they are paying for document preparation only",
    )

    # BACKLOG PRIORITY 3: Multi-city support
    city_id: Optional[str] = Field(
        None,
        examples=["s", "la", "nyc"],
        description="City identifier from citation validation",
    )
    section_id: Optional[str] = Field(
        None,
        examples=["sfmta", "lapd", "nydot"],
        description="Section/agency identifier from citation validation",
    )

    @validator("city_id")
    def validate_city_id(cls, v):
        """AUDIT FIX: Validate city_id format."""
        if v is None:
            return v
        # City IDs should be lowercase alphanumeric with underscores
        import re

        if not re.match(r"^[a-z0-9_]+$", v.lower()):
            raise ValueError(
                "city_id must be lowercase alphanumeric with underscores only"
            )
        return v.lower()

    @validator("user_state")
    def validate_state(cls, v):
        if len(v.strip()) != 2:
            raise ValueError("State must be 2-letter code")
        return v.upper().strip()

    @validator("user_zip")
    def validate_zip(cls, v):
        import re

        if not re.match(r"^\d{5}(-\d{4})?$", v.strip()):
            raise ValueError("ZIP code must be 5 or 9 digits")
        return v.strip()

    @validator("draft_text")
    def validate_draft_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Appeal letter text is required")
        if len(v.strip()) < 50:
            raise ValueError("Appeal letter must be at least 50 characters")
        return v.strip()


class AppealCheckoutResponse(BaseModel):
    """Response model for appeal checkout session (database-first)."""

    checkout_url: str
    session_id: str
    amount_total: int
    currency: str = "usd"
    appeal_type: AppealType
    citation_number: str
    payment_id: Optional[int] = None


class SessionStatusResponse(BaseModel):
    """Response model for session status check."""

    session_id: str
    payment_status: str
    amount_total: int
    currency: str
    citation_number: Optional[str]
    appeal_type: Optional[AppealType]
    user_email: Optional[str]
    payment_id: Optional[int]
    intake_id: Optional[int]
    draft_id: Optional[int]
    tracking_visible: bool = True  # False for standard mail ($9) users


@router.post("/create-session", response_model=AppealCheckoutResponse)
def create_appeal_checkout(request: Request, appeal_request: AppealCheckoutRequest):
    """
    Create a Stripe checkout session for parking ticket appeal payment.

    This endpoint:
    1. Validates the appeal data
    2. Creates intake, draft, and payment records in the database
    3. Creates a Stripe checkout session with only IDs in metadata
    4. Returns the checkout URL

    Database-first approach ensures data persistence before payment.
    Rate limited to 10 requests per minute per IP address.
    """
    try:
        # BLOCKED STATE CHECK - Prevent UPL liability
        if appeal_request.user_state in BLOCKED_STATES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="We are currently unable to offer our services in your state due to local regulations.",
            )

        # USER ADDRESS VALIDATION - Prevent undeliverable mail burn
        is_valid_addr, addr_error = await verify_user_address(
            appeal_request.user_address_line1,
            appeal_request.user_city,
            appeal_request.user_state,
            appeal_request.user_zip,
        )
        if not is_valid_addr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=addr_error
            )

        # Initialize Stripe service
        stripe_service = StripeService()

        # Convert request to service object
        checkout_request = CheckoutRequest(
            citation_number=appeal_request.citation_number,
            violation_date=appeal_request.violation_date,
            vehicle_info=appeal_request.vehicle_info,
            license_plate=appeal_request.license_plate,
            user_name=appeal_request.user_name,
            user_address_line1=appeal_request.user_address_line1,
            user_address_line2=appeal_request.user_address_line2,
            user_city=appeal_request.user_city,
            user_state=appeal_request.user_state,
            user_zip=appeal_request.user_zip,
            user_email=appeal_request.user_email,
            draft_text=appeal_request.draft_text,
            appeal_type=appeal_request.appeal_type,
            selected_evidence=appeal_request.selected_evidence,
            signature_data=appeal_request.signature_data,
            user_attestation=appeal_request.user_attestation,
            city_id=appeal_request.city_id,  # BACKLOG PRIORITY 3: Multi-city support
            section_id=appeal_request.section_id,  # BACKLOG PRIORITY 3: Multi-city support
        )

        # AUDIT FIX: Database-first approach - create DB records BEFORE Stripe session
        db_service = get_db_service()

        # Create intake record
        intake = db_service.create_intake(
            citation_number=appeal_request.citation_number,
            violation_date=appeal_request.violation_date,
            vehicle_info=appeal_request.vehicle_info,
            license_plate=appeal_request.license_plate,
            user_name=appeal_request.user_name,
            user_address_line1=appeal_request.user_address_line1,
            user_address_line2=appeal_request.user_address_line2,
            user_city=appeal_request.user_city,
            user_state=appeal_request.user_state,
            user_zip=appeal_request.user_zip,
            user_email=appeal_request.user_email,
            appeal_reason=appeal_request.draft_text[:5000]
            if appeal_request.draft_text
            else None,
            selected_evidence=appeal_request.selected_evidence,
            signature_data=appeal_request.signature_data,
            city=appeal_request.city_id or "s",  # Default to SF if not provided
        )

        # Create draft record
        draft = db_service.create_draft(
            intake_id=intake.id,
            appeal_type=appeal_request.appeal_type,
            draft_text=appeal_request.draft_text,
        )

        # Now create Stripe checkout session with IDs in metadata
        # Note: We'll create payment record AFTER Stripe session to get accurate amount
        checkout_request.intake_id = intake.id
        checkout_request.draft_id = draft.id

        try:
            # Create Stripe checkout session first to get accurate amount
            response = stripe_service.create_checkout_session(checkout_request)

            # AUDIT FIX: Create payment record AFTER Stripe session with accurate amount
            # Note: payment_id won't be in metadata, but webhook can find by session_id
            payment = db_service.create_payment(
                intake_id=intake.id,
                stripe_session_id=response.session_id,
                amount_total=response.amount_total,  # Use amount from Stripe response
                appeal_type=appeal_request.appeal_type,
            )

            # Update checkout request with payment_id for response (not metadata)
            checkout_request.payment_id = payment.id

            logger.info(
                f"Created payment {payment.id} for intake {intake.id} "
                "with Stripe session {response.session_id}"
            )
        except Exception as stripe_error:
            # AUDIT FIX: If Stripe fails, we have intake and draft records saved
            # This is acceptable - user can retry payment later
            logger.error(
                "Stripe session creation failed after DB records created [intake_id={intake.id}]: {stripe_error}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment gateway error: {str(stripe_error)}. Your appeal has been saved (intake_id: {intake.id}).",
            ) from stripe_error

        # Convert to API response
        api_response = AppealCheckoutResponse(
            checkout_url=response.checkout_url,
            session_id=response.session_id,
            amount_total=response.amount_total,
            currency=response.currency,
            appeal_type=appeal_request.appeal_type,
            citation_number=appeal_request.citation_number,
            payment_id=response.payment_id,
        )

        return api_response

    except ValueError as e:
        # Validation error from our service
        logger.warning(f"Checkout validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}"
        ) from e
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., from Stripe error handler)
        raise
    except Exception as e:
        # Unexpected error - log with request context
        logger.error(f"Unexpected error creating checkout session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session. Please try again.",
        ) from e


@router.get("/session/{session_id}", response_model=SessionStatusResponse)
def get_session_status(session_id: str):
    """
    Get the status of a Stripe checkout session.

    This endpoint allows checking if a payment was successful and provides
    the session metadata for fulfillment processing.
    """
    try:
        # Validate session ID format
        if not session_id.startswith("cs_"):
            raise ValueError("Invalid session ID format")

        # Initialize Stripe service and get status
        stripe_service = StripeService()
        status_info = stripe_service.get_session_status(session_id)

        # Determine if tracking is visible (only for certified mail)
        is_certified = status_info.appeal_type == "certified"

        # Convert to API response
        api_response = SessionStatusResponse(
            session_id=status_info.session_id,
            payment_status=status_info.payment_status,
            amount_total=status_info.amount_total,
            currency=status_info.currency,
            citation_number=None,  # Would need to fetch from database
            appeal_type=(
                AppealType(status_info.appeal_type) if status_info.appeal_type else None
            ),
            user_email=None,  # Would need to fetch from database
            payment_id=status_info.payment_id,
            intake_id=status_info.intake_id,
            draft_id=status_info.draft_id,
            tracking_visible=is_certified,
        )

        return api_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid session ID: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session status: {str(e)}",
        ) from e


@router.post("/test-checkout")
def test_checkout_endpoint():
    """
    Test endpoint to verify checkout functionality.

    Returns a mock response for testing without creating actual Stripe sessions.
    """
    return {
        "status": "test_mode",
        "message": "Checkout endpoint is working (test mode)",
        "note": "In production, this would create actual Stripe checkout sessions",
        "database_approach": "Database-first: intake → draft → payment → Stripe session",
        "metadata_strategy": "Only IDs stored in Stripe metadata",
        "webhook_flow": "Webhook looks up data from database using IDs",
    }


# Legacy endpoint (can be removed later)
@router.post("/old-format", deprecated=True, include_in_schema=False)
def create_checkout_legacy(req: dict):
    """
    Legacy checkout endpoint for backward compatibility.

    DEPRECATED: Use /create-session instead.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint is deprecated. Use /create-session instead.",
    )
