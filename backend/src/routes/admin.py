"""
Admin Routes for Fight City Tickets.com

Provides endpoints for monitoring server status, viewing logs, and accessing recent activity.
Protected by admin secret key header.
"""

import json
import logging
import os
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from ..auth import (
    ADMIN_COOKIE_NAME,
    create_admin_token,
    get_current_admin,
    log_admin_action,
    verify_admin_secret,
)
from ..models import Draft, Intake, Payment, PaymentStatus
from ..services.database import get_db_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter - shared instance from app.py
limiter = Limiter(key_func=get_remote_address)


# Response Models


class SystemStats(BaseModel):
    total_intakes: int
    total_drafts: int
    total_payments: int
    pending_fulfillments: int
    fulfilled_count: int
    db_status: str


class RecentActivity(BaseModel):
    id: int
    created_at: str
    citation_number: str
    status: str
    payment_status: Optional[str] = None
    amount: Optional[float] = None
    lob_tracking_id: Optional[str] = None


class IntakeDetail(BaseModel):
    id: int
    created_at: str
    citation_number: str
    status: str
    user_name: str
    user_email: Optional[str]
    user_phone: Optional[str]
    user_address: str
    violation_date: Optional[str]
    vehicle_info: Optional[str]
    draft_text: Optional[str]
    payment_status: Optional[str]
    amount_total: Optional[float]
    lob_tracking_id: Optional[str]
    lob_mail_type: Optional[str]
    is_fulfilled: bool


class LogResponse(BaseModel):
    logs: str


class LoginRequest(BaseModel):
    secret: str


# Endpoints


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, response: Response, body: LoginRequest):
    """
    Admin login endpoint.
    Verifies secret and sets httpOnly cookie.
    """
    admin_secret = os.getenv("ADMIN_SECRET")
    if not admin_secret:
        raise HTTPException(status_code=503, detail="Admin auth not configured")

    # Verify secret
    if not secrets.compare_digest(body.secret.encode(), admin_secret.encode()):
        logger.warning(f"Failed login attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(status_code=401, detail="Invalid secret")

    # Generate token
    token = create_admin_token({"sub": "admin"})

    # Set secure cookie
    # Only use secure=True in production to allow local dev/testing
    is_production = os.getenv("APP_ENV", "dev") == "prod"

    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=is_production,
        samesite="strict",
        max_age=43200,  # 12 hours
    )

    return {"message": "Logged in successfully"}


@router.post("/logout")
def logout(response: Response):
    """Logout by clearing the session cookie."""
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return {"message": "Logged out successfully"}


@router.get("/me")
def get_me(admin_secret: str = Depends(get_current_admin)):
    """Check authentication status."""
    return {"authenticated": True, "method": "session" if admin_secret == "admin-session" else "header"}


@router.get("/stats", response_model=SystemStats)
@limiter.limit("5/minute")
def get_system_stats(
    request: Request, admin_secret: str = Depends(get_current_admin)
):
    """
    Get high-level system statistics.
    """
    logger.info("Admin action: get_system_stats")
    log_admin_action("get_system_stats", admin_secret, request)
    db = get_db_service()

    if not db.health_check():
        return SystemStats(
            total_intakes=0,
            total_drafts=0,
            total_payments=0,
            pending_fulfillments=0,
            fulfilled_count=0,
            db_status="disconnected",
        )

    with db.get_session() as session:
        total_intakes = session.query(func.count(Intake.id)).scalar() or 0
        total_drafts = session.query(func.count(Draft.id)).scalar() or 0
        total_payments = session.query(func.count(Payment.id)).scalar() or 0

        pending_fulfillments = (
            session.query(func.count(Payment.id))
            .filter(Payment.status == PaymentStatus.PAID, ~Payment.is_fulfilled)
            .scalar()
            or 0
        )

        fulfilled_count = (
            session.query(func.count(Payment.id)).filter(Payment.is_fulfilled).scalar()
            or 0
        )

    return SystemStats(
        total_intakes=total_intakes,
        total_drafts=total_drafts,
        total_payments=total_payments,
        pending_fulfillments=pending_fulfillments,
        fulfilled_count=fulfilled_count,
        db_status="connected",
    )


