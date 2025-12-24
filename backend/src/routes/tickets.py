"""
Citation and Ticket Routes for FightSFTickets.com

Handles citation validation and related ticket services.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

try:
    from services.citation import CitationValidator
except ImportError:
    from ..services.citation import CitationValidator

router = APIRouter()


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


# Legacy ticket inventory (keep for old clients)
LEGACY_INVENTORY: List[TicketType] = [
    TicketType(id="general", name="General Admission", price_cents=5000),
    TicketType(id="vip", name="VIP", price_cents=15000),
]


@router.post("/validate", response_model=CitationValidationResponse)
def validate_citation(request: CitationValidationRequest):
    """
    Validate a San Francisco parking citation.

    Performs comprehensive validation including:
    - Format checking
    - Agency identification (SFMTA vs others)
    - Appeal deadline calculation
    - Deadline status (urgent/past due)
    """
    try:
        # Use the citation validation service
        validation = CitationValidator.validate_citation(
            citation_number=request.citation_number,
            violation_date=request.violation_date,
            license_plate=request.license_plate,
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
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Citation validation failed: {str(e)}",
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
            "formatted_citation": validation.formatted_citation,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get citation info: {str(e)}",
        )
