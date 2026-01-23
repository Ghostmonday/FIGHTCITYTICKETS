"""
OCR Telemetry API endpoint for tracking OCR accuracy and improvement.

Opt-in telemetry for OCR accuracy to enable future model tuning.
"""

import logging
import hashlib
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request

from ..services.ocr_telemetry import get_ocr_telemetry_service, OcrTelemetryRecord

router = APIRouter()
logger = logging.getLogger(__name__)


class OcrTelemetryRequest(BaseModel):
    """Request body for OCR telemetry."""

    city_id: str  # e.g., "sf", "la", "nyc"
    ocr_confidence: float  # 0.0 to 1.0
    user_corrected: bool = False  # Did user manually correct the result?
    manual_entry_used: bool = False  # Did user enter citation manually?
    image_width: int | None = None  # Image dimensions (no PII)
    image_height: int | None = None
    extraction_success: bool = False  # Did OCR extract any text?
    font_type: str | None = None  # Detected font category
    document_type: str | None = None  # "ticket", "notice", etc.
    session_id: str | None = None  # Anonymized session for grouping


class OcrTelemetryResponse(BaseModel):
    """Response for telemetry submission."""

    success: bool
    record_id: int | None = None
    message: str


@router.post("/ocr", response_model=OcrTelemetryResponse)
async def submit_ocr_telemetry(request: Request, data: OcrTelemetryRequest):
    """
    Submit anonymous OCR telemetry for model improvement.

    This endpoint is opt-in and stores no PII. Only metrics about
    OCR accuracy are stored for training future models.

    The session_id is hashed before storage to provide anonymity
    while still allowing analysis of user journeys.
    """
    # Validate input
    if not 0.0 <= data.ocr_confidence <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="ocr_confidence must be between 0.0 and 1.0",
        )

    try:
        # Hash session ID for anonymity
        session_hash = None
        if data.session_id:
            session_hash = hashlib.sha256(
                data.session_id.encode()
            ).hexdigest()[:16]  # First 16 chars of hash

        # Create telemetry record
        record = OcrTelemetryRecord(
            city_id=data.city_id,
            ocr_confidence=data.ocr_confidence,
            user_corrected=data.user_corrected,
            manual_entry_used=data.manual_entry_used,
            image_width=data.image_width,
            image_height=data.image_height,
            extraction_success=data.extraction_success,
            font_type=data.font_type,
            document_type=data.document_type,
            session_hash=session_hash,
        )

        # Store telemetry
        telemetry_service = get_ocr_telemetry_service()
        record_id = telemetry_service.record_ocr_event(record)

        return OcrTelemetryResponse(
            success=True,
            record_id=record_id,
            message="Telemetry recorded (no PII stored)",
        )

    except Exception as e:
        logger.error(f"Failed to record OCR telemetry: {e}")
        return OcrTelemetryResponse(
            success=False,
            record_id=None,
            message="Failed to record telemetry",
        )


@router.get("/ocr/stats/{city_id}")
async def get_ocr_stats(city_id: str):
    """
    Get OCR accuracy statistics for a city.

    Returns aggregate statistics about OCR performance for model tuning.
    """
    try:
        telemetry_service = get_ocr_telemetry_service()
        stats = telemetry_service.get_city_ocr_stats(city_id)
        suggestions = telemetry_service.get_model_improvement_suggestions(city_id)

        return {
            "city_id": city_id,
            "statistics": stats,
            "model_improvement_suggestions": suggestions,
        }

    except Exception as e:
        logger.error(f"Failed to get OCR stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}",
        )
