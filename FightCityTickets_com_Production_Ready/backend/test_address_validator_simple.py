"""
Simple test for address validator (without API calls).
Tests address normalization and comparison logic.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.address_validator import AddressValidator


def test_address_normalization():
    """Test address normalization logic."""
    print("=" * 80)
    print("TESTING ADDRESS NORMALIZATION")
    print("=" * 80)
    print()

    cities_dir = Path(__file__).parent.parent / "cities"
    validator = AddressValidator(cities_dir)

    # Test cases
    test_cases = [
        (
            "Phoenix Municipal Court, 300 West Washington Street, Phoenix, AZ 85003",
            "phoenix municipal court, 300 west washington st, phoenix, az 85003",
            True,  # Should match
        ),
        (
            "P.O. Box 30247, Los Angeles, CA 90030",
            "PO Box 30247, Los Angeles, CA 90030",
            True,  # Should match (P.O. vs PO)
        ),
        (
            "11 South Van Ness Avenue, San Francisco, CA 94103",
            "11 S Van Ness Ave, San Francisco, CA 94103",
            True,  # Should match (abbreviations)
        ),
        (
            "300 West Washington Street, Phoenix, AZ 85003",
            "300 East Washington Street, Phoenix, AZ 85003",
            False,  # Should NOT match (different direction)
        ),
    ]

    print("Testing address normalization and comparison...")
    print()

    for i, (addr1, addr2, should_match) in enumerate(test_cases, 1):
        normalized1 = validator._normalize_address(addr1)
        normalized2 = validator._normalize_address(addr2)
        matches = normalized1 == normalized2

        status = "[OK]" if matches == should_match else "[FAIL]"
        print("Test {i}: {status}")
        print("  Address 1: {addr1}")
        print("  Address 2: {addr2}")
        print("  Normalized 1: {normalized1}")
        print("  Normalized 2: {normalized2}")
        print("  Match: {matches} (expected: {should_match})")
        print()

    print("=" * 80)
    print("NORMALIZATION TEST COMPLETE")
    print("=" * 80)
    print()

    # Test address parsing
    print("=" * 80)
    print("TESTING ADDRESS PARSING")
    print("=" * 80)
    print()

    parse_tests = [
        "Phoenix Municipal Court, 300 West Washington Street, Phoenix, AZ 85003",
        "Parking Violations Bureau, P.O. Box 30247, Los Angeles, CA 90030",
        "SFMTA Customer Service Center, ATTN: Citation Review, 11 South Van Ness Avenue, San Francisco, CA 94103",
        "Denver Parks and Recreation, Manager of Finance, Denver Post Building, 101 West Colfax Ave, 9th Floor, Denver, CO 80202",
    ]

    for addr_str in parse_tests:
        print("Parsing: {addr_str}")
        parts = validator._parse_address_string(addr_str)
        print("  Department: {parts.get('department', '')}")
        print("  Attention: {parts.get('attention', '')}")
        print("  Address1: {parts.get('address1', '')}")
        print("  Address2: {parts.get('address2', '')}")
        print("  City: {parts.get('city', '')}")
        print("  State: {parts.get('state', '')}")
        print("  ZIP: {parts.get('zip', '')}")
        print()


def test_stored_address_extraction():
    """Test extracting stored addresses from city files."""
    print("=" * 80)
    print("TESTING STORED ADDRESS EXTRACTION")
    print("=" * 80)
    print()

    cities_dir = Path(__file__).parent.parent / "cities"
    validator = AddressValidator(cities_dir)

    # Load city registry
    validator.city_registry.load_cities()

    test_cities = [
        "us-az-phoenix",
        "us-ca-los_angeles",
        "us-ny-new_york",
    ]

    for city_id in test_cities:
        stored = validator._get_stored_address_string(city_id)
        print("{city_id}:")
        if stored:
            print("  {stored}")
        else:
            print("  [NOT FOUND]")
        print()


if __name__ == "__main__":
    test_address_normalization()
    test_stored_address_extraction()

    print("=" * 80)
    print("NOTE: To test full validation with API calls, set DEEPSEEK_API_KEY")
    print("=" * 80)

