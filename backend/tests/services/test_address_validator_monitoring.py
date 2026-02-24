import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.src.services.address_validator import AddressValidator, AddressValidationResult

@pytest.fixture
def mock_email_service():
    with patch("backend.src.services.address_validator.get_email_service") as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service

@pytest.fixture
def address_validator():
    # Mock settings and city registry to avoid external dependencies
    with patch("backend.src.services.address_validator.settings") as mock_settings, \
         patch("backend.src.services.address_validator.get_city_registry") as mock_registry:

        mock_settings.deepseek_api_key = "dummy"
        mock_settings.deepseek_base_url = "http://dummy"

        # Create validator
        validator = AddressValidator(cities_dir="dummy_path")

        # Mock methods to avoid actual scraping and file operations
        validator._scrape_url = AsyncMock()
        validator._extract_address_from_text = AsyncMock()
        validator._get_stored_address_string = MagicMock(return_value="123 Main St")
        validator.update_city_address = MagicMock(return_value=True)
        validator._set_cached_scrape = MagicMock()
        validator._get_cached_scrape = MagicMock(return_value=None) # Force scrape

        # Add city to mapping to avoid "No URL mapping" error
        from backend.src.services.address_validator import CITY_URL_MAPPING
        CITY_URL_MAPPING["test-city"] = "http://test-city.gov"

        yield validator

@pytest.mark.asyncio
async def test_scrape_success_resets_failure_count(address_validator, mock_email_service):
    # Setup failure count
    address_validator._failure_counts["test-city"] = 2

    # Mock successful scrape
    address_validator._scrape_url.return_value = "<html>Address</html>"
    address_validator._extract_address_from_text.return_value = "123 Main St"

    # Run validation
    await address_validator.validate_address("test-city")

    # Verify count reset
    assert "test-city" not in address_validator._failure_counts

@pytest.mark.asyncio
async def test_scrape_failure_increments_count(address_validator, mock_email_service):
    # Mock failed scrape
    address_validator._scrape_url.return_value = None

    # Run validation
    await address_validator.validate_address("test-city")

    # Verify count incremented
    assert address_validator._failure_counts["test-city"] == 1

    # Run again
    await address_validator.validate_address("test-city")
    assert address_validator._failure_counts["test-city"] == 2

@pytest.mark.asyncio
async def test_third_failure_triggers_alert(address_validator, mock_email_service):
    # Setup failure count
    address_validator._failure_counts["test-city"] = 2

    # Mock failed scrape
    address_validator._scrape_url.return_value = None

    # Run validation (3rd failure)
    await address_validator.validate_address("test-city")

    # Verify alert sent
    mock_email_service.send_admin_alert.assert_called_once()
    args, kwargs = mock_email_service.send_admin_alert.call_args
    assert "Urgent: Address Scraping Failed for test-city" in args[0]

    # Verify count reset after alert (as per implementation)
    assert address_validator._failure_counts["test-city"] == 0

@pytest.mark.asyncio
async def test_failures_tracked_separately(address_validator, mock_email_service):
    # Add another city
    from backend.src.services.address_validator import CITY_URL_MAPPING
    CITY_URL_MAPPING["other-city"] = "http://other-city.gov"

    # Mock failed scrape
    address_validator._scrape_url.return_value = None
    address_validator._get_stored_address_string.return_value = "Address"

    # Fail test-city
    await address_validator.validate_address("test-city")
    assert address_validator._failure_counts["test-city"] == 1
    assert "other-city" not in address_validator._failure_counts

    # Fail other-city
    await address_validator.validate_address("other-city")
    assert address_validator._failure_counts["test-city"] == 1
    assert address_validator._failure_counts["other-city"] == 1
