"""
Database Service for Fight City Tickets

Handles database connections, session management, and common operations.
Uses SQLAlchemy with PostgreSQL for production-ready data persistence.
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from ..middleware.resilience import CircuitBreaker, CircuitState, create_database_circuit
from ..models import AppealType, Base, Draft, Intake, Payment, PaymentStatus

# Set up logger
logger = logging.getLogger(__name__)

# Cache for recent lookups during outage
_lookups_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL = 300  # 5 minutes


class DatabaseService:
    """Manages database connections and operations."""

    # Circuit breaker configuration
    CIRCUIT_FAILURE_THRESHOLD = 5
    CIRCUIT_TIMEOUT = 300  # 5 minutes

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database service.

        Args:
            database_url: Optional database URL. If not provided, uses settings.
        """
        self.database_url = database_url or settings.database_url

        if not self.database_url:
            raise ValueError("Database URL not configured. Set DATABASE_URL in .env")

        # Get pool size from environment or use production default
        pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))

        # Create engine with connection pooling (tuned for production)
        self.engine = create_engine(
            self.database_url,
            pool_size=pool_size,      # Base connections (configurable, default 10 for production)
            max_overflow=max_overflow, # Extra connections during spikes (configurable, default 20)
            pool_pre_ping=True,       # Verify connections before using
            pool_recycle=3600,        # Recycle connections after 1 hour
            pool_timeout=pool_timeout, # Wait up to 30s for connection (configurable)
            echo=settings.debug,      # Log SQL queries in debug mode
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
        )

        # Circuit breaker for database resilience
        self._circuit_breaker = create_database_circuit(fallback=self._db_fallback)

        logger.info(f"Database service initialized for {self._masked_url()}")

    def _db_fallback(self) -> dict[str, Any]:
        """Fallback when database circuit is open."""
        return {
            "status": "unavailable",
            "message": "Database temporarily unavailable. Please try again later.",
            "retry_after": 30,
        }

    def is_healthy(self) -> bool:
        """Check if database connection is healthy (respects circuit breaker)."""
        if self._circuit_breaker.metrics.state == CircuitState.OPEN:
            return False
        return self.health_check()

    def get_status(self) -> dict[str, Any]:
        """Get database status including circuit breaker state."""
        return {
            "healthy": self.is_healthy(),
            "circuit_state": self._circuit_breaker.metrics.state.value,
            "circuit_failures": self._circuit_breaker.metrics.failure_count,
            "total_calls": self._circuit_breaker.metrics.total_calls,
        }

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached lookup result."""
        if key in _lookups_cache:
            value, timestamp = _lookups_cache[key]
            if time.time() - timestamp < CACHE_TTL:
                return value
            del _lookups_cache[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        """Cache lookup result."""
        _lookups_cache[key] = (value, time.time())

    def _masked_url(self) -> str:
        """Return database URL with password masked for logging."""
        if "@" in self.database_url:
            parts = self.database_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                if len(user_pass) > 1:
                    masked = f"{user_pass[0]}:****@{parts[1]}"
                    return masked
        return self.database_url

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.

        Usage:
            with db.get_session() as session:
                # Use session
                result = session.query(...).all()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (for testing/development)."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    def health_check(self) -> bool:
        """Check if database is accessible."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def create_intake(self, **kwargs) -> Intake:
        """
        Create a new intake record.

        Args:
            **kwargs: Intake fields

        Returns:
            Created Intake object
        """
        with self.get_session() as session:
            intake = Intake(**kwargs)
            session.add(intake)
            session.flush()  # Get the ID without committing

            logger.info(
                f"Created intake {intake.id} for citation {intake.citation_number}"
            )
            return intake

    def get_intake(self, intake_id: int) -> Optional[Intake]:
        """
        Get intake by ID.

        Args:
            intake_id: Intake ID

        Returns:
            Intake object or None if not found
        """
        with self.get_session() as session:
            return session.query(Intake).filter(Intake.id == intake_id).first()

    def get_intake_by_email_and_citation(self, email: str, citation_number: str) -> Optional[Intake]:
        """
        Get intake by email and citation number.

        Args:
            email: User email address
            citation_number: Citation number

        Returns:
            Intake object or None if not found
        """
        with self.get_session() as session:
            return (
                session.query(Intake)
                .filter(
                    Intake.user_email == email,
                    Intake.citation_number == citation_number
                )
                .first()
            )

    def get_intake_by_citation(self, citation_number: str) -> Optional[Intake]:
        """
        Get intake by citation number.

        Args:
            citation_number: Citation number

        Returns:
            Intake object or None if not found
        """
        with self.get_session() as session:
            return (
                session.query(Intake)
                .filter(Intake.citation_number == citation_number)
                .order_by(Intake.created_at.desc())
                .first()
            )

    def create_draft(
        self,
        intake_id: int,
        draft_text: str,
        appeal_type: AppealType = AppealType.STANDARD,
        **kwargs,
    ) -> Draft:
        """
        Create a draft for an intake.

        Args:
            intake_id: Intake ID
            draft_text: The appeal letter text
            appeal_type: Type of appeal (standard or certified)
            **kwargs: Additional draft fields

        Returns:
            Created Draft object
        """
        with self.get_session() as session:
            # Verify intake exists
            intake = session.query(Intake).filter(Intake.id == intake_id).first()
            if not intake:
                raise ValueError(f"Intake {intake_id} not found")

            draft = Draft(
                intake_id=intake_id,
                draft_text=draft_text,
                appeal_type=appeal_type,
                **kwargs,
            )
            session.add(draft)
            session.flush()

            logger.info(
                f"Created draft {draft.id} for intake {intake_id} (type: {appeal_type})"
            )
            return draft

    def get_draft(self, draft_id: int) -> Optional[Draft]:
        """
        Get draft by ID.

        Args:
            draft_id: Draft ID

        Returns:
            Draft object or None if not found
        """
        with self.get_session() as session:
            return session.query(Draft).filter(Draft.id == draft_id).first()

    def get_latest_draft(self, intake_id: int) -> Optional[Draft]:
        """
        Get the latest draft for an intake.

        Args:
            intake_id: Intake ID

        Returns:
            Latest Draft object or None if not found
        """
        with self.get_session() as session:
            return (
                session.query(Draft)
                .filter(Draft.intake_id == intake_id)
                .order_by(Draft.created_at.desc())
                .first()
            )

    def create_payment(
        self,
        intake_id: int,
        stripe_session_id: str,
        amount_total: int,
        appeal_type: AppealType,
        **kwargs,
    ) -> Payment:
        """
        Create a payment record.

        Args:
            intake_id: Intake ID
            stripe_session_id: Stripe checkout session ID
            amount_total: Amount in cents
            appeal_type: Type of appeal
            **kwargs: Additional payment fields

        Returns:
            Created Payment object
        """
        with self.get_session() as session:
            # Verify intake exists
            intake = session.query(Intake).filter(Intake.id == intake_id).first()
            if not intake:
                raise ValueError(f"Intake {intake_id} not found")
            
            # Check for existing payment for this intake to prevent duplicates
            existing_payment = (
                session.query(Payment)
                .filter(Payment.intake_id == intake_id)
                .first()
            )
            if existing_payment:
                logger.warning(
                    f"Payment already exists for intake {intake_id}: {existing_payment.id}"
                )
                return existing_payment

            payment = Payment(
                intake_id=intake_id,
                stripe_session_id=stripe_session_id,
                amount_total=amount_total,
                appeal_type=appeal_type,
                **kwargs,
            )
            session.add(payment)
            session.flush()

            logger.info(
                f"Created payment {payment.id} for intake {intake_id} (session: {stripe_session_id})"
            )
            return payment

    def get_payment_by_session(self, stripe_session_id: str) -> Optional[Payment]:
        """
        Get payment by Stripe session ID.

        Args:
            stripe_session_id: Stripe checkout session ID

        Returns:
            Payment object or None if not found
        """
        with self.get_session() as session:
            return (
                session.query(Payment)
                .filter(Payment.stripe_session_id == stripe_session_id)
                .first()
            )

    def update_payment_status(
        self, stripe_session_id: str, status: PaymentStatus, **kwargs
    ) -> Optional[Payment]:
        """
        Update payment status.

        Args:
            stripe_session_id: Stripe session ID
            status: New payment status
            **kwargs: Additional fields to update

        Returns:
            Updated Payment object or None if not found
        """
        with self.get_session() as session:
            payment = (
                session.query(Payment)
                .filter(Payment.stripe_session_id == stripe_session_id)
                .first()
            )

            if payment:
                payment.status = status
                for key, value in kwargs.items():
                    if hasattr(payment, key):
                        setattr(payment, key, value)

                logger.info(f"Updated payment {payment.id} status to {status}")
                return payment

            return None

    def mark_payment_fulfilled(
        self, stripe_session_id: str, lob_tracking_id: str, lob_mail_type: str
    ) -> Optional[Payment]:
        """
        Mark payment as fulfilled with Lob tracking info.

        Args:
            stripe_session_id: Stripe session ID
            lob_tracking_id: Lob tracking ID
            lob_mail_type: Lob mail type

        Returns:
            Updated Payment object or None if not found
        """
        from datetime import datetime, timezone

        with self.get_session() as session:
            payment = (
                session.query(Payment)
                .filter(Payment.stripe_session_id == stripe_session_id)
                .first()
            )

            if payment:
                payment.is_fulfilled = True
                payment.fulfillment_date = datetime.now(timezone.utc)
                payment.lob_tracking_id = lob_tracking_id
                payment.lob_mail_type = lob_mail_type

                logger.info(
                    f"Marked payment {payment.id} as fulfilled (Lob: {lob_tracking_id})"
                )
                return payment

            return None

    def get_pending_payments(self, limit: int = 100) -> list[Payment]:
        """
        Get pending payments that need fulfillment.

        Args:
            limit: Maximum number of payments to return

        Returns:
            List of Payment objects
        """
        with self.get_session() as session:
            return (
                session.query(Payment)
                .filter(
                    Payment.status == PaymentStatus.PAID, ~Payment.is_fulfilled
                )
                .order_by(Payment.created_at.asc())
                .limit(limit)
                .all()
            )

    def get_intake_with_drafts_and_payments(self, intake_id: int) -> Optional[Intake]:
        """
        Get intake with all related drafts and payments.

        Args:
            intake_id: Intake ID

        Returns:
            Intake object with relationships loaded
        """
        with self.get_session() as session:
            return (
                session.query(Intake)
                .filter(Intake.id == intake_id)
                .options(
                    # Load relationships
                    session.query(Intake).options(
                        session.query(Intake)
                        .load_only(Intake.id, Intake.citation_number, Intake.user_name)
                        .joinedload(Intake.drafts),
                        session.query(Intake).joinedload(Intake.payments),
                    )
                )
                .first()
            )


