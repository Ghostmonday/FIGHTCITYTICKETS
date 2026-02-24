import json
import shutil
import tempfile
import sys
from pathlib import Path

# Add backend directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.address_validator import AddressValidator

def test_manual_override():
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Created temp dir: {temp_dir}")
    try:
        # Create a mock city JSON
        city_id = "us-test-city"
        city_data = {
            "city_id": city_id,
            "name": "Test City",
            "jurisdiction": "city",
            "citation_patterns": [{"regex": "^T\\d+", "section_id": "main", "description": "Test"}],
            "appeal_mail_address": {
                "status": "complete",
                "department": "Old Dept",
                "address1": "123 Old St",
                "city": "Old City",
                "state": "TS",
                "zip": "00000",
                "country": "US"
            },
            "phone_confirmation_policy": {"required": False},
            "routing_rule": "direct",
            "sections": {
                "main": {
                    "section_id": "main",
                    "name": "Main",
                    "routing_rule": "direct"
                }
            },
            "verification_metadata": {
                "last_updated": "2024-01-01",
                "source": "test",
                "confidence_score": 1.0
            }
        }

        json_path = temp_dir / f"{city_id}.json"
        with open(json_path, 'w') as f:
            json.dump(city_data, f)

        # Initialize validator
        try:
            validator = AddressValidator(cities_dir=temp_dir)
        except Exception as e:
            print(f"FAIL: Failed to initialize AddressValidator: {e}")
            import traceback
            traceback.print_exc()
            return

        print("\nTesting manual update with string...")
        # 1. Test update with string (parsing)
        new_address_str = "New Dept, 456 New St, New City, TS 11111"
        try:
            validator.update_city_address(city_id, new_address_str)

            # Verify update
            with open(json_path, 'r') as f:
                data = json.load(f)
            addr = data["appeal_mail_address"]
            if addr["address1"] == "456 New St" and addr["city"] == "New City":
                print("PASS: String update successful")
            else:
                print(f"FAIL: String update failed. Got: {addr}")
        except AttributeError:
             print("FAIL: update_city_address method not found (expected initially)")
        except Exception as e:
             print(f"FAIL: String update raised exception: {e}")

        print("\nTesting manual update with dict...")
        # 2. Test update with dict
        new_address_dict = {
            "department": "Manual Dept",
            "address1": "789 Manual Ave",
            "city": "Manual City",
            "state": "TS",
            "zip": "22222",
            "country": "US"
        }
        try:
            validator.update_city_address(city_id, new_address_dict)

            # Verify update
            with open(json_path, 'r') as f:
                data = json.load(f)
            addr = data["appeal_mail_address"]
            if addr["address1"] == "789 Manual Ave" and addr["city"] == "Manual City":
                print("PASS: Dict update successful")
            else:
                print(f"FAIL: Dict update failed. Got: {addr}")
        except AttributeError:
             print("FAIL: update_city_address method not found (expected initially)")
        except Exception as e:
             print(f"FAIL: Dict update raised exception: {e}")

    finally:
        shutil.rmtree(temp_dir)
        print(f"\nRemoved temp dir: {temp_dir}")

if __name__ == "__main__":
    test_manual_override()
