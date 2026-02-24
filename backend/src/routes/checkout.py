"""
Checkout Routes for Fight City Tickets.com (Database-First Approach)

Handles payment session creation and status checking for appeal processing.
Uses database for persistent storage before creating Stripe checkout sessions.

Civil Shield Compliance: Includes Clerical ID and compliance metadata.
"""

import hashlib
import logging
import os
import secrets
from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import text

from ..config import settings
from ..middleware.rate_limit import limiter
from ..models import Payment, PaymentStatus
from ..services.database import get_db_service
from ..services.stripe_service import StripeService

# Initialize logger
logger = logging.getLogger(__name__)

# States where service is blocked due to UPL regulations
# Can be overridden via BLOCKED_STATES environment variable (comma-separated)
BLOCKED_STATES = os.getenv(
    "BLOCKED_STATES", "TX,NC,NJ,WA"
).split(",") if os.getenv("BLOCKED_STATES") else ["TX", "NC", "NJ", "WA"]

# Compliance version for document tracking
COMPLIANCE_VERSION = "civil_shield_v1"
CLERICAL_ENGINE_VERSION = "2.1.0"

# Create router
router = APIRouter()


def generate_clerical_id(citation_number: str) -> str:
    """
    Generate a unique Clerical ID for compliance tracking.

    Format: ND-XXXX-XXXX where X is alphanumeric
    Uses citation number and timestamp for uniqueness.

    Args:
        citation_number: The citation number to base the ID on

    Returns:
        str: Unique Clerical ID (e.g., ND-A1B2-C3D4)
    """
    timestamp = datetime.now().isoformat()
    random_suffix = secrets.token_hex(4).upper()

    # Create hash from citation + timestamp
    hash_input = f"{citation_number}-{timestamp}-{random_suffix}"
    hash_output = hashlib.sha256(hash_input.encode()).hexdigest()

    # Extract 8 characters for the middle portion
    middle = hash_output[:8].upper()

    # Generate first portion from citation
    prefix = "ND"

    return f"{prefix}-{middle[:4]}-{middle[4:8]}"


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
            logger.error(f"Lob address verification returned {resp.status_code}")
            return (
                False,
                "Address verification service is temporarily unavailable. Please try again later.",
            )

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
        logger.error(f"Address verification API error: {e}")
        return (
            False,
            "Address verification service is temporarily unavailable. Please try again later.",
        )


class AppealCheckoutRequest(BaseModel):
    """Request model for creating appeal checkout session"""

    citation_number: str = Field(..., min_length=3, max_length=50)
    city_id: str = Field(..., min_length=2, max_length=100)
    section_id: Optional[str] = None
    user_email: Optional[EmailStr] = None  # Optional email for intake creation
    user_attestation: bool = Field(..., description="User must acknowledge terms")

    @validator("city_id")
    def validate_city_id(cls, v):
        """Validate city_id format"""
        if not v or len(v) < 2:
            raise ValueError("Invalid city ID")
        return v

    @validator("section_id", pre=True, always=True)
    def validate_section_id(cls, v):
        """Validate section_id format if provided"""
        if v is not None and not isinstance(v, str):
            raise ValueError("Section ID must be a string")
        return v

    @validator("user_attestation")
    def validate_attestation(cls, v):
        """Validate user attestation - must be True"""
        if not v:
            raise ValueError("User must acknowledge the terms")
        return v


class AppealCheckoutResponse(BaseModel):
    """Response model for appeal checkout session"""

    checkout_url: str
    session_id: str
    amount: int
    clerical_id: str


class SessionStatusResponse(BaseModel):
    """Response model for session status"""

    status: str
    payment_status: str
    mailing_status: str
    tracking_number: Optional[str] = None
    expected_delivery: Optional[str] = None
    clerical_id: Optional[str] = None


