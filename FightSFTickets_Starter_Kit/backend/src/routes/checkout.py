"""
Checkout Routes for FightSFTickets.com (Database-First Approach)

Handles payment session creation and status checking for appeal processing.
Uses database for persistent storage before creating Stripe checkout sessions.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator

from ..models import AppealType, PaymentStatus
from ..services.database import get_db_service
from ..services.stripe_service import (
    CheckoutRequest,
    CheckoutResponse,
    SessionStatus,
    StripeService,
)

router = APIRouter()


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
    photos: Optional[List[str]] = Field(
        None,
        description="List of base64 encoded photos",
    )
    signature_data: Optional[str] = Field(
        None,
        examples=["data:image/png;base64,iVBORw0KGgoAAA..."],
        description="Base64-encoded signature image",
    )

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


@router.post("/create-session", response_model=AppealCheckoutResponse)
def create_appeal_checkout(request: AppealCheckoutRequest):
    """
    Create a Stripe checkout session for parking ticket appeal payment.

    This endpoint:
    1. Validates the appeal data
    2. Creates intake, draft, and payment records in the database
    3. Creates a Stripe checkout session with only IDs in metadata
    4. Returns the checkout URL

    Database-first approach ensures data persistence before payment.
    """
    try:
        # Initialize Services
        stripe_service = StripeService()
        db_service = get_db_service()

        # 1. Save Intake to Database
        # Use photos if provided, otherwise fallback to selected_evidence
        evidence_data = request.photos if request.photos else request.selected_evidence

        intake = db_service.create_intake(
            citation_number=request.citation_number,
            violation_date=request.violation_date,
            vehicle_info=request.vehicle_info,
            license_plate=request.license_plate,
            user_name=request.user_name,
            user_address_line1=request.user_address_line1,
            user_address_line2=request.user_address_line2,
            user_city=request.user_city,
            user_state=request.user_state,
            user_zip=request.user_zip,
            user_email=request.user_email,
            appeal_reason=request.draft_text, # Using draft text as reason or separate? Usually draft text is the final output.
            selected_evidence=evidence_data,
            signature_data=request.signature_data,
            status="draft"
        )

        # 2. Save Draft to Database
        draft = db_service.create_draft(
            intake_id=intake.id,
            draft_text=request.draft_text,
            appeal_type=request.appeal_type,
            is_final=True # Assuming checkout means final
        )

        # 3. Create Stripe Checkout Session
        checkout_request = CheckoutRequest(
            citation_number=request.citation_number,
            violation_date=request.violation_date,
            vehicle_info=request.vehicle_info,
            license_plate=request.license_plate,
            user_name=request.user_name,
            user_address_line1=request.user_address_line1,
            user_address_line2=request.user_address_line2,
            user_city=request.user_city,
            user_state=request.user_state,
            user_zip=request.user_zip,
            user_email=request.user_email,
            draft_text=request.draft_text,
            appeal_type=request.appeal_type,
            selected_evidence=request.selected_evidence,
            signature_data=request.signature_data,
        )

        response = stripe_service.create_checkout_session(checkout_request)

        # 4. Create Payment Record
        payment = db_service.create_payment(
            intake_id=intake.id,
            stripe_session_id=response.session_id,
            amount_total=response.amount_total,
            appeal_type=request.appeal_type,
            status=PaymentStatus.PENDING,
            currency=response.currency
        )

        # Convert to API response
        api_response = AppealCheckoutResponse(
            checkout_url=response.checkout_url,
            session_id=response.session_id,
            amount_total=response.amount_total,
            currency=response.currency,
            appeal_type=request.appeal_type,
            citation_number=request.citation_number,
            payment_id=payment.id,
        )

        return api_response

    except ValueError as e:
        # Validation error from our service
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        # Unexpected error
        import traceback
        print(f"Checkout error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


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

        # Initialize Services
        stripe_service = StripeService()
        db_service = get_db_service()

        # Get status from Stripe
        status_info = stripe_service.get_session_status(session_id)

        # Get data from DB
        payment = db_service.get_payment_by_session(session_id)

        intake_id = None
        draft_id = None

        if payment:
            # Update payment status if changed
            if status_info.payment_status == "paid" and payment.status != PaymentStatus.PAID:
                 db_service.update_payment_status(session_id, PaymentStatus.PAID, paid_at=datetime.utcnow())

            intake_id = payment.intake_id
            # Try to get draft ID associated with intake
            intake = db_service.get_intake_with_drafts_and_payments(payment.intake_id)
            if intake and intake.drafts:
                # Get the latest draft
                draft_id = intake.drafts[-1].id

        # Convert to API response
        api_response = SessionStatusResponse(
            session_id=status_info.session_id,
            payment_status=status_info.payment_status,
            amount_total=status_info.amount_total,
            currency=status_info.currency,
            citation_number=status_info.citation_number,
            appeal_type=(
                AppealType(status_info.appeal_type) if status_info.appeal_type else None
            ),
            user_email=status_info.user_email,
            payment_id=payment.id if payment else None,
            intake_id=intake_id,
            draft_id=draft_id,
        )

        return api_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid session ID: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session status: {str(e)}",
        )


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
