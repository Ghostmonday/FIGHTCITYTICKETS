"""
Citation and Ticket Routes for Fight City Tickets.com

Handles citation validation and related ticket services.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..middleware.rate_limit import limiter
from ..services.citation import CitationValidator
from ..services.city_registry import get_city_registry

logger = logging.getLogger(__name__)

# Legacy short codes to full city IDs mapping
CITY_ID_MAPPING = {
    "sf": "us-ca-san_francisco",
    "la": "us-ca-los_angeles",
    "nyc": "us-ny-new_york",
    "chicago": "us-il-chicago",
    "seattle": "us-wa-seattle",
    "denver": "us-co-denver",
    "portland": "us-or-portland",
    "phoenix": "us-az-phoenix",
}

router = APIRouter()


class TicketType(BaseModel):
    """Legacy ticket type model - kept for backward compatibility."""

    id: str
    name: str
    price_cents: int
    currency: str = "USD"
    available: bool = True


class CitationValidationRequest(BaseModel):
    """Request model for citation validation."""

    citation_number: str = Field(..., max_length=100)
    license_plate: Optional[str] = Field(None, max_length=20)
    violation_date: Optional[str] = Field(None, max_length=20)
    city_id: Optional[str] = Field(None, max_length=100)


class CitationValidationResponse(BaseModel):
    """Response model for citation validation."""

    is_valid: bool
    citation_number: str
    agency: str
    deadline_date: Optional[str] = None
    days_remaining: Optional[int] = None
    is_past_deadline: bool = False
    is_urgent: bool = False
    error_message: Optional[str] = None
    formatted_citation: Optional[str] = None

    # Multi-city metadata
    city_id: Optional[str] = None
    section_id: Optional[str] = None
    appeal_deadline_days: int = 21
    phone_confirmation_required: bool = False
    phone_confirmation_policy: Optional[Dict[str, Any]] = None

    # City mismatch detection
    city_mismatch: bool = False
    selected_city_mismatch_message: Optional[str] = None


# Legacy ticket inventory (keep for old clients)
LEGACY_INVENTORY: List[TicketType] = [
    TicketType(id="general", name="General Admission", price_cents=5000),
    TicketType(id="vip", name="VIP", price_cents=15000),
]


@router.post("/validate", response_model=CitationValidationResponse)
def validate_citation(request: CitationValidationRequest):
    """
    Validate a parking citation and check against selected city.
    
    NOTE: Simplified for MVP - just accepts citation number format.
    Real city validation can be added later.
    """
    # Simple format check only - accept any valid-looking citation
    citation = request.citation_number.strip()
    if len(citation) < 5:
        return CitationValidationResponse(
            is_valid=False,
            citation_number=request.citation_number,
            agency="unknown",
            error_message="Citation number too short"
        )
    
    # Get city deadline days from registry
    # Use mapping for legacy short codes, or raw city_id if not mapped
    mapped_city_id = CITY_ID_MAPPING.get(request.city_id, request.city_id)
    deadline_days = 21

    if mapped_city_id:
        registry = get_city_registry()
        config = registry.get_city_config(mapped_city_id)
        if config:
            deadline_days = config.appeal_deadline_days

    return CitationValidationResponse(
        is_valid=True,
        citation_number=request.citation_number,
        agency=request.city_id or "unknown",
        city_id=request.city_id,
        section_id="general",
        appeal_deadline_days=deadline_days,
        deadline_date=None,
        days_remaining=deadline_days,
        is_past_deadline=False,
        is_urgent=False,
        phone_confirmation_required=False
    )


@router.get("", response_model=List[TicketType], deprecated=True)
def list_ticket_types():
    """
    LEGACY ENDPOINT: List available ticket types.

    DEPRECATED: This endpoint is for backward compatibility.
    New clients should use citation-specific endpoints.
    """
    return LEGACY_INVENTORY


@router.get("/citation/{citation_number}")
def get_citation_info(citation_number: str):
    """
    Get detailed information about a citation.

    Returns comprehensive citation data including validation,
    deadline calculation, and agency information.
    """
    try:
        # Basic validation
        validation = CitationValidator.validate_citation(citation_number)

        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation.error_message,
            )

        # Get full citation info
        info = CitationValidator.get_citation_info(citation_number)

        return {
            "citation_number": info.citation_number,
            "agency": info.agency.value,
            "deadline_date": info.deadline_date,
            "days_remaining": info.days_remaining,
            "is_within_appeal_window": info.is_within_appeal_window,
            "can_appeal_online": info.can_appeal_online,
            "online_appeal_url": info.online_appeal_url,
            "formatted_citation": validation.formatted_citation,
            "city_id": info.city_id,
            "section_id": info.section_id,
            "appeal_deadline_days": info.appeal_deadline_days,
            "phone_confirmation_required": info.phone_confirmation_required,
            "phone_confirmation_policy": info.phone_confirmation_policy,
            "appeal_mail_address": info.appeal_mail_address,
            "routing_rule": info.routing_rule,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get citation info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get citation info: {str(e)}",
        ) from e
