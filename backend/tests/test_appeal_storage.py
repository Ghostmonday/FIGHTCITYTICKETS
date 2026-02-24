import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from src.services.appeal_storage import AppealStorage, AppealData, get_appeal_storage

# Test data constants
CITATION_NUMBER = "TEST-12345"
VIOLATION_DATE = "2023-01-01"
VEHICLE_INFO = "Test Vehicle"
USER_NAME = "Test User"
USER_ADDRESS = "123 Test St"
USER_CITY = "Test City"
USER_STATE = "TS"
USER_ZIP = "12345"
APPEAL_LETTER = "This is a test appeal letter."
LICENSE_PLATE = "TEST-PLATE"
USER_EMAIL = "test@example.com"
APPEAL_TYPE = "standard"

@pytest.fixture
def storage():
    """Fixture to provide a fresh AppealStorage instance for each test."""
    return AppealStorage(ttl_hours=24)

def test_store_appeal(storage):
    """Test storing an appeal."""
    # Mock datetime to have a fixed time for key generation
    fixed_time = datetime(2023, 1, 1, 12, 0, 0)

    with patch("src.services.appeal_storage.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.strftime = datetime.strftime

        key = storage.store_appeal(
            citation_number=CITATION_NUMBER,
            violation_date=VIOLATION_DATE,
            vehicle_info=VEHICLE_INFO,
            user_name=USER_NAME,
            user_address=USER_ADDRESS,
            user_city=USER_CITY,
            user_state=USER_STATE,
            user_zip=USER_ZIP,
            appeal_letter_text=APPEAL_LETTER,
            license_plate=LICENSE_PLATE,
            user_email=USER_EMAIL,
            appeal_type=APPEAL_TYPE
        )

        # Verify key format
        expected_key = f"{CITATION_NUMBER}_{USER_ZIP}_{fixed_time.strftime('%Y%m%d%H%M%S')}"
        assert key == expected_key

        # Verify stored data
        stored_appeal = storage.get_appeal(key)
        assert stored_appeal is not None
        assert stored_appeal.citation_number == CITATION_NUMBER
        assert stored_appeal.violation_date == VIOLATION_DATE
        assert stored_appeal.vehicle_info == VEHICLE_INFO
        assert stored_appeal.user_name == USER_NAME
        assert stored_appeal.user_address == USER_ADDRESS
        assert stored_appeal.user_city == USER_CITY
        assert stored_appeal.user_state == USER_STATE
        assert stored_appeal.user_zip == USER_ZIP
        assert stored_appeal.appeal_letter_text == APPEAL_LETTER
        assert stored_appeal.license_plate == LICENSE_PLATE
        assert stored_appeal.user_email == USER_EMAIL
        assert stored_appeal.appeal_type == APPEAL_TYPE

        # Check created_at is populated
        # This will fail if the bug exists
        assert stored_appeal.created_at != ""
        assert stored_appeal.created_at == fixed_time.isoformat()

def test_get_appeal_success(storage):
    """Test retrieving an existing appeal."""
    key = storage.store_appeal(
        citation_number=CITATION_NUMBER,
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )

    appeal = storage.get_appeal(key)
    assert appeal is not None
    assert appeal.citation_number == CITATION_NUMBER

def test_get_appeal_not_found(storage):
    """Test retrieving a non-existent appeal."""
    assert storage.get_appeal("non_existent_key") is None

def test_get_appeal_expired(storage):
    """Test retrieving an expired appeal."""
    # Set created_at to 25 hours ago
    past_time = datetime.now() - timedelta(hours=25)

    # We need to manually inject an expired appeal because store_appeal uses datetime.now()
    # and we can't easily mock it for just store_appeal without affecting get_appeal if we want to simulate time passing.
    # So we store it, then modify created_at directly.

    key = storage.store_appeal(
        citation_number=CITATION_NUMBER,
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )

    # Manually expire it
    storage._storage[key].created_at = past_time.isoformat()

    # Now get it
    assert storage.get_appeal(key) is None
    # Verify it was removed
    assert key not in storage._storage

def test_cleanup_expired(storage):
    """Test cleaning up expired appeals."""
    current_time = datetime.now()
    expired_time = current_time - timedelta(hours=25)
    valid_time = current_time - timedelta(hours=1)

    # Add expired appeal
    expired_appeal = AppealData(
        citation_number="EXPIRED",
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER,
        created_at=expired_time.isoformat()
    )
    storage._storage["expired_key"] = expired_appeal

    # Add valid appeal
    valid_appeal = AppealData(
        citation_number="VALID",
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER,
        created_at=valid_time.isoformat()
    )
    storage._storage["valid_key"] = valid_appeal

    count = storage.cleanup_expired()
    assert count == 1
    assert "expired_key" not in storage._storage
    assert "valid_key" in storage._storage

def test_update_payment_status(storage):
    """Test updating payment status."""
    key = storage.store_appeal(
        citation_number=CITATION_NUMBER,
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )

    session_id = "sess_123"
    status = "paid"

    result = storage.update_payment_status(key, session_id, status)
    assert result is True

    appeal = storage.get_appeal(key)
    assert appeal.stripe_session_id == session_id
    assert appeal.payment_status == status

def test_update_payment_status_not_found(storage):
    """Test updating payment status for non-existent appeal."""
    result = storage.update_payment_status("non_existent", "sess_123", "paid")
    assert result is False

def test_delete_appeal(storage):
    """Test deleting an appeal."""
    key = storage.store_appeal(
        citation_number=CITATION_NUMBER,
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )

    assert storage.delete_appeal(key) is True
    assert storage.get_appeal(key) is None

def test_delete_appeal_not_found(storage):
    """Test deleting a non-existent appeal."""
    assert storage.delete_appeal("non_existent") is False

def test_get_all_appeals(storage):
    """Test listing all appeals."""
    storage.store_appeal(
        citation_number="1",
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )
    storage.store_appeal(
        citation_number="2",
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )

    appeals = storage.get_all_appeals()
    assert len(appeals) == 2

def test_get_stats(storage):
    """Test getting stats."""
    key1 = storage.store_appeal(
        citation_number="1",
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )
    storage.store_appeal(
        citation_number="2",
        violation_date=VIOLATION_DATE,
        vehicle_info=VEHICLE_INFO,
        user_name=USER_NAME,
        user_address=USER_ADDRESS,
        user_city=USER_CITY,
        user_state=USER_STATE,
        user_zip=USER_ZIP,
        appeal_letter_text=APPEAL_LETTER
    )

    storage.update_payment_status(key1, "sess_1", "paid")

    stats = storage.get_stats()
    assert stats["total_appeals"] == 2
    assert stats["paid"] == 1
    assert stats["pending"] == 1
    assert len(stats["storage_keys"]) == 2

def test_get_appeal_storage_singleton():
    """Test singleton getter."""
    s1 = get_appeal_storage()
    s2 = get_appeal_storage()
    assert s1 is s2
    assert isinstance(s1, AppealStorage)
