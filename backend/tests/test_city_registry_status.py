import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.city_registry import (
    CityRegistry,
    CityStatus,
    CityConfiguration,
    Jurisdiction,
    CitationPattern,
    AppealMailAddress,
    AppealMailStatus,
    PhoneConfirmationPolicy,
    RoutingRule,
    VerificationMetadata,
    CitySection,
)

@pytest.fixture
def mock_registry():
    """Create a registry with manually populated cities for testing."""
    registry = CityRegistry(cities_dir=None) # Use default or None

    # Create configurations
    active_city = CityConfiguration(
        city_id="active_city",
        name="Active City",
        jurisdiction=Jurisdiction.CITY,
        status=CityStatus.ACTIVE,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(status=AppealMailStatus.MISSING),
        phone_confirmation_policy=PhoneConfirmationPolicy(),
        routing_rule=RoutingRule.DIRECT,
        sections={},
        verification_metadata=VerificationMetadata(last_updated="2024-01-01", source="test")
    )

    blocked_city = CityConfiguration(
        city_id="blocked_city",
        name="Blocked City",
        jurisdiction=Jurisdiction.CITY,
        status=CityStatus.BLOCKED,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(status=AppealMailStatus.MISSING),
        phone_confirmation_policy=PhoneConfirmationPolicy(),
        routing_rule=RoutingRule.DIRECT,
        sections={},
        verification_metadata=VerificationMetadata(last_updated="2024-01-01", source="test")
    )

    beta_city = CityConfiguration(
        city_id="beta_city",
        name="Beta City",
        jurisdiction=Jurisdiction.CITY,
        status=CityStatus.BETA,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(status=AppealMailStatus.MISSING),
        phone_confirmation_policy=PhoneConfirmationPolicy(),
        routing_rule=RoutingRule.DIRECT,
        sections={},
        verification_metadata=VerificationMetadata(last_updated="2024-01-01", source="test")
    )

    coming_soon_city = CityConfiguration(
        city_id="coming_soon_city",
        name="Coming Soon City",
        jurisdiction=Jurisdiction.CITY,
        status=CityStatus.COMING_SOON,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(status=AppealMailStatus.MISSING),
        phone_confirmation_policy=PhoneConfirmationPolicy(),
        routing_rule=RoutingRule.DIRECT,
        sections={},
        verification_metadata=VerificationMetadata(last_updated="2024-01-01", source="test")
    )

    registry.city_configs["active_city"] = active_city
    registry.city_configs["blocked_city"] = blocked_city
    registry.city_configs["beta_city"] = beta_city
    registry.city_configs["coming_soon_city"] = coming_soon_city

    return registry

def test_is_eligible_for_appeals(mock_registry):
    assert mock_registry.is_eligible_for_appeals("active_city") is True
    assert mock_registry.is_eligible_for_appeals("beta_city") is True
    assert mock_registry.is_eligible_for_appeals("blocked_city") is False
    assert mock_registry.is_eligible_for_appeals("coming_soon_city") is False
    assert mock_registry.is_eligible_for_appeals("non_existent") is False

def test_get_all_cities_no_filter(mock_registry):
    cities = mock_registry.get_all_cities()
    assert len(cities) == 4

    city_ids = [c["city_id"] for c in cities]
    assert "active_city" in city_ids
    assert "blocked_city" in city_ids
    assert "beta_city" in city_ids
    assert "coming_soon_city" in city_ids

def test_get_all_cities_filter_active(mock_registry):
    cities = mock_registry.get_all_cities(status=CityStatus.ACTIVE)
    assert len(cities) == 1
    assert cities[0]["city_id"] == "active_city"

def test_get_all_cities_filter_blocked(mock_registry):
    cities = mock_registry.get_all_cities(status=CityStatus.BLOCKED)
    assert len(cities) == 1
    assert cities[0]["city_id"] == "blocked_city"

def test_load_real_cities():
    """Test loading actual JSON files to verify status parsing."""
    registry = CityRegistry() # Uses default cities dir
    registry.load_cities()

    # Check Chicago (should be blocked)
    if "us-il-chicago" in registry.city_configs:
        assert registry.city_configs["us-il-chicago"].status == CityStatus.BLOCKED
        assert registry.is_eligible_for_appeals("us-il-chicago") is False

    # Check Boston (should be active)
    if "us-ma-boston" in registry.city_configs:
        assert registry.city_configs["us-ma-boston"].status == CityStatus.ACTIVE
        assert registry.is_eligible_for_appeals("us-ma-boston") is True

    # Check NYC (should be active)
    if "us-ny-new_york" in registry.city_configs:
        assert registry.city_configs["us-ny-new_york"].status == CityStatus.ACTIVE
