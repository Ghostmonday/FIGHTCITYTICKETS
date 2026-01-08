"""
Script to check current addresses in city JSON files against the updated list.
"""

import json
from pathlib import Path

# Expected addresses from user-provided list
EXPECTED_ADDRESSES = {
    "us-az-phoenix": "Phoenix Municipal Court, 300 West Washington Street, Phoenix, AZ 85003",
    "us-ca-los_angeles": "Parking Violations Bureau, P.O. Box 30247, Los Angeles, CA 90030",
    "us-ca-san_diego": "PO Box 129038, San Diego, CA 92112-9038",
    "us-ca-san_francisco": "SFMTA Customer Service Center, ATTN: Citation Review, 11 South Van Ness Avenue, San Francisco, CA 94103",
    "us-co-denver": "Denver Parks and Recreation, Manager of Finance, Denver Post Building, 101 West Colfax Ave, 9th Floor, Denver, CO 80202",
    "us-il-chicago": "Department of Finance, City of Chicago, P.O. Box 88292, Chicago, IL 60680-1292 (send signed statement with facts for defense)",
    "us-ny-new_york": "New York City Department of Finance, Adjudications Division, Parking Ticket Transcript Processing, 66 John Street, 3rd Floor, New York, NY 10038",
    "us-or-portland": "Multnomah County Circuit Court, Parking Citation Office, P.O. Box 78, Portland, OR 97207",
    "us-pa-philadelphia": "Bureau of Administrative Adjudication, 48 N. 8th Street, Philadelphia, PA 19107",
    "us-tx-dallas": "City of Dallas, Parking Adjudication Office, 2014 Main Street, Dallas, TX 75201-4406",
    "us-tx-houston": "Parking Adjudication Office, Municipal Courts, 1400 Lubbock, Houston, TX 77002",
    "us-ut-salt_lake_city": "Salt Lake City Corporation, P.O. Box 145580, Salt Lake City, UT 84114-5580 (no direct mail appeal listed, use this for payments while appealing online or in person)",
    "us-wa-seattle": "Seattle Municipal Court, PO Box 34987, Seattle, WA 98124-4987",
}

# City ID to JSON file mapping
CITY_FILE_MAP = {
    "us-az-phoenix": "us-az-phoenix.json",
    "us-ca-los_angeles": "us-ca-los_angeles.json",
    "us-ca-san_diego": "us-ca-san_diego.json",
    "us-ca-san_francisco": "us-ca-san_francisco.json",
    "us-co-denver": "us-co-denver.json",
    "us-il-chicago": "us-il-chicago.json",
    "us-ny-new_york": "us-ny-new_york.json",
    "us-or-portland": "us-or-portland.json",
    "us-pa-philadelphia": "us-pa-philadelphia.json",
    "us-tx-dallas": "us-tx-dallas.json",
    "us-tx-houston": "us-tx-houston.json",
    "us-ut-salt_lake_city": "us-ut-salt_lake_city.json",
    "us-wa-seattle": "us-wa-seattle.json",
}


def get_stored_address(city_file: Path) -> str:
    """Extract stored address from city JSON file."""
    try:
        with open(city_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        addr = data.get("appeal_mail_address", {})
        if not addr or addr.get("status") != "complete":
            return "MISSING OR INCOMPLETE"

        parts = []
        if addr.get("department"):
            parts.append(addr["department"])
        if addr.get("attention"):
            parts.append("ATTN: {addr['attention']}")
        if addr.get("address1"):
            parts.append(addr["address1"])
        if addr.get("address2"):
            parts.append(addr["address2"])
        if addr.get("city"):
            parts.append(addr["city"])
        if addr.get("state"):
            parts.append(addr["state"])
        if addr.get("zip"):
            parts.append(addr["zip"])

        return ", ".join(parts) if parts else "EMPTY"
    except Exception as e:
        return "ERROR: {e}"


def normalize_address(addr: str) -> str:
    """Normalize address for comparison."""
    import re
    normalized = addr.lower().strip()
    # Remove parenthetical notes
    normalized = re.sub(r'\([^)]*\)', '', normalized)
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip()


def main():
    """Check all addresses."""
    # Get cities directory - script is in backend/scripts/, cities is at root level
    script_dir = Path(__file__).parent
    cities_dir = script_dir.parent.parent.parent / "cities"

    if not cities_dir.exists():
        # Try alternative path
        cities_dir = script_dir.parent.parent / "cities"

    print("Looking for cities in: {cities_dir}")
    print("Directory exists: {cities_dir.exists()}")
    if cities_dir.exists():
        print("Files found: {list(cities_dir.glob('*.json'))[:5]}...")
    print()

    print("=" * 80)
    print("ADDRESS COMPARISON REPORT")
    print("=" * 80)
    print()

    matches = []
    mismatches = []
    missing = []

    for city_id, expected in EXPECTED_ADDRESSES.items():
        json_file = cities_dir / CITY_FILE_MAP[city_id]

        if not json_file.exists():
            missing.append((city_id, "FILE NOT FOUND"))
            continue

        stored = get_stored_address(json_file)

        # Normalize for comparison
        norm_expected = normalize_address(expected)
        norm_stored = normalize_address(stored)

        # Check if they match (allowing for minor variations)
        if norm_expected == norm_stored or norm_expected in norm_stored or norm_stored in norm_expected:
            matches.append((city_id, stored, expected))
        else:
            mismatches.append((city_id, stored, expected))

    print("[OK] MATCHES: {len(matches)}")
    print("[X] MISMATCHES: {len(mismatches)}")
    print("[!] MISSING FILES: {len(missing)}")
    print()

    if matches:
        print("=" * 80)
        print("MATCHING ADDRESSES:")
        print("=" * 80)
        for city_id, stored, expected in matches:
            print("\n{city_id}:")
            print("  Stored:   {stored}")
            print("  Expected: {expected}")

    if mismatches:
        print("\n" + "=" * 80)
        print("MISMATCHING ADDRESSES (WILL BE UPDATED BY VALIDATOR):")
        print("=" * 80)
        for city_id, stored, expected in mismatches:
            print("\n{city_id}:")
            print("  Stored:   {stored}")
            print("  Expected: {expected}")

    if missing:
        print("\n" + "=" * 80)
        print("MISSING FILES:")
        print("=" * 80)
        for city_id, reason in missing:
            print("  {city_id}: {reason}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Total cities checked: {len(EXPECTED_ADDRESSES)}")
    print("Matches: {len(matches)}")
    print("Mismatches: {len(mismatches)}")
    print("Missing: {len(missing)}")
    print()
    print("Note: Mismatches will be automatically updated by the address validator")
    print("when appeals are sent, after scraping the city websites.")


if __name__ == "__main__":
    main()

