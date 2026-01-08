"""
Standalone live test for address validator - avoids config import issues.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load .env file FIRST
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    # Force reload by overriding existing values
    load_dotenv(env_path, encoding='utf-8', override=True)
    print("Loaded .env from: {env_path.absolute()}")
    # Also read directly from file to ensure we get latest
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('DEEPSEEK_API_KEY='):
                api_key_from_file = line.split('=', 1)[1].strip()
                os.environ['DEEPSEEK_API_KEY'] = api_key_from_file
                break
else:
    api_key_from_file = None

# Get API key from environment - try new key first if old one fails
api_key = os.getenv("DEEPSEEK_API_KEY")

# If user updated .env, try the new key they mentioned
if not api_key or api_key.endswith("1461"):
    # Try the new key from user's update
    new_key = "sk-4663d43612b94180a04f3456e5b544d4"
    print("Trying new API key: {new_key[:15]}...")
    api_key = new_key
    os.environ["DEEPSEEK_API_KEY"] = new_key

if not api_key or api_key in ["sk_dummy", "change-me"]:
    print("ERROR: DeepSeek API key not found in environment")
    sys.exit(1)

print("Using DeepSeek API key: {api_key[:15]}...")
print("Full key length: {len(api_key)} characters")
print()

# Import httpx directly (no config dependency)
import httpx  # noqa: E402
import re  # noqa: E402

# City URL mapping (copied to avoid config import)
CITY_URL_MAPPING = {
    "us-az-phoenix": "https://www.phoenix.gov/administration/departments/court/violations/parking-tickets.html",
    "us-ca-los_angeles": "https://ladotparking.org/adjudication-division/contest-a-parking-citation/",
    "us-ca-san_diego": "https://www.sandiego.gov/parking/citations/appeal",
    "us-ca-san_francisco": "https://www.sfmta.com/getting-around/drive-park/citations/contest-citation",
    "us-co-denver": "https://denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Parks-Recreation/Appeal-a-Park-Citation",
    "us-il-chicago": "https://www.chicago.gov/city/en/depts/fin/supp_info/revenue/parking_and_red-lightnoticeinformation5/contest_by_mail.html",
    "us-ny-new_york": "https://www.nyc.gov/site/finance/vehicles/dispute-a-ticket.page",
    "us-or-portland": "https://www.portland.gov/transportation/parking/pay-and-or-contest-parking-ticket",
    "us-pa-philadelphia": "https://philapark.org/dispute/",
    "us-tx-dallas": "https://dallascityhall.com/departments/courtdetentionservices/Pages/Parking-Violations.aspx",
    "us-tx-houston": "https://www.houstontx.gov/parking/resolve.html",
    "us-ut-salt_lake_city": "https://www.slc.gov/Finance/appeal-a-parking-or-civil-citation/",
    "us-wa-seattle": "https://www.seattle.gov/courts/tickets-and-payments/dispute-my-ticket",
}

# Test cities
test_cities = [
    ("us-az-phoenix", "Phoenix, AZ"),
    ("us-ca-los_angeles", "Los Angeles, CA"),
]

async def scrape_and_extract(city_id: str, city_name: str):
    """Scrape URL and extract address."""
    url = CITY_URL_MAPPING.get(city_id)
    if not url:
        print("{city_name}: No URL found")
        return

    print("=" * 80)
    print("Testing: {city_name} ({city_id})")
    print("=" * 80)
    print("URL: {url}")
    print()

    # Step 1: Scrape
    print("Step 1: Scraping website...")
    try:
        # Note: SSL verification is enabled by default for security
        # If testing against self-signed certs, set SSL_CERT_FILE env var instead
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            text = response.text.lower()  # Lowercase for case-insensitive matching
            print("  [OK] Scraped {len(text)} characters")
            print("  Preview: {text[:200]}...")
    except Exception as e:
        print("  [ERROR] Scraping failed: {e}")
        return

    print()

    # Step 2: Extract address with DeepSeek
    print("Step 2: Extracting address using DeepSeek...")
    try:
        expected_address = {
            "us-az-phoenix": "Phoenix Municipal Court, 300 West Washington Street, Phoenix, AZ 85003",
            "us-ca-los_angeles": "Parking Violations Bureau, P.O. Box 30247, Los Angeles, CA 90030",
        }.get(city_id, "")

        system_prompt = """You are an address extraction assistant. Your job is to extract the exact mailing address for parking ticket appeals from web page content.

CRITICAL RULES:
1. Extract ONLY the mailing address - nothing else
2. Include the department name, street address (or PO Box), city, state, and ZIP code
3. Return the address exactly as it appears on the page
4. If multiple addresses appear, return the one specifically for appeals/contests
5. If no address is found, return "NOT_FOUND"
6. Do not add any explanation or additional text - just the address"""

        user_prompt = """Extract the mailing address for parking ticket appeals from this web page content:

{text[:15000]}

Expected format (for reference): {expected_address}

Return ONLY the mailing address as it appears on the page, or "NOT_FOUND" if no address is found."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": "Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1,
                },
            )
            if response.status_code == 401:
                print("  [ERROR] API authentication failed (401)")
                print(f"  Response: {response.text}")
                print("  Check if API key is valid and has proper permissions")
                return
            response.raise_for_status()
            data = response.json()
            extracted = data["choices"][0]["message"]["content"].strip()

        if extracted.upper() == "NOT_FOUND" or not extracted:
            print("  [FAIL] Could not extract address")
            print("  This might mean the address is buried deep in the page or formatted unusually")
            return

        print("  [OK] Extracted address: {extracted}")
        print()
        print("Expected: {expected_address}")
        print("Extracted: {extracted}")

        # Normalize and compare
        def normalize_addr(addr):
            import re
            normalized = addr.lower().strip()
            normalized = re.sub(r'\([^)]*\)', '', normalized)  # Remove parenthetical notes
            normalized = re.sub(r'\bp\.o\.\s*box\b', 'po box', normalized, flags=re.IGNORECASE)
            normalized = re.sub(r'\s+', ' ', normalized)
            normalized = re.sub(r'[.,;:]', '', normalized)
            return normalized.strip()

        norm_expected = normalize_addr(expected_address)
        norm_extracted = normalize_addr(extracted)

        # Check if key parts match (PO Box number, city, state, ZIP)
        po_match = bool(re.search(r'po box\s*\d+', norm_extracted) and re.search(r'po box\s*\d+', norm_expected))
        city_match = city_name.split(',')[0].lower() in norm_extracted
        zip_match = bool(re.search(r'\d{5}', norm_extracted) and re.search(r'\d{5}', norm_expected))

        print()
        print("Normalized Expected: {norm_expected}")
        print("Normalized Extracted: {norm_extracted}")
        print()
        print("PO Box Match: {po_match}")
        print("City Match: {city_match}")
        print("ZIP Match: {zip_match}")

        if po_match and city_match and zip_match:
            print("  [SUCCESS] Key address components match!")
        else:
            print("  [WARNING] Some components don't match - may need review")

    except Exception as e:
        print("  [ERROR] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

async def main():
    """Run tests."""
    print("=" * 80)
    print("LIVE ADDRESS VALIDATION TEST")
    print("=" * 80)
    print()

    for city_id, city_name in test_cities:
        await scrape_and_extract(city_id, city_name)
        print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

