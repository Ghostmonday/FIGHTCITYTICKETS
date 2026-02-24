"""
Appeal Storage Routes for Fight City Tickets.com

Handles saving and loading appeal state from the database.
Enables persistence across sessions and devices.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, validator

from ..config import settings
from ..models import Intake
from ..services.database import get_db_service

logger = logging.getLogger(__name__)

router = APIRouter()


def create_access_token(intake_id: int) -> str:
    """Create a stateless access token for an intake."""
    now = int(time.time())
    payload = {
        "sub": str(intake_id),
        "iat": now,
        "exp": now + 86400,  # 24 hours expiration
        "type": "appeal_access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def verify_appeal_token(
    intake_id: int,
    x_appeal_token: Optional[str] = Header(None, alias="X-Appeal-Token"),
    token: Optional[str] = Query(None),
) -> None:
    """
    Verify the appeal access token.
    Accepts token in header (X-Appeal-Token) or query param (token).
    """
    access_token = x_appeal_token or token

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms=["HS256"])
        token_intake_id = int(payload.get("sub"))

        if token_intake_id != intake_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token invalid for this intake",
            )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def validate_appeal_access(
    intake_id: int,
    _auth: None = Depends(verify_appeal_token),
) -> int:
    """
    Dependency to validate access to an intake.
    Returns the intake_id if valid.
    """
    return intake_id


class AppealUpdateRequest(BaseModel):
    """Request model for updating appeal/intake state."""

    citation_number: Optional[str] = None
    violation_date: Optional[str] = None
    vehicle_info: Optional[str] = None
    license_plate: Optional[str] = None
    appeal_reason: Optional[str] = None
    selected_evidence: Optional[list] = None
    signature_data: Optional[str] = None

    # User information
    user_name: Optional[str] = None
    user_address_line1: Optional[str] = None
    user_address_line2: Optional[str] = None
    user_city: Optional[str] = None
    user_state: Optional[str] = None
    user_zip: Optional[str] = None
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None

    # City info
    city: Optional[str] = None
    section_id: Optional[str] = None


class AppealResponse(BaseModel):
    """Response model for appeal data."""

    id: int
    citation_number: str
    violation_date: Optional[str]
    vehicle_info: Optional[str]
    license_plate: Optional[str]
    user_name: Optional[str]
    user_address_line1: Optional[str]
    user_address_line2: Optional[str]
    user_city: Optional[str]
    user_state: Optional[str]
    user_zip: Optional[str]
    user_email: Optional[str]
    appeal_reason: Optional[str]
    selected_evidence: Optional[list]
    signature_data: Optional[str]
    city: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


@router.put("/appeals/{intake_id}")
async def update_appeal(
    intake_id: int,
    data: AppealUpdateRequest,
    _auth: None = Depends(verify_appeal_token),
):
    """
    Update an existing appeal/intake record.

    This endpoint allows the frontend to save progress to the database
    as the user completes the appeal flow.
    """
    db_service = get_db_service()

    try:
        with db_service.get_session() as session:
            # Build update dynamically
            updates = {}
            if data.citation_number:
                updates["citation_number"] = data.citation_number
            if data.violation_date:
                updates["violation_date"] = data.violation_date
            if data.vehicle_info:
                updates["vehicle_info"] = data.vehicle_info
            if data.license_plate:
                updates["license_plate"] = data.license_plate
            if data.appeal_reason:
                updates["appeal_reason"] = data.appeal_reason
            if data.selected_evidence is not None:
                updates["selected_evidence"] = data.selected_evidence
            if data.signature_data is not None:
                updates["signature_data"] = data.signature_data
            if data.user_name:
                updates["user_name"] = data.user_name
            if data.user_address_line1:
                updates["user_address_line1"] = data.user_address_line1
            if data.user_address_line2 is not None:
                updates["user_address_line2"] = data.user_address_line2
            if data.user_city:
                updates["user_city"] = data.user_city
            if data.user_state:
                updates["user_state"] = data.user_state
            if data.user_zip:
                updates["user_zip"] = data.user_zip
            if data.user_email is not None:
                updates["user_email"] = data.user_email
            if data.user_phone is not None:
                updates["user_phone"] = data.user_phone
            if data.city:
                updates["city"] = data.city
            if data.section_id is not None:
                updates["section_id"] = data.section_id

            if not updates:
                return {"message": "No updates provided", "intake_id": intake_id}

            # Whitelist of allowed column names to prevent SQL injection
            ALLOWED_COLUMNS = {
                "citation_number", "violation_date", "vehicle_info", "license_plate",
                "appeal_reason", "selected_evidence", "signature_data", "user_name",
                "user_address_line1", "user_address_line2", "user_city", "user_state",
                "user_zip", "user_email", "user_phone", "city", "section_id", "status",
            }
            # Filter to only allowed columns
            updates = {k: v for k, v in updates.items() if k in ALLOWED_COLUMNS}

            if not updates:
                return {"message": "No valid updates provided", "intake_id": intake_id}

            # Use ORM to update instead of raw SQL to prevent injection
            intake = session.query(Intake).filter(Intake.id == intake_id).first()
            if not intake:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Intake {intake_id} not found",
                )
            
            # Update fields using ORM
            for key, value in updates.items():
                if hasattr(intake, key):
                    setattr(intake, key, value)
            
            # Update timestamp
            intake.updated_at = datetime.now(timezone.utc)
            session.flush()

            logger.info(f"Updated intake {intake_id} with progress data")

            return {
                "message": "Intake updated successfully",
                "intake_id": intake_id,
                "updated_at": intake.updated_at.isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating intake {intake_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update intake: {str(e)}",
        )


@router.get("/appeals/{intake_id}", response_model=AppealResponse)
async def get_appeal(
    intake_id: int = Depends(validate_appeal_access),
):
    """
    Get an appeal/intake record by ID.

    Requires a valid appeal token for the specific intake ID.
    Used to restore user progress from the database.
    Protected against IDOR via verify_appeal_token dependency.
    """
    db_service = get_db_service()

    try:
        intake = db_service.get_intake(intake_id)
        if not intake:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Intake {intake_id} not found",
            )

        return {
            "id": intake.id,
            "citation_number": intake.citation_number,
            "violation_date": intake.violation_date,
            "vehicle_info": intake.vehicle_info,
            "license_plate": intake.license_plate,
            "user_name": intake.user_name,
            "user_address_line1": intake.user_address_line1,
            "user_address_line2": intake.user_address_line2,
            "user_city": intake.user_city,
            "user_state": intake.user_state,
            "user_zip": intake.user_zip,
            "user_email": intake.user_email,
            "appeal_reason": intake.appeal_reason,
            "selected_evidence": intake.selected_evidence,
            "signature_data": intake.signature_data,
            "city": intake.city,
            "status": intake.status,
            "created_at": intake.created_at,
            "updated_at": intake.updated_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving intake {intake_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve intake: {str(e)}",
        )


@router.post("/appeals")
async def create_appeal(data: AppealUpdateRequest):
    """
    Create a new appeal/intake record.

    This is used when the user first starts an appeal.
    """
    db_service = get_db_service()

    try:
        intake = db_service.create_intake(
            citation_number=data.citation_number or "",
            violation_date=data.violation_date,
            vehicle_info=data.vehicle_info,
            license_plate=data.license_plate,
            user_name=data.user_name or "Pending",
            user_address_line1=data.user_address_line1 or "",
            user_address_line2=data.user_address_line2,
            user_city=data.user_city or "",
            user_state=data.user_state or "",
            user_zip=data.user_zip or "",
            user_email=data.user_email,
            user_phone=data.user_phone,
            appeal_reason=data.appeal_reason,
            selected_evidence=data.selected_evidence,
            signature_data=data.signature_data,
            city=data.city or "",
            status="draft",
        )

        logger.info(f"Created new intake {intake.id}")

        # Generate access token
        token = create_access_token(intake.id)

        return {
            "message": "Intake created successfully",
            "intake_id": intake.id,
            "citation_number": intake.citation_number,
            "token": token,
        }

    except Exception as e:
        logger.error(f"Error creating intake: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create intake: {str(e)}",
        )