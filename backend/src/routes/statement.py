"""
Statement Refinement Routes for Fight City Tickets.com

Handles AI-powered appeal statement refinement using DeepSeek.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

try:
    from services.statement import refine_statement
except ImportError:
    from ..services.statement import refine_statement

router = APIRouter()


class StatementRefinementRequest(BaseModel):
    """Request model for statement refinement."""

    original_statement: str
    citation_number: Optional[str] = None
    citation_type: str = "parking"
    desired_tone: str = "professional"
    max_length: int = 500


class StatementRefinementResponse(BaseModel):
    """Response model for statement refinement."""

    status: str  # "success", "fallback", "error", "service_unavailable"
    original_statement: str
    refined_statement: str
    improvements: Optional[dict] = None
    error_message: Optional[str] = None
    method_used: str = ""  # "deepseek", "local_fallback"


@router.post("/refine", response_model=StatementRefinementResponse)
async def refine_appeal_statement(request: StatementRefinementRequest):
    """
    Refine a user's appeal statement using AI.

    Uses DeepSeek to convert informal complaints into professional,
    UPL-compliant appeal letters for San Francisco parking tickets.

    Falls back to basic local refinement if AI service unavailable.
    """
    try:
        # Validate input
        if not request.original_statement or not request.original_statement.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Original statement cannot be empty",
            )

        if len(request.original_statement) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Original statement too long (max 10000 characters)",
            )

        # Call the refinement service
        result = await refine_statement(
            original_statement=request.original_statement,
            citation_number=request.citation_number or "",
            citation_type=request.citation_type,
            desired_tone=request.desired_tone,
            max_length=request.max_length,
        )

        # Convert service response to API response
        return StatementRefinementResponse(
            status=result.status,
            original_statement=result.original_statement,
            refined_statement=result.refined_statement,
            improvements=result.improvements,
            error_message=result.error_message,
            method_used=result.method_used,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statement refinement failed: {str(e)}",
        ) from e


@router.post("/polish", response_model=StatementRefinementResponse, deprecated=True)
async def polish_statement(request: StatementRefinementRequest):
    """
    DEPRECATED: Use /refine endpoint instead.

    Legacy endpoint for backward compatibility.
    """
    return await refine_appeal_statement(request)
