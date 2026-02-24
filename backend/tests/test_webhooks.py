import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch, ANY
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.routes.webhooks import (
    _is_event_processed,
    _mark_event_processed,
    _is_event_processed_memory,
    _mark_event_processed_memory,
    _cleanup_expired_entries,
    _WEBHOOK_CACHE,
    _WEBHOOK_CACHE_TTL,
    _WEBHOOK_CACHE_MAX_SIZE,
)
from src.models import WebhookEvent

@pytest.fixture
def mock_db_service():
    with patch("src.routes.webhooks.get_db_service") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock

        # Mock the db session
        db_mock = MagicMock()
        service_mock.db = db_mock

        yield service_mock

@pytest.fixture
def reset_webhook_cache():
    """Clear the webhook cache before and after each test."""
    _WEBHOOK_CACHE.clear()
    yield
    _WEBHOOK_CACHE.clear()

def test_imports():
    """Basic test to verify imports work."""
    assert _WEBHOOK_CACHE == {}

def test_is_event_processed_db_hit(mock_db_service):
    """Test when event is found in the database."""
    event_id = "evt_test_123"
    expected_result = {"message": "Success"}

    # Mock database return value
    mock_event = WebhookEvent(
        stripe_event_id=event_id,
        processed=True,
        result_message="Success"
    )
    mock_db_service.db.query.return_value.filter.return_value.first.return_value = mock_event

    is_processed, result = _is_event_processed(event_id)

    assert is_processed is True
    assert result == expected_result

    # Verify DB interaction
    mock_db_service.db.query.assert_called_once()

def test_is_event_processed_db_miss(mock_db_service):
    """Test when event is not found in the database."""
    event_id = "evt_test_missing"

    # Mock database returning None
    mock_db_service.db.query.return_value.filter.return_value.first.return_value = None

    is_processed, result = _is_event_processed(event_id)

    assert is_processed is False
    assert result is None

def test_is_event_processed_db_error_memory_hit(mock_db_service, reset_webhook_cache):
    """Test fallback to memory cache when database fails (hit in memory)."""
    event_id = "evt_test_error_hit"
    cached_result = {"message": "Cached Success"}

    # Populate memory cache
    _WEBHOOK_CACHE[event_id] = {
        "processed": True,
        "timestamp": time.time(),
        "result": cached_result
    }

    # Mock database raising exception
    mock_db_service.db.query.side_effect = Exception("DB Connection Error")

    is_processed, result = _is_event_processed(event_id)

    assert is_processed is True
    assert result == cached_result

def test_is_event_processed_db_error_memory_miss(mock_db_service, reset_webhook_cache):
    """Test fallback to memory cache when database fails (miss in memory)."""
    event_id = "evt_test_error_miss"

    # Ensure cache is empty
    _WEBHOOK_CACHE.clear()

    # Mock database raising exception
    mock_db_service.db.query.side_effect = Exception("DB Connection Error")

    is_processed, result = _is_event_processed(event_id)

    assert is_processed is False
    assert result is None

def test_mark_event_processed_new(mock_db_service):
    """Test marking a new event as processed in the database."""
    event_id = "evt_new_123"
    event_type = "test.event"
    result_data = {"message": "Processed successfully"}

    # Mock database returning None (not found)
    mock_db_service.db.query.return_value.filter.return_value.first.return_value = None

    _mark_event_processed(event_id, event_type, result_data)

    # Verify add was called
    mock_db_service.db.add.assert_called_once()
    args, _ = mock_db_service.db.add.call_args
    added_event = args[0]

    assert isinstance(added_event, WebhookEvent)
    assert added_event.stripe_event_id == event_id
    assert added_event.event_type == event_type
    assert added_event.processed is True
    assert added_event.result_message == result_data["message"]

    # Verify commit was called
    mock_db_service.db.commit.assert_called_once()

def test_mark_event_processed_existing(mock_db_service):
    """Test updating an existing event in the database."""
    event_id = "evt_existing_123"
    event_type = "test.event"
    result_data = {"message": "Updated processing"}

    # Mock existing event
    mock_existing_event = MagicMock(spec=WebhookEvent)
    mock_existing_event.processed = False
    mock_db_service.db.query.return_value.filter.return_value.first.return_value = mock_existing_event

    _mark_event_processed(event_id, event_type, result_data)

    # Verify no new add
    mock_db_service.db.add.assert_not_called()

    # Verify attributes updated
    assert mock_existing_event.processed is True
    assert mock_existing_event.result_message == result_data["message"]

    # Verify commit was called
    mock_db_service.db.commit.assert_called_once()

def test_mark_event_processed_db_error(mock_db_service, reset_webhook_cache):
    """Test fallback to memory cache when database fails on mark."""
    event_id = "evt_error_mark"
    event_type = "test.event"
    result_data = {"message": "Memory fallback"}

    # Mock database raising exception
    mock_db_service.db.query.side_effect = Exception("DB Insert Error")

    _mark_event_processed(event_id, event_type, result_data)

    # Verify added to memory cache
    assert event_id in _WEBHOOK_CACHE
    assert _WEBHOOK_CACHE[event_id]["processed"] is True
    assert _WEBHOOK_CACHE[event_id]["result"] == result_data

def test_memory_cache_hit(reset_webhook_cache):
    """Test hit in memory cache."""
    event_id = "evt_mem_hit"
    result = {"status": "ok"}

    _WEBHOOK_CACHE[event_id] = {
        "processed": True,
        "timestamp": time.time(),
        "result": result
    }

    found, cached_result = _is_event_processed_memory(event_id)
    assert found is True
    assert cached_result == result

def test_memory_cache_miss(reset_webhook_cache):
    """Test miss in memory cache."""
    found, cached_result = _is_event_processed_memory("evt_mem_miss")
    assert found is False
    assert cached_result is None

def test_memory_cache_expiry(reset_webhook_cache):
    """Test that expired entries are removed."""
    event_id = "evt_expired"

    # Add expired entry
    _WEBHOOK_CACHE[event_id] = {
        "processed": True,
        "timestamp": time.time() - _WEBHOOK_CACHE_TTL - 1,
        "result": {"status": "expired"}
    }

    found, cached_result = _is_event_processed_memory(event_id)

    assert found is False
    assert cached_result is None
    assert event_id not in _WEBHOOK_CACHE

def test_memory_cache_cleanup_trigger(reset_webhook_cache):
    """Test that cleanup is triggered when cache is full."""

    # Reduce max size for testing
    original_max_size = _WEBHOOK_CACHE_MAX_SIZE

    # We need to patch the module-level variable used inside the function
    # Since we imported _WEBHOOK_CACHE_MAX_SIZE, it's a local name in the test file,
    # but the function uses the one in src.routes.webhooks.
    # However, integers are immutable, so patching `src.routes.webhooks._WEBHOOK_CACHE_MAX_SIZE` is needed.

    with patch("src.routes.webhooks._WEBHOOK_CACHE_MAX_SIZE", 5):
        # Fill cache to limit (5 * 0.8 = 4 is trigger point, but let's just fill it)
        for i in range(5):
            _mark_event_processed_memory(f"evt_{i}", {"msg": f"{i}"})

        # Verify size
        assert len(_WEBHOOK_CACHE) == 5

        # Add one more (should trigger cleanup if expired)
        # To test cleanup logic properly, let's make some expired
        _WEBHOOK_CACHE["evt_0"]["timestamp"] -= (_WEBHOOK_CACHE_TTL + 10)

        _mark_event_processed_memory("evt_new", {"msg": "new"})

        # evt_0 should be gone
        assert "evt_0" not in _WEBHOOK_CACHE
