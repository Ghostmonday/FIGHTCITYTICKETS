"""
Simple Appeal Data Storage for FightSFTickets.com

Provides temporary storage for appeal data between frontend submission
and Stripe webhook processing. In production, this should be replaced
with a proper database (PostgreSQL, Redis, etc.).
"""

import hashlib
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class AppealData:
    """Complete appeal data for mail fulfillment."""

    # Citation information
    citation_number: str
    violation_date: str
    vehicle_info: str
    license_plate: Optional[str] = None

    # User information
    user_name: str
    user_address: str
    user_city: str
    user_state: str
    user_zip: str
    user_email: Optional[str] = None

    # Appeal content
    appeal_letter_text: str  # The refined appeal letter
    appeal_type: str = "standard"  # "standard" or "certified"

    # Evidence (stored as references/URLs, not actual data)
    selected_photo_ids: Optional[List[str]] = None
    signature_data: Optional[str] = None  # Base64 signature

    # Metadata
    created_at: str = ""
    stripe_session_id: Optional[str] = None
    payment_status: str = "pending"

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Ensure created_at is set if empty
        if not data["created_at"]:
            data["created_at"] = datetime.now().isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "AppealData":
        """Create from dictionary."""
        return cls(**data)


class AppealStorage:
    """
    Simple in-memory storage for appeal data.

    This is a temporary solution for development. In production,
    replace with a proper database (PostgreSQL, Redis, etc.).
    """

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize storage with time-to-live.

        Args:
            ttl_hours: Hours before data expires (default: 24)
        """
        self._storage: Dict[str, AppealData] = {}
        self._ttl = timedelta(hours=ttl_hours)
        logger.info("Appeal storage initialized with {ttl_hours}h TTL")

    def _generate_key(
        self, citation_number: str, user_email: Optional[str] = None
    ) -> str:
        """Generate a unique storage key."""
        # Use citation number + timestamp hash for uniqueness
        timestamp = str(time.time())
        key_data = "{citation_number}:{timestamp}"
        if user_email:
            key_data += ":{user_email}"

        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    def store_appeal(self, appeal: AppealData) -> str:
        """
        Store appeal data and return a storage key.

        Args:
            appeal: Complete appeal data

        Returns:
            Storage key for retrieval
        """
        # Generate unique key
        storage_key = self._generate_key(appeal.citation_number, appeal.user_email)

        # Ensure created_at is set
        if not appeal.created_at:
            appeal.created_at = datetime.now().isoformat()

        # Store the data
        self._storage[storage_key] = appeal

        logger.info(
            "Stored appeal for citation {appeal.citation_number} "
            "(key: {storage_key}, type: {appeal.appeal_type})"
        )

        return storage_key

    def get_appeal(self, storage_key: str) -> Optional[AppealData]:
        """
        Retrieve appeal data by storage key.

        Args:
            storage_key: The storage key returned by store_appeal()

        Returns:
            AppealData if found and not expired, None otherwise
        """
        if storage_key not in self._storage:
            logger.warning("Appeal not found for key: {storage_key}")
            return None

        appeal = self._storage[storage_key]

        # Check if expired
        try:
            created_at = datetime.fromisoformat(appeal.created_at)
            if datetime.now() - created_at > self._ttl:
                logger.info("Appeal expired for key: {storage_key}")
                del self._storage[storage_key]
                return None
        except (ValueError, TypeError):
            # If created_at is invalid, keep the data but log warning
            logger.warning("Invalid created_at for key: {storage_key}")

        return appeal

    def update_payment_status(
        self, storage_key: str, session_id: str, status: str
    ) -> bool:
        """
        Update payment status for an appeal.

        Args:
            storage_key: Storage key for the appeal
            session_id: Stripe session ID
            status: Payment status ("paid", "failed", etc.)

        Returns:
            True if updated successfully, False otherwise
        """
        appeal = self.get_appeal(storage_key)
        if not appeal:
            logger.warning(
                "Cannot update payment status: appeal not found for key {storage_key}"
            )
            return False

        appeal.stripe_session_id = session_id
        appeal.payment_status = status

        logger.info(
            "Updated payment status for citation {appeal.citation_number}: "
            "{status} (session: {session_id})"
        )

        return True

    def delete_appeal(self, storage_key: str) -> bool:
        """
        Delete appeal data.

        Args:
            storage_key: Storage key to delete

        Returns:
            True if deleted, False if not found
        """
        if storage_key in self._storage:
            citation = self._storage[storage_key].citation_number
            del self._storage[storage_key]
            logger.info("Deleted appeal for citation {citation} (key: {storage_key})")
            return True
        return False

    def cleanup_expired(self) -> int:
        """
        Clean up expired appeal data.

        Returns:
            Number of expired appeals removed
        """
        expired_keys = []
        now = datetime.now()

        for key, appeal in self._storage.items():
            try:
                created_at = datetime.fromisoformat(appeal.created_at)
                if now - created_at > self._ttl:
                    expired_keys.append(key)
            except (ValueError, TypeError):
                # Invalid timestamp, mark for cleanup
                expired_keys.append(key)

        for key in expired_keys:
            del self._storage[key]

        if expired_keys:
            logger.info("Cleaned up {len(expired_keys)} expired appeals")

        return len(expired_keys)

    def get_stats(self) -> dict:
        """Get storage statistics."""
        total = len(self._storage)

        # Count by appeal type
        by_type = {"standard": 0, "certified": 0}
        by_status = {}

        for appeal in self._storage.values():
            by_type[appeal.appeal_type] = by_type.get(appeal.appeal_type, 0) + 1
            by_status[appeal.payment_status] = (
                by_status.get(appeal.payment_status, 0) + 1
            )

        return {
            "total_appeals": total,
            "by_appeal_type": by_type,
            "by_payment_status": by_status,
            "ttl_hours": self._ttl.total_seconds() / 3600,
        }


# Global storage instance
_global_storage: Optional[AppealStorage] = None


def get_appeal_storage() -> AppealStorage:
    """Get the global appeal storage instance."""
    global _global_storage
    if _global_storage is None:
        _global_storage = AppealStorage()
    return _global_storage


def store_appeal_for_checkout(appeal: AppealData) -> str:
    """
    High-level function to store appeal data before checkout.

    This should be called when the user is ready to pay,
    before creating the Stripe checkout session.

    Returns:
        Storage key to include in Stripe metadata
    """
    storage = get_appeal_storage()
    return storage.store_appeal(appeal)


def retrieve_appeal_for_fulfillment(storage_key: str) -> Optional[AppealData]:
    """
    Retrieve appeal data for mail fulfillment.

    This should be called from the Stripe webhook handler
    after successful payment.

    Args:
        storage_key: Storage key from Stripe metadata

    Returns:
        AppealData if found, None otherwise
    """
    storage = get_appeal_storage()
    return storage.get_appeal(storage_key)


# Test function
def test_storage():
    """Test the appeal storage system."""
    print("🧪 Testing Appeal Storage")
    print("=" * 50)

    storage = get_appeal_storage()

    # Create test appeal
    test_appeal = AppealData(
        citation_number="912345678",
        violation_date="2024-01-15",
        vehicle_info="Honda Civic ABC123",
        user_name="Test User",
        user_address="123 Test St",
        user_city="San Francisco",
        user_state="CA",
        user_zip="94102",
        appeal_letter_text="This is a test appeal letter.",
        appeal_type="certified",
    )

    # Store the appeal
    storage_key = storage.store_appeal(test_appeal)
    print("✅ Stored appeal with key: {storage_key}")

    # Retrieve the appeal
    retrieved = storage.get_appeal(storage_key)
    if retrieved and retrieved.citation_number == test_appeal.citation_number:
        print(
            "✅ Successfully retrieved appeal for citation: {retrieved.citation_number}"
        )
    else:
        print("❌ Failed to retrieve appeal")

    # Update payment status
    storage.update_payment_status(storage_key, "cs_test_123", "paid")

    # Get stats
    stats = storage.get_stats()
    print("✅ Storage stats: {stats}")

    # Cleanup (won't remove since it's new)
    cleaned = storage.cleanup_expired()
    print("✅ Cleaned up {cleaned} expired appeals")

    print("\n" + "=" * 50)
    print("✅ Appeal Storage Test Complete")


if __name__ == "__main__":
    test_storage()
