"""
Test script for address validator service.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.address_validator import get_address_validator, AddressValidationResult


async def test_address_validation():
    """Test address validation for a few cities."""
    print("=" * 80)
    print("TESTING ADDRESS VALIDATOR")
    print("=" * 80)
    print()

    # Initialize validator
    cities_dir = Path(__file__).parent.parent / "cities"
    validator = get_address_validator(cities_dir)

    if not validator.is_available:
        print("WARNING: DeepSeek API key not configured")
        print("Set DEEPSEEK_API_KEY environment variable to test")
        return

    # Test cities (start with a few)
    test_cities = [
        "us-az-phoenix",
        "us-ca-los_angeles",
        "us-ny-new_york",
    ]

    print("Testing {len(test_cities)} cities...")
    print()

    for city_id in test_cities:
        print("Testing {city_id}...")
        print("-" * 80)

        try:
            result = await validator.validate_address(city_id)

            if result.is_valid:
                print("[OK] Address validated successfully")
                print("  Stored: {result.stored_address}")
                print("  Scraped: {result.scraped_address}")
            else:
                print("[FAIL] Address validation failed")
                print("  Error: {result.error_message}")
                print("  Stored: {result.stored_address}")
                print("  Scraped: {result.scraped_address}")
                if result.was_updated:
                    print("  [UPDATED] Address was updated in database")

        except Exception as e:
            print("[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()

        print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_address_validation())

