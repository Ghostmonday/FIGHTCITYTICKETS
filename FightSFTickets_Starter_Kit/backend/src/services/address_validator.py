"""
Address Validation Service for FightSFTickets.com

Validates mailing addresses by scraping city websites in real-time using DeepSeek.
Compares scraped addresses with stored addresses and updates database if they differ.
"""

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import httpx

from ..config import settings
from .city_registry import get_city_registry

# Set up logger
logger = logging.getLogger(__name__)

# City ID to URL mapping from user-provided list
CITY_URL_MAPPING: Dict[str, str] = {
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

# Expected addresses from user-provided list (for comparison)
EXPECTED_ADDRESSES: Dict[str, str] = {
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


@dataclass
class AddressValidationResult:
    """Result of address validation."""
    is_valid: bool
    city_id: str
    stored_address: Optional[str] = None
    scraped_address: Optional[str] = None
    error_message: Optional[str] = None
    was_updated: bool = False


class AddressValidator:
    """Service for validating addresses by scraping city websites."""

    def __init__(self, cities_dir: Optional[Path] = None):
        """Initialize address validator."""
        import os
        # Check environment variable first, then settings
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.is_available = bool(self.api_key and self.api_key != "change-me" and self.api_key != "sk_dummy")

        # Initialize city registry
        if cities_dir is None:
            cities_dir = Path(__file__).parent.parent.parent.parent / "cities"
        self.cities_dir = Path(cities_dir) if isinstance(cities_dir, str) else cities_dir
        self.city_registry = get_city_registry(self.cities_dir)

    def _normalize_address(self, address: str) -> str:
        """
        Normalize an address for comparison.

        Removes extra whitespace, normalizes common abbreviations, etc.
        """
        if not address:
            return ""

        # Convert to lowercase
        normalized = address.lower().strip()

        # Normalize common abbreviations
        replacements = {
            r'\bp\.o\.\s*box\b': 'po box',
            r'\bp\.o\s*box\b': 'po box',
            r'\bpo\s*box\b': 'po box',
            r'\bstreet\b': 'st',
            r'\bavenue\b': 'ave',
            r'\bdrive\b': 'dr',
            r'\broad\b': 'rd',
            r'\blane\b': 'ln',
            r'\bboulevard\b': 'blvd',
            r'\bnorth\b': 'n',
            r'\bsouth\b': 's',
            r'\beast\b': 'e',
            r'\bwest\b': 'w',
            r'\bfloor\b': 'fl',
            r'\battn\b': 'attn',
            r'\battention\b': 'attn',
        }

        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

        # Remove extra whitespace and punctuation variations
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = re.sub(r'[.,;:]', '', normalized)

        return normalized.strip()

    async def _extract_address_from_text(self, text: str, city_id: str) -> Optional[str]:
        """
        Extract mailing address from scraped text using DeepSeek.

        Returns the extracted address string or None if not found.
        """
        if not self.is_available:
            logger.warning("DeepSeek API not available for address extraction")
            return None

        expected_address = EXPECTED_ADDRESSES.get(city_id, "")

        # Normalize text to lowercase for case-insensitive matching
        text = text.lower()

        system_prompt = """You are an address extraction assistant. Your job is to extract the exact mailing address for parking ticket appeals from web page content.

CRITICAL RULES:
1. Extract ONLY the mailing address - nothing else
2. Include the department name, street address (or PO Box), city, state, and ZIP code
3. Return the address exactly as it appears on the page
4. If multiple addresses appear, return the one specifically for appeals/contests
5. If no address is found, return "NOT_FOUND"
6. Do not add any explanation or additional text - just the address"""

        user_prompt = """Extract the mailing address for parking ticket appeals from this web page content:

{text[:15000]}  # Limit to avoid token limits

Expected format (for reference): {expected_address}

Return ONLY the mailing address as it appears on the page, or "NOT_FOUND" if no address is found."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": 500,
                        "temperature": 0.1,  # Very low temperature for accuracy
                    },
                )
                response.raise_for_status()
                data = response.json()
                extracted = data["choices"][0]["message"]["content"].strip()

            if extracted.upper() == "NOT_FOUND" or not extracted:
                return None

            return extracted.strip()

        except Exception as e:
            logger.error("Error extracting address with DeepSeek: {e}")
            return None

    async def _scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape raw text content from a URL.

        Returns the raw text content or None if scraping fails.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                # For PDF files, we'd need special handling, but for now just return text
                content_type = response.headers.get("content-type", "").lower()
                if "pd" in content_type:
                    logger.warning(f"PDF file detected at {url} - PDF parsing not implemented")
                    return None

                return response.text

        except Exception as e:
            logger.error("Error scraping URL {url}: {e}")
            return None

    def _get_stored_address_string(self, city_id: str, section_id: Optional[str] = None) -> Optional[str]:
        """
        Get the stored address as a normalized string for comparison.

        Returns the address as a single string or None if not found.
        """
        mail_address = self.city_registry.get_mail_address(city_id, section_id)
        if not mail_address or mail_address.status.value != "complete":
            return None

        # Build address string
        parts = []
        if mail_address.department:
            parts.append(mail_address.department)
        if mail_address.attention:
            parts.append("ATTN: {mail_address.attention}")
        if mail_address.address1:
            parts.append(mail_address.address1)
        if mail_address.address2:
            parts.append(mail_address.address2)
        if mail_address.city:
            parts.append(mail_address.city)
        if mail_address.state:
            parts.append(mail_address.state)
        if mail_address.zip:
            parts.append(mail_address.zip)

        return ", ".join(parts) if parts else None

    def _addresses_match(self, stored: str, scraped: str) -> bool:
        """
        Check if two addresses match exactly (after normalization).

        Returns True if addresses match, False otherwise.
        """
        if not stored or not scraped:
            return False

        normalized_stored = self._normalize_address(stored)
        normalized_scraped = self._normalize_address(scraped)

        # Exact match after normalization
        return normalized_stored == normalized_scraped

    def _update_city_json(self, city_id: str, new_address: str, section_id: Optional[str] = None) -> bool:
        """
        Update the city JSON file with the new address.

        Returns True if update was successful, False otherwise.
        """
        try:
            # Find the JSON file for this city
            json_files = list(self.cities_dir.glob("{city_id}.json"))
            if not json_files:
                # Try alternative naming
                city_name_map = {
                    "us-az-phoenix": "phoenix.json",
                    "us-ca-los_angeles": "la.json",
                    "us-ca-san_diego": "sandiego.json",
                    "us-ca-san_francisco": "us-ca-san_francisco.json",
                    "us-co-denver": "denver.json",
                    "us-il-chicago": "chicago.json",
                    "us-ny-new_york": "nyc.json",
                    "us-or-portland": "portland.json",
                    "us-pa-philadelphia": "philadelphia.json",
                    "us-tx-dallas": "dallas.json",
                    "us-tx-houston": "houston.json",
                    "us-ut-salt_lake_city": "salt_lake_city.json",
                    "us-wa-seattle": "seattle.json",
                }
                alt_name = city_name_map.get(city_id)
                if alt_name:
                    json_files = list(self.cities_dir.glob(alt_name))

            if not json_files:
                logger.error("Could not find JSON file for city_id: {city_id}")
                return False

            json_file = json_files[0]

            # Load the JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Parse the new address to extract components
            # This is a simplified parser - in production you might want more robust parsing
            address_parts = self._parse_address_string(new_address)

            # Update the address in the JSON structure
            if section_id and section_id in data.get("sections", {}):
                # Update section address
                section = data["sections"][section_id]
                if "appeal_mail_address" in section:
                    section["appeal_mail_address"].update({
                        "status": "complete",
                        "department": address_parts.get("department", ""),
                        "attention": address_parts.get("attention", ""),
                        "address1": address_parts.get("address1", ""),
                        "address2": address_parts.get("address2", ""),
                        "city": address_parts.get("city", ""),
                        "state": address_parts.get("state", ""),
                        "zip": address_parts.get("zip", ""),
                        "country": address_parts.get("country", "US"),
                    })
            else:
                # Update main city address
                if "appeal_mail_address" in data:
                    data["appeal_mail_address"].update({
                        "status": "complete",
                        "department": address_parts.get("department", ""),
                        "attention": address_parts.get("attention", ""),
                        "address1": address_parts.get("address1", ""),
                        "address2": address_parts.get("address2", ""),
                        "city": address_parts.get("city", ""),
                        "state": address_parts.get("state", ""),
                        "zip": address_parts.get("zip", ""),
                        "country": address_parts.get("country", "US"),
                    })

            # Save the updated JSON file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info("Updated address in {json_file} for city_id: {city_id}")

            # Reload the city registry to pick up changes
            self.city_registry.load_cities()

            return True

        except Exception as e:
            logger.error("Error updating city JSON for {city_id}: {e}")
            return False

    def _parse_address_string(self, address: str) -> Dict[str, str]:
        """
        Parse an address string into components.

        This is a simplified parser - you may want to use a more robust library.
        """
        parts = {
            "department": "",
            "attention": "",
            "address1": "",
            "address2": "",
            "city": "",
            "state": "",
            "zip": "",
            "country": "US",
        }

        # Extract ATTN/Attention
        attn_match = re.search(r'attn[:\s]+([^,]+)', address, re.IGNORECASE)
        if attn_match:
            parts["attention"] = attn_match.group(1).strip()

        # Extract state and ZIP (format: "City, ST ZIP")
        state_zip_match = re.search(r',\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)', address, re.IGNORECASE)
        if state_zip_match:
            parts["state"] = state_zip_match.group(1).upper()
            parts["zip"] = state_zip_match.group(2)

        # Extract city (before state)
        if parts["state"]:
            city_match = re.search(r',\s*([^,]+?),\s*' + parts["state"], address, re.IGNORECASE)
            if city_match:
                parts["city"] = city_match.group(1).strip()

        # Extract PO Box or street address
        po_box_match = re.search(r'(po\s*box\s*\d+[^,]*|p\.o\.\s*box\s*\d+[^,]*)', address, re.IGNORECASE)
        if po_box_match:
            parts["address1"] = po_box_match.group(0).strip()
        else:
            # Try to extract street address (number + street name)
            street_match = re.search(r'(\d+\s+[^,]+(?:street|st|avenue|ave|drive|dr|road|rd|boulevard|blvd|parkway|pkwy)[^,]*)', address, re.IGNORECASE)
            if street_match:
                parts["address1"] = street_match.group(0).strip()

        # Extract department (usually at the beginning)
        if parts["address1"]:
            dept_end = address.find(parts["address1"])
            if dept_end > 0:
                dept_part = address[:dept_end].strip()
                # Remove ATTN if present
                dept_part = re.sub(r'attn[:\s]+[^,]+', '', dept_part, flags=re.IGNORECASE).strip()
                if dept_part:
                    parts["department"] = dept_part.rstrip(',').strip()

        # Extract address2 (floor, suite, etc.)
        floor_match = re.search(r'(\d+(?:st|nd|rd|th)\s+floor|floor\s+\d+)', address, re.IGNORECASE)
        if floor_match:
            parts["address2"] = floor_match.group(0).strip()

        return parts

    async def validate_address(self, city_id: str, section_id: Optional[str] = None) -> AddressValidationResult:
        """
        Validate the address for a city by scraping the website and comparing.

        Args:
            city_id: City identifier
            section_id: Optional section identifier

        Returns:
            AddressValidationResult with validation status
        """
        if city_id not in CITY_URL_MAPPING:
            return AddressValidationResult(
                is_valid=False,
                city_id=city_id,
                error_message="No URL mapping found for city_id: {city_id}"
            )

        url = CITY_URL_MAPPING[city_id]
        stored_address = self._get_stored_address_string(city_id, section_id)

        if not stored_address:
            return AddressValidationResult(
                is_valid=False,
                city_id=city_id,
                error_message="No stored address found for city_id: {city_id}"
            )

        # Scrape the URL
        scraped_text = await self._scrape_url(url)
        if not scraped_text:
            return AddressValidationResult(
                is_valid=False,
                city_id=city_id,
                stored_address=stored_address,
                error_message="Failed to scrape URL: {url}"
            )

        # Extract address from scraped text
        scraped_address = await self._extract_address_from_text(scraped_text, city_id)
        if not scraped_address:
            return AddressValidationResult(
                is_valid=False,
                city_id=city_id,
                stored_address=stored_address,
                error_message="Could not extract address from scraped content"
            )

        # Compare addresses
        addresses_match = self._addresses_match(stored_address, scraped_address)

        if addresses_match:
            return AddressValidationResult(
                is_valid=True,
                city_id=city_id,
                stored_address=stored_address,
                scraped_address=scraped_address
            )

        # Addresses don't match - update the database
        logger.warning(
            "Address mismatch for {city_id}: stored='{stored_address}', scraped='{scraped_address}'"
        )

        update_success = self._update_city_json(city_id, scraped_address, section_id)

        return AddressValidationResult(
            is_valid=False,
            city_id=city_id,
            stored_address=stored_address,
            scraped_address=scraped_address,
            was_updated=update_success,
            error_message="Address mismatch detected and updated" if update_success else "Address mismatch detected but update failed"
        )


# Global service instance
_validator = None


def get_address_validator(cities_dir: Optional[Path] = None) -> AddressValidator:
    """Get the global address validator instance."""
    global _validator
    if _validator is None:
        _validator = AddressValidator(cities_dir)
    return _validator

