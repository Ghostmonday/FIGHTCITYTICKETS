from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.scheduler import (
    run_address_verification_job,
    shutdown_scheduler,
    start_scheduler,
)


@pytest.mark.asyncio
async def test_run_address_verification_job():
    """Test that the job iterates over cities and calls validate_address."""

    # Mock CITY_URL_MAPPING
    mock_mapping = {"city1": "url1", "city2": "url2"}

    # Mock AddressValidator
    mock_validator = MagicMock()
    mock_validator.validate_address = AsyncMock()

    # Mock result for city1 (success)
    result1 = MagicMock()
    result1.is_valid = True
    result1.was_updated = False

    # Mock result for city2 (failure but updated)
    result2 = MagicMock()
    result2.is_valid = False
    result2.was_updated = True

    mock_validator.validate_address.side_effect = [result1, result2]

    with patch("src.scheduler.CITY_URL_MAPPING", mock_mapping), \
         patch("src.scheduler.get_address_validator", return_value=mock_validator):

        await run_address_verification_job()

        # Verify calls
        assert mock_validator.validate_address.call_count == 2
        mock_validator.validate_address.assert_any_call("city1")
        mock_validator.validate_address.assert_any_call("city2")

@pytest.mark.asyncio
async def test_scheduler_lifecycle():
    """Test start and shutdown of scheduler."""
    with patch("src.scheduler.AsyncIOScheduler") as mock_scheduler_cls:
        mock_scheduler = MagicMock()
        mock_scheduler.running = False
        mock_scheduler_cls.return_value = mock_scheduler

        # Test start
        scheduler = start_scheduler()

        assert scheduler == mock_scheduler
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()

        # Test shutdown
        # Simulate running state for shutdown check
        mock_scheduler.running = True
        shutdown_scheduler()
        mock_scheduler.shutdown.assert_called_once()