@router.get("/activity", response_model=List[RecentActivity])
@limiter.limit("5/minute")
def get_recent_activity(
    request: Request, limit: int = 50, admin_secret: str = Depends(get_current_admin)
):
    """
    Get recent intake activity.
    """
    logger.info(f"Admin action: get_recent_activity (limit={limit})")
    log_admin_action("get_recent_activity", admin_secret, request, {"limit": limit})
    db = get_db_service()

    if not db.health_check():
        raise HTTPException(status_code=503, detail="Database disconnected")

    activity_list = []

    with db.get_session() as session:
        # Use eager loading to prevent N+1 queries
        intakes = (
            session.query(Intake)
            .options(
                selectinload(Intake.payments)
            )
            .order_by(Intake.created_at.desc())
            .limit(limit)
            .all()
        )

        for intake in intakes:
            payment_status = None
            amount = None
            lob_tracking_id = None

            # Access pre-loaded payments (no additional query)
            if intake.payments:
                last_payment = intake.payments[-1]
                payment_status = (
                    last_payment.status.value if last_payment.status else None
                )
                amount = (
                    last_payment.amount_total / 100.0
                    if last_payment.amount_total
                    else None
                )
                lob_tracking_id = last_payment.lob_tracking_id

            activity_list.append(
                RecentActivity(
                    id=intake.id,
                    created_at=intake.created_at.isoformat()
                    if intake.created_at
                    else "",
                    citation_number=intake.citation_number,
                    status=intake.status,
                    payment_status=payment_status,
                    amount=amount,
                    lob_tracking_id=lob_tracking_id,
                )
            )

    return activity_list


@router.get("/intake/{intake_id}", response_model=IntakeDetail)
@limiter.limit("5/minute")
def get_intake_detail(
    request: Request, intake_id: int, admin_secret: str = Depends(get_current_admin)
):
    """
    Get full details for a specific intake.
    """
    logger.info(f"Admin action: get_intake_detail (intake_id={intake_id})")
    log_admin_action("get_intake_detail", admin_secret, request, {"intake_id": intake_id})
    db = get_db_service()

    with db.get_session() as session:
        # Use eager loading to prevent N+1 queries
        intake = (
            session.query(Intake)
            .options(
                joinedload(Intake.drafts),
                selectinload(Intake.payments)
            )
            .filter(Intake.id == intake_id)
            .first()
        )

        if not intake:
            raise HTTPException(status_code=404, detail="Intake not found")

        # Access pre-loaded drafts (no additional query)
        draft_text = None
        if intake.drafts:
            latest_draft = sorted(
                intake.drafts, key=lambda x: x.created_at, reverse=True
            )[0]
            draft_text = latest_draft.draft_text

        # Access pre-loaded payments (no additional query)
        payment_status = None
        amount_total = None
        lob_tracking_id = None
        lob_mail_type = None
        is_fulfilled = False

        if intake.payments:
            latest_payment = sorted(
                intake.payments, key=lambda x: x.created_at, reverse=True
            )[0]
            payment_status = (
                latest_payment.status.value if latest_payment.status else None
            )
            amount_total = (
                latest_payment.amount_total / 100.0
                if latest_payment.amount_total
                else None
            )
            lob_tracking_id = latest_payment.lob_tracking_id
            lob_mail_type = latest_payment.lob_mail_type
            is_fulfilled = latest_payment.is_fulfilled

        # Format address
        address_parts = [intake.user_address_line1]
        if intake.user_address_line2:
            address_parts.append(intake.user_address_line2)
        address_parts.append(
            f"{intake.user_city}, {intake.user_state} {intake.user_zip}"
        )
        full_address = "\n".join(address_parts)

        return IntakeDetail(
            id=intake.id,
            created_at=intake.created_at.isoformat() if intake.created_at else "",
            citation_number=intake.citation_number,
            status=intake.status,
            user_name=intake.user_name,
            user_email=intake.user_email,
            user_phone=intake.user_phone,
            user_address=full_address,
            violation_date=intake.violation_date,
            vehicle_info=intake.vehicle_info,
            draft_text=draft_text,
            payment_status=payment_status,
            amount_total=amount_total,
            lob_tracking_id=lob_tracking_id,
            lob_mail_type=lob_mail_type,
            is_fulfilled=is_fulfilled,
        )


@router.get("/logs", response_model=LogResponse)
@limiter.limit("5/minute")
def get_server_logs(
    request: Request, lines: int = 100, admin_secret: str = Depends(get_current_admin)
):
    """
    Get recent server logs.
    Reads from 'server.log' if it exists.
    """
    logger.info(f"Admin action: get_server_logs (lines={lines})")
    log_admin_action("get_server_logs", admin_secret, request, {"lines": lines})
    log_file = "server.log"

    if not os.path.exists(log_file):
        return LogResponse(
            logs="Log file not found (server.log). Ensure logging is configured to write to file."
        )

    try:
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            return LogResponse(logs="".join(last_lines))
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return LogResponse(logs=f"Error reading log file: {str(e)}")
