"""
Admin Routes for Fight City Tickets.com

Provides endpoints for monitoring server status, viewing logs, and accessing recent activity.
Protected by admin secret key header.
"""

import hashlib
import json
import logging
import os
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from ..models import Draft, Intake, Payment, PaymentStatus
from ..services.database import get_db_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter - shared instance from app.py
limiter = Limiter(key_func=get_remote_address)

# Audit logging for admin actions
ADMIN_AUDIT_LOG = "admin_audit.log"


def log_admin_action(action: str, admin_id: str, request: Request, details: dict[str, Any] = None):
    """
    Log admin actions for security auditing.

    Args:
        action: The admin action being performed
        admin_id: Identifier for the admin (secret or IP)
        request: The original request
        details: Additional details to log
    """
    from datetime import datetime

    # Securely hash the admin_id so we don't log secrets
    hashed_id = hashlib.sha256(admin_id.encode()).hexdigest()[:8]

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "admin_id": f"admin-{hashed_id}",
        "ip": request.client.host if request.client else "unknown",
        "path": request.url.path,
        "method": request.method,
        "details": details or {},
    }

    try:
        with open(ADMIN_AUDIT_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write admin audit log: {e}")

# Basic admin security (header check)
ADMIN_SECRET_HEADER = "X-Admin-Secret"


def verify_admin_secret(x_admin_secret: str = Header(...)):
    """
    Verify the admin secret header.
    Requires explicit ADMIN_SECRET environment variable.

    Also logs all admin access attempts for security auditing.
    """
    admin_secret = os.getenv("ADMIN_SECRET")

    if not admin_secret:
        logger.error(
            "ADMIN_SECRET environment variable not set - admin routes disabled"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured. Set ADMIN_SECRET environment variable.",
        )

    import secrets
    if not secrets.compare_digest(x_admin_secret.encode(), admin_secret.encode()):
        client_ip = os.getenv('REMOTE_ADDR', 'unknown')
        logger.warning(
            f"Failed admin access attempt - Invalid admin secret provided. "
            f"IP: {client_ip}"
        )
        # Log failed attempt
        try:
            with open(ADMIN_AUDIT_LOG, "a") as f:
                from datetime import datetime
                f.write(json.dumps({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "action": "auth_failure",
                    "ip": client_ip,
                    "status": "failed",
                }) + "\n")
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret",
        )

    logger.info(f"Admin access granted - IP: {os.getenv('REMOTE_ADDR', 'unknown')}")
    return x_admin_secret


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


# Endpoints


@router.get("/stats", response_model=SystemStats)
@limiter.limit("5/minute")
def get_system_stats(
    request: Request, admin_secret: str = Depends(verify_admin_secret)
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
    request: Request, limit: int = 50, admin_secret: str = Depends(verify_admin_secret)
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
    request: Request, intake_id: int, admin_secret: str = Depends(verify_admin_secret)
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
    request: Request, lines: int = 100, admin_secret: str = Depends(verify_admin_secret)
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
