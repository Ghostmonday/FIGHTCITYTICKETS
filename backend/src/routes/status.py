"""
Appeal Status Lookup Routes

Allows users to check the status of their appeal using email and citation number.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.database import get_db_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class StatusLookupRequest(BaseModel):
    """Request model for appeal status lookup."""

    email: EmailStr = Field(..., description="Email address used for appeal")
    citation_number: str = Field(
        ..., min_length=3, max_length=20, description="Citation number"
    )


class StatusLookupResponse(BaseModel):
    """Response model for appeal status lookup."""

    citation_number: str
    payment_status: str
    mailing_status: str
    tracking_number: Optional[str] = None
    expected_delivery: Optional[str] = None
    amount_total: int
    appeal_type: str
    payment_date: Optional[str] = None
    mailed_date: Optional[str] = None


@router.post("/lookup", response_model=StatusLookupResponse)
@limiter.limit("5/minute")
def lookup_appeal_status(request: Request, lookup_data: StatusLookupRequest):
    """
    Look up appeal status by email and citation number.

    This endpoint allows users to check:
    - Payment status
    - Mailing status
    - Tracking information
    - Appeal details
    """
    try:
        db_service = get_db_service()

        # Find intake by email and citation number
        intake = db_service.get_intake_by_email_and_citation(
            email=lookup_data.email, citation_number=lookup_data.citation_number
        )

        if not intake:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No appeal found with that email and citation number",
            )

        # Get latest payment for this intake
        payment = db_service.get_latest_payment(intake.id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment found for this appeal",
            )

        # Determine mailing status
        mailing_status = "pending"
        if payment.is_fulfilled:
            mailing_status = "mailed"
        elif payment.status.value == "paid":
            mailing_status = "processing"

        # Format dates
        payment_date = None
        if payment.paid_at:
            payment_date = payment.paid_at.isoformat()

        mailed_date = None
        if payment.fulfilled_at:
            mailed_date = payment.fulfilled_at.isoformat()

        # TRACKING GATE: Hide tracking for standard mail users
        is_certified = payment.appeal_type.value == "certified"
        tracking_number = payment.lob_tracking_id if is_certified else None
        expected_delivery = None  # Would need to calculate from Lob API

        return StatusLookupResponse(
            citation_number=intake.citation_number,
            payment_status=payment.status.value,
            mailing_status=mailing_status,
            tracking_number=tracking_number,
            expected_delivery=expected_delivery,
            amount_total=payment.amount_total,
            appeal_type=payment.appeal_type.value,
            payment_date=payment_date,
            mailed_date=mailed_date,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up appeal status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lookup appeal status",
        ) from e