# Global database service instance
_global_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get the global database service instance."""
    global _global_db_service
    if _global_db_service is None:
        _global_db_service = DatabaseService()
    return _global_db_service


# Test function
def test_database():
    """Test the database service."""
    print("🧪 Testing Database Service")
    print("=" * 50)

    try:
        db = get_db_service()

        # Health check
        if db.health_check():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return

        # Create tables (if they don't exist)
        try:
            db.create_tables()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"⚠️  Tables may already exist: {e}")

        # Test creating an intake
        test_intake = db.create_intake(
            citation_number="912345678",
            user_name="Test User",
            user_address_line1="123 Test St",
            user_city="San Francisco",
            user_state="CA",
            user_zip="94102",
            user_email="test@example.com",
            appeal_reason="Meter was broken",
            status="draft",
        )
        print(
            f"✅ Created intake {test_intake.id} for citation {test_intake.citation_number}"
        )

        # Test creating a draft
        test_draft = db.create_draft(
            intake_id=test_intake.id,
            draft_text="This is a test appeal letter.",
            appeal_type=AppealType.STANDARD,
            is_final=True,
        )
        print(f"✅ Created draft {test_draft.id} for intake {test_intake.id}")

        # Test creating a payment
        test_payment = db.create_payment(
            intake_id=test_intake.id,
            stripe_session_id="cs_test_123456789",
            amount_total=900,  # $9.00
            appeal_type=AppealType.STANDARD,
            status=PaymentStatus.PENDING,
        )
        print(f"✅ Created payment {test_payment.id} for intake {test_intake.id}")

        # Test retrieval
        retrieved_intake = db.get_intake(test_intake.id)
        if retrieved_intake:
            print(f"✅ Retrieved intake {retrieved_intake.id}")

        retrieved_payment = db.get_payment_by_session("cs_test_123456789")
        if retrieved_payment:
            print("Retrieved payment by session ID")

        print("\n" + "=" * 50)
        print("✅ Database Service Test Complete")

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_database()
