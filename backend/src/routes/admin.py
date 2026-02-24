"""
Admin Routes for Fight City Tickets.com

Provides endpoints for monitoring server status, viewing logs, and accessing recent activity.
Protected by admin secret key header.
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from ..config import settings
from ..models import Draft, Intake, Payment, PaymentStatus
from ..services.database import get_db_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter - shared instance from app.py
limiter = Limiter(key_func=get_remote_address)

# Audit logging for admin actions
ADMIN_AUDIT_LOG = "admin_audit.log"
ADMIN_SESSION_COOKIE_NAME = "admin_session"


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


def log_auth_failure(request: Request, reason: str):
    """Log authentication failure to audit log."""
    try:
        client_ip = request.client.host if request.client else "unknown"
        with open(ADMIN_AUDIT_LOG, "a") as f:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "action": "auth_failure",
                "ip": client_ip,
                "status": "failed",
                "reason": reason
            }
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# Basic admin security (header check)
ADMIN_SECRET_HEADER = "X-Admin-Secret"


def check_ip_allowlist(request: Request):
    """
    Check if the request IP is in the allowlist.
    Raises HTTPException(403) if blocked.
    """
    allowed_ips = os.getenv("ADMIN_ALLOWED_IPS", "").strip()
    if allowed_ips:
        client_ip = request.client.host if request.client else None
        if client_ip and client_ip not in allowed_ips.split(","):
            logger.warning(
                f"Failed admin access attempt - IP not in allowlist. "
                f"IP: {client_ip}, Allowed: {allowed_ips}"
            )
            log_auth_failure(request, "IP not allowed")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP not authorized for admin access",
            )


class LoginRequest(BaseModel):
    secret: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for admin session."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=12)
    to_encode.update({"exp": expire})
    
    # Use configured secret key
    key = settings.secret_key
    encoded_jwt = jwt.encode(to_encode, key, algorithm="HS256")
    return encoded_jwt


def verify_admin_secret(request: Request, x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret")):
    """
    Verify the admin secret via session cookie OR header.
    Requires explicit ADMIN_SECRET environment variable.
    
    Security enhancements:
    - Session-based authentication (preferred)
    - Timing-safe secret comparison (fallback)
    - IP allowlist (ADMIN_ALLOWED_IPS env var)
    - Failed attempt logging
    """
    check_ip_allowlist(request)
    admin_secret = os.getenv("ADMIN_SECRET")

    if not admin_secret:
        logger.error(
            "ADMIN_SECRET environment variable not set - admin routes disabled"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured. Set ADMIN_SECRET environment variable.",
        )

    # 1. Check for valid session cookie
    session_cookie = request.cookies.get(ADMIN_SESSION_COOKIE_NAME)
    if session_cookie:
        try:
            # Verify JWT
            key = settings.secret_key
            payload = jwt.decode(session_cookie, key, algorithms=["HS256"])
            if payload.get("sub") == "admin":
                # Valid session
                return "admin-session"
        except jwt.PyJWTError as e:
            logger.warning(f"Invalid admin session cookie: {e}")
            log_auth_failure(request, f"Invalid cookie: {str(e)}")
            # Continue to check header
            pass

    # 2. Fallback: Check Header
    if x_admin_secret:
        import secrets
        if secrets.compare_digest(x_admin_secret.encode(), admin_secret.encode()):
            # Valid header - Check IP allowlist
            allowed_ips = os.getenv("ADMIN_ALLOWED_IPS", "").strip()
            if allowed_ips:
                client_ip = request.client.host if request.client else None
                if client_ip and client_ip not in allowed_ips.split(","):
                    logger.warning(
                        f"Failed admin access attempt - IP not in allowlist. "
                        f"IP: {client_ip}, Allowed: {allowed_ips}"
                    )
                    log_auth_failure(request, "IP not allowed")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="IP not authorized for admin access",
                    )
            return x_admin_secret
        else:
            # Header present but invalid
            client_ip = request.client.host if request.client else "unknown"
            logger.warning(
                f"Failed admin access attempt - Invalid admin secret provided. "
                f"IP: {client_ip}"
            )
            log_auth_failure(request, "Invalid secret (header)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin secret",
            )

    # 3. Neither cookie nor header valid
    log_auth_failure(request, "Missing credentials")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required (Header or Cookie)",
    )


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


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, login_data: LoginRequest):
    """
    Admin login endpoint.
    Exchanges admin secret for a secure session cookie.
    """
    check_ip_allowlist(request)
    admin_secret = os.getenv("ADMIN_SECRET")
    if not admin_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured.",
        )

    import secrets
    if not secrets.compare_digest(login_data.secret.encode(), admin_secret.encode()):
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"Failed admin login attempt - IP: {client_ip}")
        log_auth_failure(request, "Invalid secret (login)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret",
        )

    # Create session token
    access_token_expires = timedelta(hours=12)
    access_token = create_access_token(
        data={"sub": "admin"}, expires_delta=access_token_expires
    )

    response = JSONResponse(content={"message": "Login successful"})

    # Set secure cookie
    # Note: secure=True requires HTTPS, but localhost is exempt in modern browsers
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=int(access_token_expires.total_seconds()),
    )

    logger.info(f"Admin login successful - IP: {request.client.host if request.client else 'unknown'}")
    return response


@router.post("/logout")
def logout():
    """
    Admin logout endpoint.
    Clears the session cookie.
    """
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(ADMIN_SESSION_COOKIE_NAME)
    return response


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
