"""
Tests for Boston City Configuration.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.city_registry import get_city_registry
from src.services.citation import CitationValidator

class TestBostonConfiguration:
    """Test Boston city configuration."""

    def setup_method(self):
        """Set up test environment."""
        self.cities_dir = Path(__file__).parent.parent / "cities"
        self.registry = get_city_registry(self.cities_dir)
        self.validator = CitationValidator(self.cities_dir)
        self.city_id = "us-ma-boston"

    def test_boston_config_loaded(self):
        """Test that Boston configuration is loaded."""
        config = self.registry.get_city_config(self.city_id)
        assert config is not None
        assert config.name == "Boston"
        assert config.jurisdiction.value == "city"
        assert len(config.citation_patterns) >= 2

    def test_citation_matching_parking(self):
        """Test matching Boston Parking Commission citations."""
        # Pattern: ^BO\d{7,9}$
        citation = "BO1234567"
        match = self.registry.match_citation(citation)
        assert match is not None
        city_id, section_id = match
        assert city_id == self.city_id
        assert section_id == "parking"

        # Test validation
        validation = self.validator.validate_citation(citation)
        assert validation.is_valid
        assert validation.city_id == self.city_id
        assert validation.section_id == "parking"

    def test_citation_matching_police(self):
        """Test matching Boston Police Department citations."""
        # Pattern: ^BPD\d{6,8}$
        citation = "BPD123456"
        match = self.registry.match_citation(citation)
        assert match is not None
        city_id, section_id = match
        assert city_id == self.city_id
        assert section_id == "police"

        # Test validation
        validation = self.validator.validate_citation(citation)
        assert validation.is_valid
        assert validation.city_id == self.city_id
        assert validation.section_id == "police"

    def test_appeal_address_correctness(self):
        """Test that appeal address matches the P.O. Box."""
        config = self.registry.get_city_config(self.city_id)
        assert config.appeal_mail_address.status.value == "complete"
        assert config.appeal_mail_address.address1 == "P.O. Box 55800"
        assert config.appeal_mail_address.city == "Boston"
        assert config.appeal_mail_address.state == "MA"
        assert config.appeal_mail_address.zip == "02205"

    def test_parking_section_address(self):
        """Test parking section address."""
        address = self.registry.get_mail_address(self.city_id, "parking")
        assert address is not None
        assert address.address1 == "P.O. Box 55800"
        assert address.city == "Boston"
        assert address.zip == "02205"

    def test_police_section_address(self):
        """Test police section address."""
        address = self.registry.get_mail_address(self.city_id, "police")
        assert address is not None
        assert address.address1 == "P.O. Box 55800"
        assert address.city == "Boston"
        assert address.zip == "02205"

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
