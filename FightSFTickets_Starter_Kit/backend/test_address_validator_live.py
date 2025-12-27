"""
Live test for address validator - tests actual web scraping and DeepSeek extraction.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load .env file BEFORE importing anything that uses settings
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, encoding='utf-8')
    print("Loaded .env from: {env_path.absolute()}")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.address_validator import get_address_validator, CITY_URL_MAPPING  # noqa: E402
from src.config import settings  # noqa: E402


async def test_live_validation():
    """Test live address validation with web scraping."""
    print("=" * 80)
    print("LIVE ADDRESS VALIDATION TEST")
    print("=" * 80)
    print()

    # Check API key from environment
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key or api_key in ["sk_dummy", "change-me"]:
        print("ERROR: DeepSeek API key not configured")
        print()
        print("To test live validation, set the DEEPSEEK_API_KEY environment variable:")
        print("  Windows PowerShell: $env:DEEPSEEK_API_KEY='your-key-here'")
        print("  Windows CMD: set DEEPSEEK_API_KEY=your-key-here")
        print("  Linux/Mac: export DEEPSEEK_API_KEY=your-key-here")
        print()
        print("Or add it to your .env file:")
        print("  DEEPSEEK_API_KEY=your-key-here")
        return

    print("DeepSeek API key found: {api_key[:10]}...")
    print()

    # Initialize validator with explicit API key override
    cities_dir = Path(__file__).parent.parent / "cities"
    validator = get_address_validator(cities_dir)

    # Override API key from environment
    validator.api_key = api_key
    validator.is_available = bool(api_key and api_key not in ["sk_dummy", "change-me"])

    if not validator.is_available:
        print("ERROR: Address validator not available")
        return

    print("DeepSeek API configured: {validator.base_url}")
    print("Model: {validator.model}")
    print()

    # Test with a few cities (start with simpler ones)
    test_cities = [
        ("us-az-phoenix", "Phoenix, AZ"),
        ("us-ca-los_angeles", "Los Angeles, CA"),
        # Add more if you want to test more cities
    ]

    print("Testing {len(test_cities)} cities with live web scraping...")
    print()

    for city_id, city_name in test_cities:
        print("=" * 80)
        print("Testing: {city_name} ({city_id})")
        print("=" * 80)

        # Get URL
        url = CITY_URL_MAPPING.get(city_id, "N/A")
        print("URL: {url}")

        # Get stored address
        stored_address = validator._get_stored_address_string(city_id)
        print("Stored Address: {stored_address}")
        print()

        # Test scraping
        print("Step 1: Scraping website...")
        try:
            scraped_text = await validator._scrape_url(CITY_URL_MAPPING[city_id])
            if scraped_text:
                print("  [OK] Scraped {len(scraped_text)} characters")
                print("  Preview: {scraped_text[:200]}...")
            else:
                print("  [FAIL] Failed to scrape website")
                print()
                continue
        except Exception as e:
            print("  [ERROR] Scraping failed: {e}")
            print()
            continue

        print()

        # Test address extraction
        print("Step 2: Extracting address using DeepSeek...")
        try:
            scraped_address = await validator._extract_address_from_text(scraped_text, city_id)
            if scraped_address:
                print("  [OK] Extracted address: {scraped_address}")
            else:
                print("  [FAIL] Could not extract address")
                print()
                continue
        except Exception as e:
            print("  [ERROR] Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            print()
            continue

        print()

        # Test comparison
        print("Step 3: Comparing addresses...")
        if stored_address:
            matches = validator._addresses_match(stored_address, scraped_address)
            print("  Stored:   {stored_address}")
            print("  Scraped: {scraped_address}")
            print("  Match:    {matches}")

            if matches:
                print("  [OK] Addresses match!")
            else:
                print("  [MISMATCH] Addresses differ")
                print()
                print("  Normalized stored:   ", validator._normalize_address(stored_address))
                print("  Normalized scraped:  ", validator._normalize_address(scraped_address))
        else:
            print("  [WARNING] No stored address found for comparison")

        print()
        print()

    print("=" * 80)
    print("LIVE VALIDATION TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_live_validation())

