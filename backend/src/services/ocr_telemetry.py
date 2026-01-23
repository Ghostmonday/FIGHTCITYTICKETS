"""
OCR Telemetry storage service for tracking OCR accuracy and improvement.

This service stores anonymous telemetry data to help improve OCR models
for citation number extraction across different cities.
"""

import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class OcrTelemetry(Base):
    """
    Anonymous OCR telemetry record for model improvement.
    
    No PII is stored - only anonymized metrics about OCR accuracy.
    """
    __tablename__ = "ocr_telemetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Anonymized city identifier
    city_id = Column(String(50), nullable=False, index=True)
    
    # OCR metrics (no PII)
    ocr_confidence = Column(Float, nullable=False)
    user_corrected = Column(Boolean, default=False)
    manual_entry_used = Column(Boolean, default=False)
    
    # Image metadata (no actual image stored)
    image_width = Column(Integer)
    image_height = Column(Integer)
    extraction_success = Column(Boolean, default=False)
    
    # Per-city model metadata
    font_type = Column(String(100))  # Detected font category
    document_type = Column(String(50))  # ticket, notice, etc.
    
    # Timestamp for analysis
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Optional: anonymized session ID (hash, not user data)
    session_hash = Column(String(64))


@dataclass
class OcrTelemetryRecord:
    """Record for creating telemetry entries."""
    city_id: str
    ocr_confidence: float
    user_corrected: bool = False
    manual_entry_used: bool = False
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    extraction_success: bool = False
    font_type: Optional[str] = None
    document_type: Optional[str] = None
    session_hash: Optional[str] = None


class OcrTelemetryService:
    """Service for storing and analyzing OCR telemetry."""

    def __init__(self):
        """Initialize telemetry service with database connection."""
        self._engine = None
        self._session_factory = None

    def _get_engine(self):
        """Lazy initialization of database engine."""
        if self._engine is None:
            self._engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
        return self._engine

    def _get_session_factory(self):
        """Lazy initialization of session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self._get_engine(),
                autocommit=False,
                autoflush=False,
            )
        return self._session_factory

    @contextmanager
    def get_session(self) -> Session:
        """Get a database session."""
        SessionLocal = self._get_session_factory()
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Telemetry session error: {e}")
            raise
        finally:
            session.close()

    def record_ocr_event(self, record: OcrTelemetryRecord) -> int:
        """
        Record an OCR telemetry event.

        Args:
            record: Telemetry record with metrics

        Returns:
            ID of the created record
        """
        try:
            with self.get_session() as session:
                telemetry = OcrTelemetry(
                    city_id=record.city_id,
                    ocr_confidence=record.ocr_confidence,
                    user_corrected=record.user_corrected,
                    manual_entry_used=record.manual_entry_used,
                    image_width=record.image_width,
                    image_height=record.image_height,
                    extraction_success=record.extraction_success,
                    font_type=record.font_type,
                    document_type=record.document_type,
                    session_hash=record.session_hash,
                )
                session.add(telemetry)
                session.flush()  # Get the ID
                return telemetry.id
        except Exception as e:
            logger.error(f"Failed to record OCR telemetry: {e}")
            return -1

    def get_city_ocr_stats(self, city_id: str) -> dict:
        """
        Get OCR accuracy statistics for a city.

        Args:
            city_id: City identifier

        Returns:
            Statistics dictionary
        """
        try:
            with self.get_session() as session:
                from sqlalchemy import func

                stats = session.query(
                    func.count(OcrTelemetry.id).label("total"),
                    func.avg(OcrTelemetry.ocr_confidence).label("avg_confidence"),
                    func.sum(
                        func.cast(OcrTelemetry.user_corrected, Integer)
                    ).label("corrected_count"),
                    func.sum(
                        func.cast(OcrTelemetry.extraction_success, Integer)
                    ).label("success_count"),
                ).filter(OcrTelemetry.city_id == city_id).first()

                return {
                    "city_id": city_id,
                    "total_ocr_attempts": stats.total or 0,
                    "avg_confidence": round(stats.avg_confidence or 0, 3),
                    "correction_rate": round(
                        (stats.corrected_count or 0) / max(stats.total or 1, 1),
                        3,
                    ),
                    "success_rate": round(
                        (stats.success_count or 0) / max(stats.total or 1, 1),
                        3,
                    ),
                }
        except Exception as e:
            logger.error(f"Failed to get OCR stats: {e}")
            return {"error": str(e)}

    def get_model_improvement_suggestions(self, city_id: str) -> list:
        """
        Get suggestions for improving OCR models for a city.

        Args:
            city_id: City identifier

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        try:
            stats = self.get_city_ocr_stats(city_id)

            if stats.get("correction_rate", 0) > 0.2:
                suggestions.append(
                    f"High correction rate ({stats['correction_rate']*100:.1f}%) - "
                    f"consider adjusting OCR preprocessing for {city_id}"
                )

            if stats.get("avg_confidence", 0) < 0.6:
                suggestions.append(
                    f"Low average confidence ({stats['avg_confidence']*100:.1f}%) - "
                    "investigate font types and image quality"
                )

        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")

        return suggestions


# Singleton instance
_telemetry_service: Optional[OcrTelemetryService] = None


def get_ocr_telemetry_service() -> OcrTelemetryService:
    """Get the telemetry service singleton."""
    global _telemetry_service
    if _telemetry_service is None:
        _telemetry_service = OcrTelemetryService()
    return _telemetry_service
