"""
Tests for AppealStorage service.
"""

import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.appeal_storage import AppealStorage, AppealData, get_appeal_storage

@pytest.fixture
def storage():
    """Fixture for a fresh AppealStorage instance."""
    return AppealStorage(ttl_hours=1)

def test_store_appeal_sets_timestamp(storage):
    """Test that store_appeal sets the created_at timestamp."""
    key = storage.store_appeal(
        citation_number="TEST-123",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    appeal = storage.get_appeal(key)
    assert appeal is not None
    # This assertion is expected to fail if the bug exists (created_at remains "")
    assert appeal.created_at != ""
    # Verify it's a valid ISO format date
    try:
        datetime.fromisoformat(appeal.created_at)
    except ValueError:
        pytest.fail(f"created_at '{appeal.created_at}' is not a valid ISO format")

def test_cleanup_does_not_delete_fresh_appeal(storage):
    """Test that cleanup_expired does not delete a freshly created appeal."""
    key = storage.store_appeal(
        citation_number="TEST-CLEANUP",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    # Run cleanup immediately
    removed_count = storage.cleanup_expired()

    # Expect 0 removed
    assert removed_count == 0

    # Expect appeal to still exist
    assert storage.get_appeal(key) is not None

def test_store_appeal_success(storage):
    """Test storing an appeal successfully."""
    # Mock datetime to have a fixed time for key generation if needed,
    # but for simple storage test, it's not strictly necessary unless we validate the key format precisely.
    key = storage.store_appeal(
        citation_number="TEST-STORE",
        violation_date="2023-01-01",
        vehicle_info="Honda Civic",
        user_name="Alice Smith",
        user_address="456 Elm St",
        user_city="Othertown",
        user_state="NY",
        user_zip="67890",
        appeal_letter_text="My appeal letter content",
        license_plate="ABC-123",
        user_email="alice@example.com",
        appeal_type="certified",
        selected_photo_ids=["photo1", "photo2"],
        signature_data="base64sig"
    )

    assert key is not None
    assert "TEST-STORE" in key
    assert "67890" in key

    appeal = storage.get_appeal(key)
    assert appeal is not None
    assert appeal.citation_number == "TEST-STORE"
    assert appeal.user_name == "Alice Smith"
    assert appeal.license_plate == "ABC-123"
    assert appeal.selected_photo_ids == ["photo1", "photo2"]
    assert appeal.appeal_type == "certified"

def test_get_appeal_not_found(storage):
    """Test getting a non-existent appeal."""
    assert storage.get_appeal("non-existent-key") is None

def test_get_appeal_expired(storage):
    """Test getting an expired appeal."""
    # Store an appeal
    key = storage.store_appeal(
        citation_number="TEST-EXPIRED",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    # Manually backdate the created_at to simulate expiration
    # We have to access the internal storage because we can't control store_appeal's time without extensive mocking
    expired_time = (datetime.now() - timedelta(hours=2)).isoformat()
    storage._storage[key].created_at = expired_time

    # TTL is 1 hour (set in fixture)
    # Should be expired now
    result = storage.get_appeal(key)
    assert result is None

    # Should be removed from storage
    assert key not in storage._storage

def test_update_payment_status(storage):
    """Test updating payment status."""
    key = storage.store_appeal(
        citation_number="TEST-PAYMENT",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    success = storage.update_payment_status(key, "sess_123", "paid")
    assert success is True

    appeal = storage.get_appeal(key)
    assert appeal.payment_status == "paid"
    assert appeal.stripe_session_id == "sess_123"

def test_update_payment_status_not_found(storage):
    """Test updating payment status for non-existent key."""
    success = storage.update_payment_status("missing-key", "sess_123", "paid")
    assert success is False

def test_delete_appeal(storage):
    """Test deleting an appeal."""
    key = storage.store_appeal(
        citation_number="TEST-DELETE",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    assert storage.delete_appeal(key) is True
    assert storage.get_appeal(key) is None
    assert storage.delete_appeal(key) is False

def test_get_all_appeals(storage):
    """Test getting all appeals."""
    storage.store_appeal(
        citation_number="TEST-ALL-1",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )
    storage.store_appeal(
        citation_number="TEST-ALL-2",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="Jane Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    appeals = storage.get_all_appeals()
    assert len(appeals) == 2

def test_get_stats(storage):
    """Test getting stats."""
    k1 = storage.store_appeal(
        citation_number="TEST-STATS-1",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )
    k2 = storage.store_appeal(
        citation_number="TEST-STATS-2",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="Jane Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    storage.update_payment_status(k1, "sess_1", "paid")

    stats = storage.get_stats()
    assert stats["total_appeals"] == 2
    assert stats["paid"] == 1
    assert stats["pending"] == 1
    assert len(stats["storage_keys"]) == 2

def test_cleanup_expired(storage):
    """Test cleaning up expired appeals."""
    # 1. Fresh appeal (should stay)
    k1 = storage.store_appeal(
        citation_number="TEST-FRESH",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )

    # 2. Expired appeal (should go)
    k2 = storage.store_appeal(
        citation_number="TEST-OLD",
        violation_date="2023-01-01",
        vehicle_info="Test Car",
        user_name="John Doe",
        user_address="123 Main St",
        user_city="Test City",
        user_state="CA",
        user_zip="12345",
        appeal_letter_text="Test appeal"
    )
    storage._storage[k2].created_at = (datetime.now() - timedelta(hours=2)).isoformat()

    # 3. Run cleanup
    removed = storage.cleanup_expired()

    assert removed == 1
    assert storage.get_appeal(k1) is not None
    assert k2 not in storage._storage

def test_get_appeal_storage_singleton():
    """Test that get_appeal_storage returns a singleton."""
    s1 = get_appeal_storage()
    s2 = get_appeal_storage()
    assert s1 is s2
