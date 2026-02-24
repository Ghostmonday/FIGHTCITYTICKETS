"""
Fleet Management Routes

Handles fleet registration, onboarding, and webhooks for Stripe Connect.
"""

import logging
import asyncio
from typing import Any
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from ..services.database import get_db_service
from ..services.stripe_service import StripeService
from ..models import Fleet
from ..config import settings

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

class FleetCreateRequest(BaseModel):
    name: str
    email: EmailStr

class FleetResponse(BaseModel):
    id: int
    name: str
    email: str
    stripe_account_id: str | None
    stripe_account_status: str
    onboarding_url: str | None = None

@router.post("", response_model=FleetResponse)
async def create_fleet(request: FleetCreateRequest):
    """
    Create a new fleet and initiate Stripe Connect onboarding.
    """
    db_service = get_db_service()
    stripe_service = StripeService()

    try:
        # Check if fleet exists by email
        with db_service.get_session() as session:
            existing_fleet = session.query(Fleet).filter(Fleet.email == request.email).first()
            if existing_fleet:
                # If exists, return existing status (and new link if needed)
                fleet = existing_fleet
            else:
                # Create Stripe Connected Account
                account = await stripe_service.create_connected_account(request.email)
                account_id = account.get("id")

                # Create Fleet in DB
                fleet = Fleet(
                    name=request.name,
                    email=request.email,
                    stripe_account_id=account_id,
                    stripe_account_status="pending",
                )
                session.add(fleet)
                session.commit()
                session.refresh(fleet)

            # Generate Onboarding Link
            # Refresh URL triggers a new link generation
            # Return URL is where they go after completion
            refresh_url = f"{settings.api_url}/fleets/{fleet.id}/onboarding/refresh"
            return_url = f"{settings.app_url}/fleets/success"

            account_link = await stripe_service.create_account_link(
                account_id=fleet.stripe_account_id,
                refresh_url=refresh_url,
                return_url=return_url
            )

            return FleetResponse(
                id=fleet.id,
                name=fleet.name,
                email=fleet.email,
                stripe_account_id=fleet.stripe_account_id,
                stripe_account_status=fleet.stripe_account_status,
                onboarding_url=account_link.get("url")
            )

    except Exception as e:
        logger.error(f"Error creating fleet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{fleet_id}/onboarding", response_model=FleetResponse)
async def get_onboarding_link(fleet_id: int):
    """
    Get a new onboarding link for an existing fleet.
    """
    db_service = get_db_service()
    stripe_service = StripeService()

    try:
        with db_service.get_session() as session:
            fleet = session.query(Fleet).filter(Fleet.id == fleet_id).first()
            if not fleet:
                raise HTTPException(status_code=404, detail="Fleet not found")

            if not fleet.stripe_account_id:
                 raise HTTPException(status_code=400, detail="Fleet has no Stripe account")

            # Check status from Stripe (optional, to keep DB in sync)
            try:
                account = await stripe_service.get_account(fleet.stripe_account_id)
                if account.get("details_submitted"):
                    fleet.stripe_account_status = "active"
                    session.commit()
            except Exception as e:
                logger.warning(f"Failed to fetch account status: {e}")

            refresh_url = f"{settings.api_url}/fleets/{fleet.id}/onboarding/refresh"
            return_url = f"{settings.app_url}/fleets/success"

            url = None
            try:
                # If account is fully onboarded, creating an account link might fail or behave differently
                # depending on account type. For Express, "account_onboarding" is valid.
                account_link = await stripe_service.create_account_link(
                    account_id=fleet.stripe_account_id,
                    refresh_url=refresh_url,
                    return_url=return_url
                )
                url = account_link.get("url")
            except Exception as e:
                logger.warning(f"Failed to create account link: {e}")

            return FleetResponse(
                id=fleet.id,
                name=fleet.name,
                email=fleet.email,
                stripe_account_id=fleet.stripe_account_id,
                stripe_account_status=fleet.stripe_account_status,
                onboarding_url=url
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{fleet_id}/onboarding/refresh")
async def refresh_onboarding(fleet_id: int):
    """
    Redirect endpoint for refreshing onboarding link.
    """
    # Redirect to the get_onboarding_link API to get JSON? No, browser needs URL.
    # This endpoint is hit by the browser when "refresh_url" is triggered.
    # We should redirect to a frontend page that says "Restarting onboarding..." and then calls API?
    # Or just redirect back to the app page that starts the flow.
    return RedirectResponse(url=f"{settings.app_url}/fleets/{fleet_id}/onboarding")

@router.post("/webhook")
async def handle_connect_webhook(request: Request):
    """
    Handle Stripe Connect webhooks (e.g. account.updated).
    """
    stripe_service = StripeService()
    body = await request.body()
    signature = request.headers.get("stripe-signature", "")

    if not stripe_service.verify_connect_webhook_signature(body, signature):
        logger.warning("Invalid Connect webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        event_data = await request.json()
        event_type = event_data.get("type")
        event_payload = event_data.get("data", {}).get("object", {})

        if event_type == "account.updated":
            account_id = event_payload.get("id")
            details_submitted = event_payload.get("details_submitted", False)

            db_service = get_db_service()
            with db_service.get_session() as session:
                fleet = session.query(Fleet).filter(Fleet.stripe_account_id == account_id).first()
                if fleet:
                    fleet.stripe_account_status = "active" if details_submitted else "pending"
                    session.commit()
                    logger.info(f"Updated fleet {fleet.id} status to {fleet.stripe_account_status}")

        return {"processed": True}

    except Exception as e:
        logger.error(f"Error processing Connect webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
