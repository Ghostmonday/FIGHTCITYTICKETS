
import sys
import pytest
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.citation import CitationValidator

class TestBostonConfig:
    def setup_method(self):
        self.cities_dir = Path(__file__).parent.parent / "cities"
        self.validator = CitationValidator(cities_dir=self.cities_dir)

    def test_boston_parking_citation(self):
        # Boston Parking Commission citation: BO + 7 digits
        citation = "BO1234567"

        validation = self.validator.validate_citation(citation)

        assert validation.is_valid
        assert validation.city_id == "us-ma-boston"
        assert validation.section_id == "parking"

        # Check special requirements
        reqs = validation.special_requirements
        assert reqs is not None
        assert reqs["representative_checkbox_enabled"] is True
        assert reqs["digital_signature_accepted"] is True
        assert "Massachusetts state law" in reqs["digital_signature_notes"]

    def test_boston_police_citation(self):
        # Boston Police Department citation: BPD + 6 digits
        citation = "BPD123456"

        validation = self.validator.validate_citation(citation)

        assert validation.is_valid
        assert validation.city_id == "us-ma-boston"
        assert validation.section_id == "police"

        # Check special requirements
        reqs = validation.special_requirements
        assert reqs is not None
        assert reqs["representative_checkbox_enabled"] is True
        # Police section might differ slightly
        assert reqs["digital_signature_accepted"] is True

    def test_citation_info_includes_requirements(self):
        citation = "BO1234567"
        info = self.validator.get_citation_info(citation)

        assert info.city_id == "us-ma-boston"
        assert info.special_requirements is not None
        assert info.special_requirements["representative_checkbox_enabled"] is True

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