@router.post("/create-appeal-checkout", response_model=AppealCheckoutResponse)
@limiter.limit("10/minute")
async def create_appeal_checkout(request: Request, data: AppealCheckoutRequest):
    """
    Create a Stripe checkout session for appeal processing.

    This endpoint:
    1. Validates the citation and city
    2. Creates a database record (Intake)
    3. Generates a unique Clerical ID for compliance tracking
    4. Creates a Stripe checkout session with compliance metadata
    5. Returns the checkout URL and Clerical ID

    Civil Shield Compliance:
    - Each submission gets a unique Clerical ID
    - Metadata includes compliance_version and clerical_id
    - Enables audit trail for procedural compliance
    """
    # Import here to avoid circular imports
    from ..services.citation import CitationValidator

    # Step 1: Validate city_id and get state
    city_id = data.city_id
    if "-" not in city_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid city ID format",
        )
    state = city_id.split("-")[1].upper()

    # Step 2: Check if service is blocked in this state (UPL compliance)
    if state in BLOCKED_STATES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="We cannot process appeals for tickets in this state due to legal restrictions.",
        )

    # Step 3: Validate citation format
    validation_result = CitationValidator.validate_citation(
        data.citation_number, city_id=city_id
    )

    if not validation_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_result.error_message
            or "Invalid citation number for this city",
        )

    # Step 4: Generate Clerical ID for compliance tracking
    clerical_id = generate_clerical_id(data.citation_number.upper())
    logger.info(
        f"Generated Clerical ID: {clerical_id} for citation: {data.citation_number.upper()}"
    )

    # Step 5: Create database record (Intake) - happens BEFORE payment
    db_service = get_db_service()
    intake_id = None

    try:
        with db_service.get_session() as session:
            # Check for existing intake with this citation
            existing_intake = db_service.get_intake_by_citation(data.citation_number.upper())
            
            # If intake exists, check for existing paid payments
            if existing_intake:
                existing_payments = (
                    session.query(Payment)
                    .filter(
                        Payment.intake_id == existing_intake.id,
                        Payment.status == PaymentStatus.PAID
                    )
                    .all()
                )
                if existing_payments:
                    logger.warning(
                        f"Citation {data.citation_number.upper()} already has a paid payment"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A payment already exists for this citation number. Please check your payment status.",
                    )
            # Upsert intake record with Clerical ID
            # Use the intakes table from the new database schema
            result = session.execute(
                text("""
                INSERT INTO intakes (
                    citation_number, city, status,
                    user_name, user_email,
                    clerical_id, created_at, updated_at
                )
                VALUES (
                    :citation_number, :city, 'draft',
                    :user_name, :user_email,
                    :clerical_id, NOW(), NOW()
                )
                ON CONFLICT (citation_number) DO UPDATE SET
                    city = EXCLUDED.city,
                    clerical_id = EXCLUDED.clerical_id,
                    updated_at = NOW()
                RETURNING id
                """),
                {
                    "citation_number": data.citation_number.upper(),
                    "city": city_id,
                    "user_name": "Pending",  # Will be updated when user completes form
                    "user_email": data.user_email or "pending@example.com",
                    "clerical_id": clerical_id,
                },
            )
            intake_row = result.fetchone()
            intake_id = intake_row[0] if intake_row else None

            if not intake_id:
                # Try to fetch existing
                existing = session.execute(
                    text("SELECT id, clerical_id FROM intakes WHERE citation_number = :citation"),
                    {"citation": data.citation_number.upper()},
                )
                existing_row = existing.fetchone()
                if existing_row:
                    intake_id = existing_row[0]
                    # Update clerical_id if not set
                    if existing_row[1] is None:
                        session.execute(
                            text("UPDATE intakes SET clerical_id = :clerical_id WHERE id = :id"),
                            {
                                "clerical_id": clerical_id,
                                "id": intake_id,
                            },
                        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Database error creating intake: {e}")
        intake_id = None

    # Step 6: Create Stripe checkout session with compliance metadata
    try:
        # Map city_id to display name
        city_names = {
            "sf": "San Francisco",
            "us-ca-san_francisco": "San Francisco",
            "la": "Los Angeles",
            "us-ca-los_angeles": "Los Angeles",
            "nyc": "New York City",
            "us-ny-new_york": "New York City",
            "us-ca-san_diego": "San Diego",
            "us-az-phoenix": "Phoenix",
            "us-co-denver": "Denver",
            "us-il-chicago": "Chicago",
            "us-or-portland": "Portland",
            "us-pa-philadelphia": "Philadelphia",
            "us-tx-dallas": "Dallas",
            "us-tx-houston": "Houston",
            "us-ut-salt_lake_city": "Salt Lake City",
            "us-wa-seattle": "Seattle",
        }

        display_city = city_names.get(
            city_id, city_id.replace("us-", "").replace("-", " ").title()
        )

        stripe_svc = StripeService()

        # Create checkout session with comprehensive metadata
        # Use frontend_url if configured, otherwise derive from app_url
        frontend_base = getattr(settings, 'frontend_url', None) or f"{settings.app_url}"
        checkout_session = await stripe_svc.create_session(
            amount=settings.fightcity_service_fee,
            currency="usd",
            success_url=f"{frontend_base}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_base}/appeal/checkout",
            metadata={
                "citation_number": data.citation_number.upper(),
                "city_id": city_id,
                "intake_id": str(intake_id) if intake_id else "",
                "service_type": "appeal_processing",
                "clerical_id": clerical_id,
                "compliance_version": COMPLIANCE_VERSION,
                "clerical_engine_version": CLERICAL_ENGINE_VERSION,
                "document_type": "PROCEDURAL_COMPLIANCE_SUBMISSION",
            },
            customer_email=settings.service_email,
            payment_description=f"Procedural Compliance Submission - {display_city} Ticket #{data.citation_number.upper()} | Clerical ID: {clerical_id}",
        )

        # Update database with Stripe session ID in payments table
        # This will be done when payment is created via webhook
        if intake_id:
            logger.info(f"Checkout session {checkout_session['id']} created for intake {intake_id}")

        logger.info(
            f"Checkout session created: {checkout_session['id']} with Clerical ID: {clerical_id}"
        )

        return AppealCheckoutResponse(
            checkout_url=checkout_session["url"],
            session_id=checkout_session["id"],
            amount=settings.fightcity_service_fee,
            clerical_id=clerical_id,
        )

    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.get("/session-status", response_model=SessionStatusResponse)
@limiter.limit("30/minute")
async def get_session_status(request: Request, session_id: str):
    """
    Check the status of a Stripe checkout session and update database accordingly.

    This endpoint:
    1. Checks the Stripe session status
    2. Updates the database record
    3. Returns the current status including Clerical ID
    """
    try:
        # Get Stripe session
        stripe_svc = StripeService()
        session = stripe_svc.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        # Determine payment status
        payment_status = "pending"
        mailing_status = "pending"
        tracking_number = None
        expected_delivery = None
        clerical_id = None

        if session["payment_status"] == "paid":
            payment_status = "paid"

            # Check payment status from payments table
            db_service = get_db_service()
            with db_service.get_session() as db:
                # Use parameterized query to prevent SQL injection
                result = db.execute(
                    text("SELECT status, lob_tracking_id FROM payments WHERE stripe_session_id = :session_id"),
                    {"session_id": session_id},
                )
                row = result.fetchone()

                if row:
                    mailing_status = "fulfilled" if row[0] == "paid" else "pending"
                    tracking_number = row[1]
                    # Get clerical_id from intake via payment relationship
                    from ..models import Intake
                    payment = db.query(Payment).filter(Payment.stripe_session_id == session_id).first()
                    if payment and payment.intake_id:
                        intake = db.query(Intake).filter(Intake.id == payment.intake_id).first()
                        if intake:
                            clerical_id = intake.clerical_id

        return SessionStatusResponse(
            status=session["status"],
            payment_status=payment_status,
            mailing_status=mailing_status,
            tracking_number=tracking_number,
            expected_delivery=expected_delivery,
            clerical_id=clerical_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check session status",
        )


@router.get("/test-checkout")
async def test_checkout_endpoint():
    """Test endpoint to verify checkout routes are working"""
    return {
        "status": "ok",
        "message": "Checkout endpoint is working",
        "stripe_configured": bool(settings.stripe_secret_key),
        "clerical_engine_version": CLERICAL_ENGINE_VERSION,
        "compliance_version": COMPLIANCE_VERSION,
    }


def create_checkout_legacy(
    citation_number: str, city_id: str, section_id: str | None = None
) -> dict:
    """
    Legacy function for creating checkout sessions without FastAPI dependency.

    Returns:
        dict: Checkout session data with 'url', 'id', and 'clerical_id' keys
    """
    # Create minimal request data
    data = AppealCheckoutRequest(
        citation_number=citation_number,
        city_id=city_id,
        section_id=section_id,
        user_attestation=True,
    )

    # Create a mock request object
    class MockRequest:
        def __init__(self):
            self.state = type("obj", (object,), {})()

    # Run the async function
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(create_appeal_checkout(MockRequest(), data))
        return {
            "url": result.checkout_url,
            "id": result.session_id,
            "amount": result.amount,
            "clerical_id": result.clerical_id,
        }
    finally:
        loop.close()
