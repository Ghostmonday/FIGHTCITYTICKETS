"""
Admin Routes for FightSFTickets.com

Provides endpoints for monitoring server status, viewing logs, and accessing recent activity.
Protected by a simple admin secret key header.
"""

import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ..config import settings
from ..models import Intake, Draft, Payment, PaymentStatus
from ..services.database import get_db_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Basic admin security (header check)
ADMIN_SECRET_HEADER = "X-Admin-Secret"

def verify_admin_secret(x_admin_secret: str = Header(...)):
    """Verify the admin secret header."""
    # In production, this should be an environment variable.
    # For now, we'll use the secret_key or a hardcoded fallback if not explicitly set
    expected_secret = os.getenv("ADMIN_SECRET", settings.secret_key)
    
    if x_admin_secret != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin secret",
        )
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
    
    # User Info
    user_name: str
    user_email: Optional[str]
    user_phone: Optional[str]
    user_address: str
    
    # Appeal Info
    violation_date: Optional[str]
    vehicle_info: Optional[str]
    draft_text: Optional[str]
    
    # Payment & Mail
    payment_status: Optional[str]
    amount_total: Optional[float]
    lob_tracking_id: Optional[str]
    lob_mail_type: Optional[str]
    is_fulfilled: bool

class LogResponse(BaseModel):
    logs: str

# Endpoints

@router.get("/stats", response_model=SystemStats)
def get_system_stats(admin_secret: str = Depends(verify_admin_secret)):
    """Get high-level system statistics."""
    db = get_db_service()
    
    if not db.health_check():
        return SystemStats(
            total_intakes=0,
            total_drafts=0,
            total_payments=0,
            pending_fulfillments=0,
            fulfilled_count=0,
            db_status="disconnected"
        )

    with db.get_session() as session:
        total_intakes = session.query(func.count(Intake.id)).scalar() or 0
        total_drafts = session.query(func.count(Draft.id)).scalar() or 0
        total_payments = session.query(func.count(Payment.id)).scalar() or 0
        
        pending_fulfillments = session.query(func.count(Payment.id)).filter(
            Payment.status == PaymentStatus.PAID,
            Payment.is_fulfilled == False
        ).scalar() or 0

        fulfilled_count = session.query(func.count(Payment.id)).filter(
            Payment.is_fulfilled == True
        ).scalar() or 0

    return SystemStats(
        total_intakes=total_intakes,
        total_drafts=total_drafts,
        total_payments=total_payments,
        pending_fulfillments=pending_fulfillments,
        fulfilled_count=fulfilled_count,
        db_status="connected"
    )

@router.get("/activity", response_model=List[RecentActivity])
def get_recent_activity(limit: int = 50, admin_secret: str = Depends(verify_admin_secret)):
    """Get recent intake activity."""
    db = get_db_service()
    
    if not db.health_check():
        raise HTTPException(status_code=503, detail="Database disconnected")

    activity_list = []
    
    with db.get_session() as session:
        # Query recent intakes
        intakes = session.query(Intake).order_by(Intake.created_at.desc()).limit(limit).all()
        
        for intake in intakes:
            # Find associated payment status if any
            payment_status = None
            amount = None
            lob_tracking_id = None
            
            # Since relationship is one-to-many, check if any payments exist
            if intake.payments:
                last_payment = intake.payments[-1]
                payment_status = last_payment.status.value if last_payment.status else None
                amount = last_payment.amount_total / 100.0 if last_payment.amount_total else None
                lob_tracking_id = last_payment.lob_tracking_id
            
            activity_list.append(RecentActivity(
                id=intake.id,
                created_at=intake.created_at.isoformat() if intake.created_at else "",
                citation_number=intake.citation_number,
                status=intake.status,
                payment_status=payment_status,
                amount=amount,
                lob_tracking_id=lob_tracking_id
            ))
            
    return activity_list

@router.get("/intake/{intake_id}", response_model=IntakeDetail)
def get_intake_detail(intake_id: int, admin_secret: str = Depends(verify_admin_secret)):
    """Get full details for a specific intake."""
    db = get_db_service()
    
    with db.get_session() as session:
        # Fetch intake with drafts and payments
        intake = session.query(Intake).filter(Intake.id == intake_id).first()
        
        if not intake:
            raise HTTPException(status_code=404, detail="Intake not found")
            
        # Get draft text
        draft_text = None
        if intake.drafts:
            # Get latest draft
            latest_draft = sorted(intake.drafts, key=lambda x: x.created_at, reverse=True)[0]
            draft_text = latest_draft.draft_text

        # Get payment info
        payment_status = None
        amount_total = None
        lob_tracking_id = None
        lob_mail_type = None
        is_fulfilled = False
        
        if intake.payments:
             # Get latest payment
            latest_payment = sorted(intake.payments, key=lambda x: x.created_at, reverse=True)[0]
            payment_status = latest_payment.status.value if latest_payment.status else None
            amount_total = latest_payment.amount_total / 100.0 if latest_payment.amount_total else None
            lob_tracking_id = latest_payment.lob_tracking_id
            lob_mail_type = latest_payment.lob_mail_type
            is_fulfilled = latest_payment.is_fulfilled
        
        # Format address
        address_parts = [intake.user_address_line1]
        if intake.user_address_line2:
            address_parts.append(intake.user_address_line2)
        address_parts.append(f"{intake.user_city}, {intake.user_state} {intake.user_zip}")
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
            is_fulfilled=is_fulfilled
        )

@router.get("/logs", response_model=LogResponse)
def get_server_logs(lines: int = 100, admin_secret: str = Depends(verify_admin_secret)):
    """
    Get recent server logs.
    Reads from 'server.log' if it exists.
    """
    log_file = "server.log"
    
    if not os.path.exists(log_file):
        return LogResponse(logs="Log file not found (server.log). Ensure logging is configured to write to file.")
    
    try:
        # Read last N lines (simplified approach)
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            return LogResponse(logs="".join(last_lines))
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return LogResponse(logs=f"Error reading log file: {str(e)}")
