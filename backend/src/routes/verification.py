"""
Email Verification Routes for Fight City Tickets.com

Handles sending and confirming email verification tokens.
"""

import logging
import time
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr

from ..config import settings
from ..models import Intake
from ..services.database import get_db_service
from ..services.email_service import get_email_service
from ..middleware.rate_limit import limiter
from .appeals import verify_appeal_token

logger = logging.getLogger(__name__)

router = APIRouter()

class VerificationRequest(BaseModel):
    """Request model for sending verification email."""
    email: Optional[EmailStr] = None

def create_verification_token(intake_id: int, email: str) -> str:
    """Create a verification token."""
    now = int(time.time())
    payload = {
        "sub": str(intake_id),
        "email": email,
        "iat": now,
        "exp": now + 86400,  # 24 hours expiration
        "type": "email_verification",
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

@router.post("/{intake_id}/send")
@limiter.limit("5/minute")
async def send_verification_email(
    request: Request,
    intake_id: int,
    data: VerificationRequest,
    _auth: None = Depends(verify_appeal_token),
):
    """
    Send verification email to the user.
    Requires existing appeal access token.
    Rate limited to 5 per minute.
    """
    db_service = get_db_service()
    intake = db_service.get_intake(intake_id)

    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intake not found",
        )

    email = data.email or intake.user_email
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required",
        )

    # Generate token
    token = create_verification_token(intake.id, email)

    # Construct verification link
    # Using api_url from settings
    # Ensure api_url does not have trailing slash
    api_url = settings.api_url.rstrip('/')
    # Note: If mounted at /verification, the path is /verification/confirm
    verification_link = f"{api_url}/verification/confirm?token={token}"

    # Send email
    email_service = get_email_service()
    success = await email_service.send_verification_email(email, verification_link)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email",
        )

    return {"message": "Verification email sent"}

@router.get("/confirm")
async def confirm_verification(token: str = Query(...)):
    """
    Confirm email verification.
    Updates intake status and redirects to frontend.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

        if payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type",
            )

        intake_id = int(payload.get("sub"))
        email = payload.get("email")

        db_service = get_db_service()

        with db_service.get_session() as session:
            intake = session.query(Intake).filter(Intake.id == intake_id).first()

            if not intake:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Intake not found",
                )

            # Update verification status
            intake.email_verified = True
            # Also update email if it changed (optional, but good for consistency)
            if email and email != intake.user_email:
                intake.user_email = email

            session.commit()

            logger.info(f"Email verified for intake {intake_id}")

        # Redirect to frontend success page
        # Using app_url from settings
        app_url = settings.app_url.rstrip('/')
        return RedirectResponse(
            url=f"{app_url}/appeal/{intake_id}?verified=true"
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
