"""
Database Models for FightSFTickets.com

Defines SQLAlchemy models for storing appeal data, drafts, and payments.
"""

import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class AppealType(str, enum.Enum):
    """Enum for appeal types."""

    STANDARD = "standard"
    CERTIFIED = "certified"


class PaymentStatus(str, enum.Enum):
    """Enum for payment statuses."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Intake(Base):
    """
    Represents an appeal intake/submission.

    This is the initial submission of appeal data before payment.
    """

    __tablename__ = "intakes"

    id = Column(Integer, primary_key=True, index=True)
    # Citation information
    citation_number = Column(String(50), nullable=False, index=True)
    violation_date = Column(String(20), nullable=True)
    vehicle_info = Column(String(200), nullable=True)
    license_plate = Column(String(20), nullable=True)

    # User information
    user_name = Column(String(100), nullable=False)
    user_address_line1 = Column(String(200), nullable=False)
    user_address_line2 = Column(String(200), nullable=True)
    user_city = Column(String(50), nullable=False)
    user_state = Column(String(2), nullable=False)
    user_zip = Column(String(10), nullable=False)
    user_email = Column(String(100), nullable=True, index=True)
    user_phone = Column(String(20), nullable=True)

    # Appeal details
    appeal_reason = Column(Text, nullable=True)
    selected_evidence = Column(
        JSON, nullable=True
    )  # JSON array of evidence IDs/descriptions
    signature_data = Column(Text, nullable=True)  # Base64 signature image

    # Metadata
    city = Column(String(50), default="s")  # For future expansion to other cities
    status = Column(String(20), default="draft")  # draft, submitted, paid, fulfilled
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    drafts = relationship(
        "Draft", back_populates="intake", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="intake", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_intakes_citation_status", "citation_number", "status"),
        Index("ix_intakes_created_at", "created_at"),
    )


class Draft(Base):
    """
    Represents an appeal draft/letter.

    This stores the generated appeal letter text and related metadata.
    """

    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    intake_id = Column(
        Integer,
        ForeignKey("intakes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Draft content
    appeal_type = Column(Enum(AppealType), nullable=False, default=AppealType.STANDARD)
    draft_text = Column(Text, nullable=False)  # The full appeal letter text
    refined_text = Column(Text, nullable=True)  # AI-refined version if applicable

    # Generation metadata
    is_ai_refined = Column(Boolean, default=False)
    ai_model_used = Column(String(50), nullable=True)
    ai_prompt_version = Column(String(20), nullable=True)

    # Metadata
    version = Column(Integer, default=1)  # For multiple drafts per intake
    is_final = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    intake = relationship("Intake", back_populates="drafts")

    # Indexes
    __table_args__ = (
        Index("ix_drafts_intake_type", "intake_id", "appeal_type"),
        Index("ix_drafts_created_at", "created_at"),
    )


class Payment(Base):
    """
    Represents a payment transaction.

    This stores Stripe payment information and links to intakes.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    intake_id = Column(
        Integer,
        ForeignKey("intakes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Stripe information
    stripe_session_id = Column(String(100), nullable=False, unique=True, index=True)
    stripe_payment_intent = Column(String(100), nullable=True, index=True)
    stripe_customer_id = Column(String(100), nullable=True, index=True)

    # Payment details
    amount_total = Column(Integer, nullable=False)  # In cents
    currency = Column(String(3), default="usd")
    appeal_type = Column(Enum(AppealType), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # Metadata from Stripe
    stripe_metadata = Column(JSON, nullable=True)
    receipt_url = Column(String(500), nullable=True)

    # Fulfillment tracking
    is_fulfilled = Column(Boolean, default=False)
    fulfillment_date = Column(DateTime(timezone=True), nullable=True)
    lob_tracking_id = Column(String(100), nullable=True)
    lob_mail_type = Column(String(50), nullable=True)  # "standard" or "certified"

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    intake = relationship("Intake", back_populates="payments")

    # Indexes
    __table_args__ = (
        Index("ix_payments_status_created", "status", "created_at"),
        Index("ix_payments_stripe_session", "stripe_session_id"),
        Index("ix_payments_fulfillment", "is_fulfilled", "created_at"),
    )


# Helper function to create all tables
def create_all_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


# Helper function to drop all tables
def drop_all_tables(engine):
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
