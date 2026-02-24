import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from backend.src.services.address_validator import AddressValidator

@pytest.fixture
def mock_city_registry():
    mock_registry = MagicMock()
    # Setup get_mail_address to return a valid address object
    mock_address = MagicMock()
    mock_address.status.value = "complete"
    mock_address.department = "Dept"
    mock_address.attention = None
    mock_address.address1 = "123 Main St"
    mock_address.address2 = None
    mock_address.city = "Test City"
    mock_address.state = "TS"
    mock_address.zip = "12345"
    mock_registry.get_mail_address.return_value = mock_address
    return mock_registry

@pytest.fixture
def mock_email_service():
    mock_service = AsyncMock()
    mock_service.send_admin_alert = AsyncMock(return_value=True)
    return mock_service

@pytest.fixture
def address_validator(mock_city_registry):
    # Mocking get_city_registry inside AddressValidator
    with patch("backend.src.services.address_validator.get_city_registry", return_value=mock_city_registry):
        validator = AddressValidator(cities_dir=Path("/tmp/cities"))

        # Override CITY_URL_MAPPING to include our test city
        from backend.src.services import address_validator as av_module
        av_module.CITY_URL_MAPPING["test-city"] = "http://test-city.com"
        av_module.EXPECTED_ADDRESSES["test-city"] = "123 Main St, Test City, TS 12345"

        yield validator

        # Cleanup
        if "test-city" in av_module.CITY_URL_MAPPING:
            del av_module.CITY_URL_MAPPING["test-city"]
        if "test-city" in av_module.EXPECTED_ADDRESSES:
            del av_module.EXPECTED_ADDRESSES["test-city"]

@pytest.mark.asyncio
async def test_alert_on_consecutive_failures(address_validator, mock_email_service):
    """Test that admin alert is sent after 3 consecutive scraping failures."""

    city_id = "test-city"

    # Mock _scrape_url to fail
    address_validator._scrape_url = AsyncMock(return_value=None)

    # Mock get_email_service to return our mock service
    with patch("backend.src.services.address_validator.get_email_service", return_value=mock_email_service):

        # 1st Failure
        await address_validator.validate_address(city_id)
        assert address_validator._failure_counts[city_id] == 1
        mock_email_service.send_admin_alert.assert_not_called()

        # 2nd Failure
        await address_validator.validate_address(city_id)
        assert address_validator._failure_counts[city_id] == 2
        mock_email_service.send_admin_alert.assert_not_called()

        # 3rd Failure - Should trigger alert
        await address_validator.validate_address(city_id)
        # Count resets to 0 after alert
        assert address_validator._failure_counts[city_id] == 0
        mock_email_service.send_admin_alert.assert_called_once()

        # Check call arguments
        args, kwargs = mock_email_service.send_admin_alert.call_args
        # Implementation uses positional args: subject, message
        message = args[1]
        assert "Address scraping has failed 3 times" in message

        # 4th Failure - Should count as 1
        mock_email_service.send_admin_alert.reset_mock()
        await address_validator.validate_address(city_id)
        assert address_validator._failure_counts[city_id] == 1
        mock_email_service.send_admin_alert.assert_not_called()

@pytest.mark.asyncio
async def test_reset_count_on_success(address_validator, mock_email_service):
    """Test that failure count resets on success."""

    city_id = "test-city"

    # Mock _scrape_url to fail initially
    address_validator._scrape_url = AsyncMock(return_value=None)

    with patch("backend.src.services.address_validator.get_email_service", return_value=mock_email_service):
        # 2 Failures
        await address_validator.validate_address(city_id)
        await address_validator.validate_address(city_id)
        assert address_validator._failure_counts[city_id] == 2

        # Success
        # We need _scrape_url to return text, and _extract_address_from_text to return address
        address_validator._scrape_url = AsyncMock(return_value="Valid content")
        address_validator._extract_address_from_text = AsyncMock(return_value="123 Main St, Test City, TS 12345")

        await address_validator.validate_address(city_id)

        # Count should be reset (key removed)
        assert city_id not in address_validator._failure_counts

        # Clear cache to force scraping again
        address_validator._scrape_cache = {}

        # Fail again
        address_validator._scrape_url = AsyncMock(return_value=None)
        await address_validator.validate_address(city_id)
        assert address_validator._failure_counts[city_id] == 1
