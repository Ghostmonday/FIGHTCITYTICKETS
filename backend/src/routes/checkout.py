"""
Checkout Routes for FightCityTickets.com (Database-First Approach)

Handles payment session creation and status checking for appeal processing.
Uses database for persistent storage before creating Stripe checkout sessions.
"""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..services.database import get_db_service
from ..services.stripe_service import StripeService

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# States where service is blocked due to UPL regulations
BLOCKED_STATES = ["TX", "NC", "NJ", "WA"]

# Create router
router = APIRouter()


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


class AppealCheckoutRequest(BaseModel):
    """Request model for creating appeal checkout session"""

    citation_number: str = Field(..., min_length=3, max_length=50)
    city_id: str = Field(..., min_length=2, max_length=100)
    section_id: Optional[str] = None
    user_attestation: bool = False

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
        """Validate user attestation"""
        if not v:
            raise ValueError("User must acknowledge the terms")
        return v


class AppealCheckoutResponse(BaseModel):
    """Response model for appeal checkout session"""

    checkout_url: str
    session_id: str
    amount: int


class SessionStatusResponse(BaseModel):
    """Response model for session status"""

    status: str
    payment_status: str
    mailing_status: str
    tracking_number: Optional[str] = None
    expected_delivery: Optional[str] = None


@router.post("/create-appeal-checkout", response_model=AppealCheckoutResponse)
@limiter.limit("10/minute")
async def create_appeal_checkout(request: Request, data: AppealCheckoutRequest):
    """
    Create a Stripe checkout session for appeal processing.

    This endpoint:
    1. Validates the citation and city
    2. Creates a database record (Intake)
    3. Creates a Stripe checkout session
    4. Returns the checkout URL

    The database record ensures we have the appeal data even if
    the user doesn't complete payment.
    """
    # Import here to avoid circular imports
    from ..services.citation import validate_citation

    # Step 1: Validate city_id and get state
    city_id = data.city_id
    state = city_id.split("-")[1] if "-" in city_id else None

    # Step 2: Check if service is blocked in this state (UPL compliance)
    if state in BLOCKED_STATES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="We cannot process appeals for tickets in this state due to legal restrictions.",
        )

    # Step 3: Validate citation format
    is_valid_citation, validation_error = validate_citation(
        data.citation_number, city_id
    )

    if not is_valid_citation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_error or "Invalid citation number for this city",
        )

    # Step 4: Create database record (Intake) - happens BEFORE payment
    db_service = get_db_service()
    intake_id = None

    try:
        with db_service.get_session() as session:
            # Upsert intake record
            result = session.execute(
                """
                INSERT INTO appeals (
                    citation_number, city_id, section_id, status,
                    payment_status, mailing_status, amount_paid,
                    created_at, updated_at
                )
                VALUES (
                    :citation_number, :city_id, :section_id, 'draft',
                    'pending', 'pending', 0,
                    NOW(), NOW()
                )
                ON CONFLICT (citation_number) DO UPDATE SET
                    city_id = EXCLUDED.city_id,
                    section_id = EXCLUDED.section_id,
                    updated_at = NOW()
                RETURNING id
                """,
                {
                    "citation_number": data.citation_number.upper(),
                    "city_id": city_id,
                    "section_id": data.section_id,
                },
            )
            intake_row = result.fetchone()
            intake_id = intake_row[0] if intake_row else None

            if not intake_id:
                # Try to fetch existing
                existing = session.execute(
                    "SELECT id FROM appeals WHERE citation_number = :citation",
                    {"citation": data.citation_number.upper()},
                )
                existing_row = existing.fetchone()
                intake_id = existing_row[0] if existing_row else None

    except Exception as e:
        logger.error(f"Database error creating intake: {e}")
        intake_id = None

    # Step 5: Create Stripe checkout session
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
        checkout_session = stripe_svc.create_checkout_session(
            amount=settings.fightcity_service_fee,
            currency="usd",
            success_url=f"{settings.frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/appeal/checkout",
            metadata={
                "citation_number": data.citation_number.upper(),
                "city_id": city_id,
                "intake_id": str(intake_id) if intake_id else "",
                "service_type": "appeal_processing",
            },
            customer_email=settings.service_email,
            payment_description=f"Appeal processing for {display_city} ticket #{data.citation_number.upper()}",
        )

        # Update database with Stripe session ID
        if intake_id:
            try:
                with db_service.get_session() as session:
                    session.execute(
                        "UPDATE appeals SET stripe_session_id = :session_id, updated_at = NOW() WHERE id = :id",
                        {"session_id": checkout_session["id"], "id": intake_id},
                    )
            except Exception as e:
                logger.warning(f"Failed to update session ID: {e}")

        return AppealCheckoutResponse(
            checkout_url=checkout_session["url"],
            session_id=checkout_session["id"],
            amount=settings.fightcity_service_fee,
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
    3. Returns the current status
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

        if session["payment_status"] == "paid":
            payment_status = "paid"

            # Check if we've already processed mailing
            db_service = get_db_service()
            with db_service.get_session() as db:
                result = db.execute(
                    "SELECT mailing_status, tracking_number FROM appeals WHERE stripe_session_id = :session_id",
                    {"session_id": session_id},
                )
                row = result.fetchone()

                if row:
                    mailing_status = row[0] or "pending"
                    tracking_number = row[1]

        return SessionStatusResponse(
            status=session["status"],
            payment_status=payment_status,
            mailing_status=mailing_status,
            tracking_number=tracking_number,
            expected_delivery=expected_delivery,
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
    }


def create_checkout_legacy(
    citation_number: str, city_id: str, section_id: str | None = None
) -> dict:
    """
    Legacy function for creating checkout sessions without FastAPI dependency.

    Returns:
        dict: Checkout session data with 'url' and 'id' keys
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
        }
    finally:
        loop.close()
