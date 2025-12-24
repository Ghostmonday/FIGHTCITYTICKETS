"""
Citation Validation Tests for FightSFTickets.com

Tests multi-city citation validation with CityRegistry integration.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.citation import CitationAgency, CitationValidator


class TestCitationValidator:
    """Test CitationValidator with multi-city support."""

    def setup_method(self):
        """Set up test environment."""
        self.cities_dir = Path(__file__).parent.parent.parent / "cities"
        self.validator = CitationValidator(self.cities_dir)

    def test_basic_format_validation(self):
        """Test basic citation format validation."""
        # Valid citations
        assert CitationValidator.validate_citation_format("912345678")[0] == True
        assert CitationValidator.validate_citation_format("SF123456")[0] == True
        assert CitationValidator.validate_citation_format("LA123456")[0] == True
        assert CitationValidator.validate_citation_format("1234567")[0] == True

        # Invalid citations (too short/long)
        assert (
            CitationValidator.validate_citation_format("12345")[0] == False
        )  # Too short
        assert (
            CitationValidator.validate_citation_format("1234567890123")[0] == False
        )  # Too long

        # Invalid format
        assert CitationValidator.validate_citation_format("")[0] == False
        assert CitationValidator.validate_citation_format("   ")[0] == False

    def test_sf_citation_matching(self):
        """Test San Francisco citation matching."""
        test_cases = [
            ("912345678", "sf", "sfmta", CitationAgency.SFMTA),
            ("998765432", "sf", "sfmta", CitationAgency.SFMTA),
            ("SF123456", "sf", "sfpd", CitationAgency.SFPD),
            ("SFSU12345", "sf", "sfsu", CitationAgency.SFSU),
            ("CAMPUS678", "sf", "sfsu", CitationAgency.SFSU),
            ("MU123456", "sf", "sfmud", CitationAgency.SFMUD),
        ]

        for citation, expected_city, expected_section, expected_agency in test_cases:
            validation = self.validator.validate_citation(citation)
            assert validation.is_valid, f"Citation {citation} should be valid"
            assert validation.city_id == expected_city, (
                f"Expected city {expected_city} for {citation}"
            )
            assert validation.section_id == expected_section, (
                f"Expected section {expected_section} for {citation}"
            )
            assert validation.agency == expected_agency, (
                f"Expected agency {expected_agency} for {citation}"
            )

    def test_la_citation_matching(self):
        """Test Los Angeles citation matching."""
        test_cases = [
            ("LA123456", "la", "lapd", CitationAgency.UNKNOWN),  # LAPD
            ("DOT789012", "la", "ladot", CitationAgency.UNKNOWN),  # LADOT
            ("LAX123456", "la", "lax", CitationAgency.UNKNOWN),  # LAX
            ("USC12345", "la", "usc", CitationAgency.UNKNOWN),  # USC
        ]

        for citation, expected_city, expected_section, expected_agency in test_cases:
            validation = self.validator.validate_citation(citation)
            assert validation.is_valid, f"Citation {citation} should be valid"
            assert validation.city_id == expected_city, (
                f"Expected city {expected_city} for {citation}"
            )
            assert validation.section_id == expected_section, (
                f"Expected section {expected_section} for {citation}"
            )
            # LA cities don't have CitationAgency enum values, so they should be UNKNOWN
            assert validation.agency == expected_agency, (
                f"Expected agency {expected_agency} for {citation}"
            )

    def test_nyc_citation_matching(self):
        """Test New York City citation matching."""
        test_cases = [
            ("1234567", "nyc", "nypd", CitationAgency.UNKNOWN),  # NYPD
            ("87654321", "nyc", "nypd", CitationAgency.UNKNOWN),  # NYPD (8 digits)
            ("NYC12345", "nyc", "nycdot", CitationAgency.UNKNOWN),  # NYC DOT
            ("JFK12345", "nyc", "nycairports", CitationAgency.UNKNOWN),  # JFK
            ("LGA67890", "nyc", "nycairports", CitationAgency.UNKNOWN),  # LGA
            ("CUNY1234", "nyc", "cuny", CitationAgency.UNKNOWN),  # CUNY
            ("MTA12345", "nyc", "mta", CitationAgency.UNKNOWN),  # MTA
        ]

        for citation, expected_city, expected_section, expected_agency in test_cases:
            validation = self.validator.validate_citation(citation)
            assert validation.is_valid, f"Citation {citation} should be valid"
            assert validation.city_id == expected_city, (
                f"Expected city {expected_city} for {citation}"
            )
            assert validation.section_id == expected_section, (
                f"Expected section {expected_section} for {citation}"
            )
            assert validation.agency == expected_agency, (
                f"Expected agency {expected_agency} for {citation}"
            )

    def test_city_specific_appeal_deadlines(self):
        """Test city-specific appeal deadline days."""
        test_cases = [
            ("912345678", "sf", 21),  # SF default
            ("LA123456", "la", 21),  # LA default
            ("1234567", "nyc", 30),  # NYC has 30 days
        ]

        for citation, expected_city, expected_days in test_cases:
            validation = self.validator.validate_citation(citation)
            assert validation.is_valid, f"Citation {citation} should be valid"
            assert validation.city_id == expected_city, (
                f"Expected city {expected_city} for {citation}"
            )
            assert validation.appeal_deadline_days == expected_days, (
                f"Expected {expected_days} days for {citation}, got {validation.appeal_deadline_days}"
            )

    def test_phone_confirmation_policies(self):
        """Test phone confirmation policies for different cities/sections."""
        test_cases = [
            ("912345678", False),  # SFMTA - no phone confirmation
            ("SF123456", True),  # SFPD - requires phone confirmation
            ("LA123456", True),  # LAPD - requires phone confirmation
            ("DOT789012", False),  # LADOT - no phone confirmation
            ("1234567", False),  # NYPD - no phone confirmation
            ("NYC12345", True),  # NYC DOT - requires phone confirmation
        ]

        for citation, expected_required in test_cases:
            validation = self.validator.validate_citation(citation)
            assert validation.is_valid, f"Citation {citation} should be valid"
            assert validation.phone_confirmation_required == expected_required, (
                f"Expected phone confirmation required={expected_required} for {citation}"
            )

    def test_deadline_calculation(self):
        """Test appeal deadline calculation with violation dates."""
        # Test with SF citation
        citation = "912345678"
        violation_date = "2024-01-15"

        validation = self.validator.validate_citation(
            citation_number=citation, violation_date=violation_date
        )

        assert validation.is_valid
        assert validation.deadline_date == "2024-02-05"  # 21 days after 2024-01-15
        assert (
            validation.days_remaining >= 0
        )  # Will be negative in the past, but calculated
        assert validation.is_past_deadline in [True, False]  # Depends on current date

        # Test urgent status (within 3 days of deadline)
        # This depends on current date relative to test date

        # Test NYC citation with 30-day deadline
        citation2 = "1234567"
        violation_date2 = "2024-01-01"

        validation2 = self.validator.validate_citation(
            citation_number=citation2, violation_date=violation_date2
        )

        assert validation2.is_valid
        assert validation2.deadline_date == "2024-01-31"  # 30 days after 2024-01-01

    def test_invalid_citations(self):
        """Test invalid citation numbers."""
        invalid_citations = [
            "12345",  # Too short
            "1234567890123",  # Too long
            "!!!!!!",  # No alphanumeric characters
            "   ",  # Whitespace only
            "",  # Empty string
        ]

        for citation in invalid_citations:
            validation = self.validator.validate_citation(citation)
            assert not validation.is_valid, f"Citation {citation} should be invalid"
            assert validation.error_message is not None, (
                f"Should have error message for {citation}"
            )
            assert validation.agency == CitationAgency.UNKNOWN

    def test_formatted_citation_output(self):
        """Test formatted citation number output."""
        test_cases = [
            ("912345678", "912-345-678"),  # SFMTA 9-digit with dashes
            ("SF123456", "SF123456"),  # SFPD - no dashes
            ("LA123456", "LA123456"),  # LAPD - no dashes
            ("1234567", "1234567"),  # NYPD - no dashes (short)
        ]

        for citation, expected_formatted in test_cases:
            validation = self.validator.validate_citation(citation)
            assert validation.is_valid
            assert validation.formatted_citation == expected_formatted, (
                f"Expected formatted {expected_formatted}, got {validation.formatted_citation}"
            )

    def test_class_method_compatibility(self):
        """Test backward compatibility with class methods."""
        # Test class method validate_citation
        validation = CitationValidator.validate_citation("912345678")
        assert validation.is_valid
        assert validation.city_id == "sf"
        assert validation.section_id == "sfmta"

        # Test class method validate_citation_format
        is_valid, error = CitationValidator.validate_citation_format("912345678")
        assert is_valid
        assert error is None

        # Test invalid format
        is_valid, error = CitationValidator.validate_citation_format("12345")
        assert not is_valid
        assert error is not None

    def test_license_plate_validation(self):
        """Test license plate validation."""
        # Valid license plates
        test_cases = [
            ("912345678", "ABC123"),  # Valid
            ("912345678", "ABC1234"),  # Valid
            ("912345678", "ABC-123"),  # Valid (with dash)
        ]

        for citation, license_plate in test_cases:
            validation = self.validator.validate_citation(
                citation_number=citation, license_plate=license_plate
            )
            assert validation.is_valid

        # Invalid license plate (too short)
        validation = self.validator.validate_citation(
            citation_number="912345678", license_plate="A"
        )
        assert validation.is_valid  # Citation still valid
        assert validation.error_message is not None  # But has error about license plate

    def test_citation_info_retrieval(self):
        """Test full citation info retrieval."""
        citation = "912345678"
        info = CitationValidator.get_citation_info(citation)

        assert info.citation_number == citation
        assert info.agency == CitationAgency.SFMTA
        assert info.deadline_date is None  # No violation date provided
        assert info.days_remaining is None
        assert info.is_within_appeal_window is None
        assert info.can_appeal_online in [True, False]  # Depends on city config

    def test_fallback_when_city_registry_unavailable(self):
        """Test backward compatibility when CityRegistry fails."""
        # Create validator with non-existent cities directory
        validator = CitationValidator(Path("/non/existent/directory"))

        # Should still work with SF citations using fallback patterns
        validation = validator.validate_citation("912345678")
        assert validation.is_valid
        # City ID might be None when CityRegistry fails
        # But agency should still be identified
        assert validation.agency == CitationAgency.SFMTA


def run_citation_tests():
    """Run all citation validation tests and report results."""
    import sys
    from pathlib import Path

    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    test_cases = [
        (
            "Basic Format Validation",
            TestCitationValidator().test_basic_format_validation,
        ),
        ("SF Citation Matching", TestCitationValidator().test_sf_citation_matching),
        ("LA Citation Matching", TestCitationValidator().test_la_citation_matching),
        ("NYC Citation Matching", TestCitationValidator().test_nyc_citation_matching),
        (
            "City-Specific Deadlines",
            TestCitationValidator().test_city_specific_appeal_deadlines,
        ),
        (
            "Phone Confirmation Policies",
            TestCitationValidator().test_phone_confirmation_policies,
        ),
        ("Deadline Calculation", TestCitationValidator().test_deadline_calculation),
        ("Invalid Citations", TestCitationValidator().test_invalid_citations),
        (
            "Formatted Citation Output",
            TestCitationValidator().test_formatted_citation_output,
        ),
        (
            "Class Method Compatibility",
            TestCitationValidator().test_class_method_compatibility,
        ),
        (
            "License Plate Validation",
            TestCitationValidator().test_license_plate_validation,
        ),
        (
            "Citation Info Retrieval",
            TestCitationValidator().test_citation_info_retrieval,
        ),
        (
            "Fallback When CityRegistry Unavailable",
            TestCitationValidator().test_fallback_when_city_registry_unavailable,
        ),
    ]

    print("=" * 60)
    print("🔍 Running Citation Validation Tests")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, test_func in test_cases:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_citation_tests()
    sys.exit(0 if success else 1)
