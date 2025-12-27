"""
Citation and Ticket Routes for FightSFTickets.com

Handles citation validation and related ticket services.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

try:
    from services.citation import CitationValidator
except ImportError:
    from ..services.citation import CitationValidator

router = APIRouter()

# Rate limiter - will be set from app.py after app initialization
limiter: Optional[object] = None


# Legacy ticket types (keep for backward compatibility, but deprecate)
class TicketType(BaseModel):
    """Legacy ticket type model."""

    id: str
    name: str
    price_cents: int
    currency: str = "USD"
    available: bool = True


# Citation validation models
class CitationValidationRequest(BaseModel):
    """Request model for citation validation."""

    citation_number: str
    license_plate: Optional[str] = None
    violation_date: Optional[str] = None
    city_id: Optional[str] = None


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

    Performs comprehensive validation including:
    - Format checking
    - Agency identification
    - City detection from citation number
    - City mismatch detection (if city_id provided)
    - Appeal deadline calculation
    - Deadline status (urgent/past due)
    """
    try:
        # Use the citation validation service
        validation = CitationValidator.validate_citation(
            citation_number=request.citation_number,
            violation_date=request.violation_date,
            license_plate=request.license_plate,
            city_id=request.city_id,  # Pass selected city for validation
        )

        # Check for city mismatch if city_id was provided
        city_mismatch = False
        selected_city_mismatch_message = None

        if request.city_id and validation.city_id:
            if validation.city_id != request.city_id:
                city_mismatch = True
                # Get city names for error message
                try:
                    from ..services.city_registry import get_city_registry
                    city_registry = get_city_registry()
                    if city_registry:
                        detected_city_config = city_registry.get_city_config(validation.city_id)
                        selected_city_config = city_registry.get_city_config(request.city_id)

                        detected_name = detected_city_config.name if detected_city_config else validation.city_id
                        selected_name = selected_city_config.name if selected_city_config else request.city_id

                        selected_city_mismatch_message = (
                            "The citation number appears to be from {detected_name}, "
                            "but you selected {selected_name}. Please verify your selection or citation number."
                        )
                    else:
                        selected_city_mismatch_message = (
                            "The citation number appears to be from {validation.city_id}, "
                            "but you selected {request.city_id}. Please verify your selection or citation number."
                        )
                except Exception:
                    # Fallback if city registry not available
                    selected_city_mismatch_message = (
                        "The citation number appears to be from {validation.city_id}, "
                        "but you selected {request.city_id}. Please verify your selection or citation number."
                    )

        # Convert service response to API response
        return CitationValidationResponse(
            is_valid=validation.is_valid,
            citation_number=validation.citation_number,
            agency=validation.agency.value if validation.agency else "UNKNOWN",
            deadline_date=validation.deadline_date,
            days_remaining=validation.days_remaining,
            is_past_deadline=validation.is_past_deadline,
            is_urgent=validation.is_urgent,
            error_message=validation.error_message,
            formatted_citation=validation.formatted_citation,
            # Multi-city metadata
            city_id=validation.city_id,
            section_id=validation.section_id,
            appeal_deadline_days=validation.appeal_deadline_days,
            phone_confirmation_required=validation.phone_confirmation_required,
            phone_confirmation_policy=validation.phone_confirmation_policy,
            # City mismatch detection
            city_mismatch=city_mismatch,
            selected_city_mismatch_message=selected_city_mismatch_message,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Citation validation failed: {str(e)}",
        ) from e


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get citation info: {str(e)}",
        ) from e
