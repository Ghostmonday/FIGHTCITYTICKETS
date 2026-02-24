"""
Test suite for City Registry Service (Schema 4.3.0).

Tests loading of city configurations, citation matching, address routing,
and phone confirmation policies using pytest.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.city_registry import (
    AppealMailAddress,
    AppealMailStatus,
    CitationPattern,
    CityConfiguration,
    CityRegistry,
    CitySection,
    Jurisdiction,
    PhoneConfirmationPolicy,
    RoutingRule,
    VerificationMetadata,
)


class TestCityRegistry:
    """Test City Registry Service."""

    @pytest.fixture
    def registry(self):
        """Fixture to provide a loaded CityRegistry."""
        # __file__ is backend/tests/test_city_registry.py
        # parent is backend/tests
        # parent.parent is backend
        cities_dir = Path(__file__).parent.parent / "cities"
        registry = CityRegistry(cities_dir)
        registry.load_cities()
        return registry

    def test_city_registry_loading(self, registry):
        """Test basic CityRegistry functionality."""
        cities = registry.get_all_cities()
        assert len(cities) > 0, "Should have loaded at least one city"

        # Verify basic structure
        for city in cities:
            assert "city_id" in city
            assert "name" in city
            assert "citation_pattern_count" in city
            assert "section_count" in city

    def test_citation_matching(self, registry):
        """Test citation number matching."""
        # Test cases: (citation_number, expected_city, expected_section)
        # Note: These test cases rely on the actual city JSON files being present.
        # If files change, these tests might need updates.
        test_cases = [
            ("912345678", "us-ca-san_francisco", "sfmta"),  # SFMTA format (9 + 8 digits)
            ("AB1234567", "us-ca-san_francisco", "sfpd"),   # SFPD format
            ("123456", None, None),  # Too short (no match)
            ("INVALID", None, None),  # Invalid format
        ]

        for citation, exp_city, exp_section in test_cases:
            match = registry.match_citation(citation)
            if exp_city is None:
                assert match is None, f"Expected no match for {citation}, got {match}"
            else:
                assert match is not None, f"Expected match for {citation}"
                assert match[0] == exp_city
                assert match[1] == exp_section

    def test_address_retrieval(self, registry):
        """Test mailing address retrieval."""
        # Test cases: (city_id, section_id, expected_status)
        test_cases = [
            ("us-ca-san_francisco", "sfmta", AppealMailStatus.COMPLETE),
            ("us-ca-san_francisco", "sfpd", AppealMailStatus.COMPLETE),
            ("nonexistent", None, None),
        ]

        for city_id, section_id, exp_status in test_cases:
            address = registry.get_mail_address(city_id, section_id)
            if exp_status is None:
                assert address is None, f"Expected no address for {city_id}/{section_id}, got {address}"
            else:
                assert address is not None, f"Expected address for {city_id}/{section_id}"
                assert address.status == exp_status

    def test_phone_validation(self, registry):
        """Test phone confirmation policies."""
        # Test cases: (city_id, section_id, phone_number, expected_valid)
        test_cases = [
            ("us-ca-san_francisco", "sfmta", "+14155551212", True),  # No requirement
            ("us-ca-san_francisco", "sfpd", "+14155531651", True),   # Valid format
            # SFPD currently has required=False, so all phones are valid
            ("us-ca-san_francisco", "sfpd", "4155531651", True),
        ]

        for city_id, section_id, phone, exp_valid in test_cases:
            is_valid, error = registry.validate_phone_for_city(city_id, phone, section_id)
            assert is_valid == exp_valid, (
                f"Expected {exp_valid} for {phone} in {city_id}/{section_id}, "
                f"got {is_valid} ({error})"
            )

    def test_routing_rules(self, registry):
        """Test routing rule retrieval."""
        test_cases = [
            ("us-ca-san_francisco", "sfmta", RoutingRule.DIRECT),
            ("us-ca-san_francisco", "sfpd", RoutingRule.DIRECT),
        ]

        for city_id, section_id, exp_rule in test_cases:
            rule = registry.get_routing_rule(city_id, section_id)
            assert rule == exp_rule

    def test_config_validation(self):
        """Test city configuration validation logic."""
        registry = CityRegistry()

        # Test a valid configuration
        valid_config = CityConfiguration(
            city_id="test",
            name="Test City",
            jurisdiction=Jurisdiction.CITY,
            citation_patterns=[
                CitationPattern(
                    regex=r"^TEST\d{3}$",
                    section_id="test_section",
                    description="Test citation",
                )
            ],
            appeal_mail_address=AppealMailAddress(
                status=AppealMailStatus.COMPLETE,
                department="Test Department",
                address1="123 Test St",
                city="Test City",
                state="TS",
                zip="12345",
                country="USA",
            ),
            phone_confirmation_policy=PhoneConfirmationPolicy(required=False),
            routing_rule=RoutingRule.DIRECT,
            sections={
                "test_section": CitySection(
                    section_id="test_section",
                    name="Test Section",
                    routing_rule=RoutingRule.DIRECT,
                )
            },
            verification_metadata=VerificationMetadata(
                last_updated="2024-01-01",
                source="test",
                confidence_score=0.9,
            ),
        )

        valid_errors = registry._validate_city_config(valid_config)
        assert not valid_errors, f"Valid config failed validation: {valid_errors}"

        # Test an invalid configuration (missing required fields)
        invalid_config = CityConfiguration(
            city_id="",
            name="",
            jurisdiction=Jurisdiction.CITY,
            citation_patterns=[],
            appeal_mail_address=AppealMailAddress(
                status=AppealMailStatus.COMPLETE,
                department="",  # Empty required field
                address1="",
                city="",
                state="",
                zip="",
                country="",
            ),
            phone_confirmation_policy=PhoneConfirmationPolicy(required=True),
            routing_rule=RoutingRule.DIRECT,
            sections={},
            verification_metadata=VerificationMetadata(
                last_updated="2024-01-01",
                source="test",
                confidence_score=0.9,
            ),
        )

        invalid_errors = registry._validate_city_config(invalid_config)
        assert invalid_errors, "Invalid config should have validation errors"

    def test_manual_configuration_matching(self):
        """
        Test logic using manually constructed configuration.
        Replaces the embedded manual test script from the service file.
        """
        registry = CityRegistry()

        # Create test SF configuration (mimicking real data but isolated)
        sf_config = CityConfiguration(
            city_id="s",
            name="San Francisco",
            jurisdiction=Jurisdiction.CITY,
            citation_patterns=[
                CitationPattern(
                    regex=r"^9\d{8}$",
                    section_id="sfmta",
                    description="SFMTA parking citation",
                    example_numbers=["912345678"],
                )
            ],
            appeal_mail_address=AppealMailAddress(
                status=AppealMailStatus.COMPLETE,
                department="SFMTA Citation Review",
                address1="1 South Van Ness Avenue",
                address2="Floor 7",
                city="San Francisco",
                state="CA",
                zip="94103",
                country="USA",
            ),
            phone_confirmation_policy=PhoneConfirmationPolicy(required=False),
            routing_rule=RoutingRule.DIRECT,
            sections={
                "sfmta": CitySection(
                    section_id="sfmta", name="SFMTA", routing_rule=RoutingRule.DIRECT
                )
            },
            verification_metadata=VerificationMetadata(
                last_updated="2024-01-01", source="official_website", confidence_score=0.95
            ),
        )

        # Manually add for testing
        registry.city_configs["s"] = sf_config
        registry._build_citation_cache_for_city("s", sf_config)

        # Test matching
        match = registry.match_citation("912345678")
        assert match is not None, "Should match valid citation for manual config"
        city_id, section_id = match
        assert city_id == "s"
        assert section_id == "sfmta"

        # Test address retrieval
        address = registry.get_mail_address(city_id, section_id)
        assert address is not None
        assert address.status == AppealMailStatus.COMPLETE
        assert address.city == "San Francisco"

        # Test phone validation
        policy = registry.get_phone_confirmation_policy(city_id, section_id)
        assert policy is not None
        assert policy.required is False
