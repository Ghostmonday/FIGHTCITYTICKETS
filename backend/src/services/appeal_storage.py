"""
Simple Appeal Data Storage for Fight City Tickets.com

Provides temporary storage for appeal data between frontend submission
and Stripe webhook processing. In production, this should be replaced
with a proper database (PostgreSQL, Redis, etc.).
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class AppealData:
    """Complete appeal data for mail fulfillment."""

    # Citation information (required)
    citation_number: str
    violation_date: str
    vehicle_info: str

    # User information (required)
    user_name: str
    user_address: str
    user_city: str
    user_state: str
    user_zip: str

    # Appeal content (required)
    appeal_letter_text: str  # The refined appeal letter

    # Optional fields with defaults
    license_plate: str | None = None
    user_email: str | None = None
    appeal_type: str = "standard"  # "standard" or "certified"
    selected_photo_ids: list[str] | None = None
    signature_data: str | None = None  # Base64 signature
    created_at: str = ""
    stripe_session_id: str | None = None
    payment_status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Ensure created_at is set if empty
        if not data["created_at"]:
            data["created_at"] = datetime.now().isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppealData":
        """Create from dictionary."""
        return cls(**data)


class AppealStorage:
    """
    Simple in-memory storage for appeal data.

    This is a temporary solution for development. In production,
    replace with a proper database (PostgreSQL, Redis, etc.).
    """

    _storage: dict[str, AppealData]
    _ttl: timedelta

    def __init__(self, ttl_hours: int = 24) -> None:
        """
        Initialize storage with time-to-live.

        Args:
            ttl_hours: Hours before data expires (default: 24)
        """
        self._storage = {}
        self._ttl = timedelta(hours=ttl_hours)

    def store_appeal(
        self,
        citation_number: str,
        violation_date: str,
        vehicle_info: str,
        user_name: str,
        user_address: str,
        user_city: str,
        user_state: str,
        user_zip: str,
        appeal_letter_text: str,
        license_plate: str | None = None,
        user_email: str | None = None,
        appeal_type: str = "standard",
        selected_photo_ids: list[str] | None = None,
        signature_data: str | None = None,
    ) -> str:
        """
        Store appeal data and return a storage key.

        Args:
            citation_number: The citation number
            violation_date: Date of violation
            vehicle_info: Vehicle information
            user_name: Full name
            user_address: Street address
            user_city: City name
            user_state: Two-letter state code
            user_zip: ZIP code
            appeal_letter_text: The appeal letter content
            license_plate: License plate (optional)
            user_email: Email address (optional)
            appeal_type: "standard" or "certified"
            selected_photo_ids: List of photo IDs (optional)
            signature_data: Base64 signature (optional)

        Returns:
            Storage key for retrieving the appeal later
        """
        # Generate a unique storage key
        storage_key = (
            f"{citation_number}_{user_zip}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        appeal = AppealData(
            citation_number=citation_number,
            violation_date=violation_date,
            vehicle_info=vehicle_info,
            user_name=user_name,
            user_address=user_address,
            user_city=user_city,
            user_state=user_state,
            user_zip=user_zip,
            appeal_letter_text=appeal_letter_text,
            license_plate=license_plate,
            user_email=user_email,
            appeal_type=appeal_type,
            selected_photo_ids=selected_photo_ids,
            signature_data=signature_data,
        )

        self._storage[storage_key] = appeal
        return storage_key

    def get_appeal(self, storage_key: str) -> AppealData | None:
        """
        Retrieve appeal data by storage key.

        Args:
            storage_key: The storage key returned by store_appeal()

        Returns:
            AppealData if found and not expired, None otherwise
        """
        if storage_key not in self._storage:
            logger.warning("Appeal not found for key: %s", storage_key)
            return None

        appeal = self._storage[storage_key]

        # Check if expired
        try:
            created_at = datetime.fromisoformat(appeal.created_at)
            if datetime.now() - created_at > self._ttl:
                logger.info("Appeal expired for key: %s", storage_key)
                del self._storage[storage_key]
                return None
        except (ValueError, TypeError):
            # If created_at is invalid, keep the data but log warning
            logger.warning("Invalid created_at for key: %s", storage_key)

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
                "Cannot update payment status: appeal not found for key %s",
                storage_key,
            )
            return False

        appeal.stripe_session_id = session_id
        appeal.payment_status = status

        logger.info(
            "Updated payment status for citation %s: %s (session: %s)",
            appeal.citation_number,
            status,
            session_id,
        )

        return True

    def delete_appeal(self, storage_key: str) -> bool:
        """
        Delete an appeal from storage.

        Args:
            storage_key: The storage key to delete

        Returns:
            True if deleted, False if not found
        """
        if storage_key in self._storage:
            del self._storage[storage_key]
            return True
        return False

    def get_all_appeals(self) -> list[AppealData]:
        """
        Get all non-expired appeals.

        Returns:
            List of all valid AppealData objects
        """
        return list(self._storage.values())

    def get_stats(self) -> dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        total = len(self._storage)
        paid_count = sum(
            1 for a in self._storage.values() if a.payment_status == "paid"
        )
        pending_count = total - paid_count

        return {
            "total_appeals": total,
            "paid": paid_count,
            "pending": pending_count,
            "storage_keys": list(self._storage.keys()),
        }

    def cleanup_expired(self) -> int:
        """
        Remove all expired appeals from storage.

        Returns:
            Number of appeals removed
        """
        expired_keys = []
        current_time = datetime.now()

        for storage_key, appeal in self._storage.items():
            try:
                created_at = datetime.fromisoformat(appeal.created_at)
                if current_time - created_at > self._ttl:
                    expired_keys.append(storage_key)
            except (ValueError, TypeError):
                # Invalid timestamp, consider it expired
                expired_keys.append(storage_key)

        for key in expired_keys:
            del self._storage[key]

        return len(expired_keys)


# Global storage instance
_global_storage: AppealStorage | None = None


def get_appeal_storage() -> AppealStorage:
    """Get the global appeal storage instance."""
    global _global_storage
    if _global_storage is None:
        _global_storage = AppealStorage()
    return _global_storage
