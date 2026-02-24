import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys

# Add backend directory to path so imports work
backend_dir = str(Path(__file__).parents[2])
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from src.services.city_registry import (
    CityRegistry,
    CityConfiguration,
    CitySection,
    SpecialRequirements,
    RoutingRule,
    Jurisdiction,
    AppealMailAddress,
    AppealMailStatus,
    PhoneConfirmationPolicy,
)

@pytest.fixture
def mock_city_registry():
    registry = CityRegistry()
    return registry

def create_mock_city(
    city_id: str,
    requires_poa: bool = False,
    corporate_blocked: bool = False,
    hard_poa_required: bool = False,
    fleet_appeals_blocked: bool = False,
) -> CityConfiguration:
    return CityConfiguration(
        city_id=city_id,
        name=f"Test City {city_id}",
        jurisdiction=Jurisdiction.CITY,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(status=AppealMailStatus.MISSING),
        phone_confirmation_policy=PhoneConfirmationPolicy(),
        routing_rule=RoutingRule.DIRECT,
        sections={
            "default": CitySection(
                section_id="default",
                name="Default Section",
                special_requirements=SpecialRequirements(
                    requires_poa=requires_poa,
                    corporate_blocked=corporate_blocked,
                    hard_poa_required=hard_poa_required,
                    fleet_appeals_blocked=fleet_appeals_blocked,
                ),
            )
        },
        verification_metadata=MagicMock(),
    )

def test_city_eligibility(mock_city_registry):
    # Test case 1: Eligible city (no restrictions)
    eligible_city = create_mock_city("eligible")
    assert eligible_city.is_eligible is True

    # Test case 2: Blocked by POA
    poa_city = create_mock_city("poa", requires_poa=True)
    assert poa_city.is_eligible is False

    # Test case 3: Blocked by Hard POA
    hard_poa_city = create_mock_city("hard_poa", hard_poa_required=True)
    assert hard_poa_city.is_eligible is False

    # Test case 4: Blocked by Corporate
    corp_city = create_mock_city("corp", corporate_blocked=True)
    assert corp_city.is_eligible is False

    # Test case 5: Blocked by Fleet
    fleet_city = create_mock_city("fleet", fleet_appeals_blocked=True)
    assert fleet_city.is_eligible is False

def test_get_all_cities_filter(mock_city_registry):
    # Setup mock cities
    mock_city_registry.city_configs = {
        "eligible": create_mock_city("eligible"),
        "poa": create_mock_city("poa", requires_poa=True),
        "corp": create_mock_city("corp", corporate_blocked=True),
    }

    # Test without filter
    all_cities = mock_city_registry.get_all_cities(eligible_only=False)
    assert len(all_cities) == 3

    # Test with filter
    eligible_cities = mock_city_registry.get_all_cities(eligible_only=True)
    assert len(eligible_cities) == 1
    assert eligible_cities[0]["city_id"] == "eligible"
    assert eligible_cities[0]["is_eligible"] is True

def test_multiple_sections_eligibility(mock_city_registry):
    # City with one blocked section and one eligible section should be eligible
    city = CityConfiguration(
        city_id="mixed",
        name="Mixed City",
        jurisdiction=Jurisdiction.CITY,
        citation_patterns=[],
        appeal_mail_address=AppealMailAddress(status=AppealMailStatus.MISSING),
        phone_confirmation_policy=PhoneConfirmationPolicy(),
        routing_rule=RoutingRule.DIRECT,
        sections={
            "blocked": CitySection(
                section_id="blocked",
                name="Blocked Section",
                special_requirements=SpecialRequirements(requires_poa=True),
            ),
            "allowed": CitySection(
                section_id="allowed",
                name="Allowed Section",
                special_requirements=SpecialRequirements(requires_poa=False),
            ),
        },
        verification_metadata=MagicMock(),
    )

    assert city.is_eligible is True
