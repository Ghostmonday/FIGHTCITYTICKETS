#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Lob Campaign CSV from Database

This script queries the database for paid but unfulfilled appeals
and generates a CSV file ready for Lob Campaign upload.

✨ AUTOMATIC MULTI-CITY SUPPORT:
   - Automatically detects cities from citation numbers via city_registry
   - New cities added to cities/ directory are automatically supported
   - No code changes needed when adding new cities!
   - Uses city registry to match citations to correct mailing addresses
"""

import csv
import sys
import os
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variable for database connection if running locally
if 'DATABASE_URL' not in os.environ:
    # Try to use local database connection
    os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/fights')

from src.services.database import DatabaseService
from src.services.mail import LobMailService
from src.models import Payment, PaymentStatus, Intake, Draft

def generate_lob_csv(output_file: str = "lob_campaign_audience.csv"):
    """Generate Lob campaign CSV from database."""

    # Initialize services
    db = DatabaseService()
    mail_service = LobMailService()

    print("🔍 Querying database for paid but unfulfilled appeals...")

    with db.get_session() as session:
        # Query for paid but unfulfilled payments
        payments = (
            session.query(Payment)
            .join(Intake)
            .join(Draft, (Draft.intake_id == Intake.id) & (Draft.appeal_type == Payment.appeal_type))
            .filter(Payment.status == PaymentStatus.PAID)
            .filter(Payment.is_fulfilled.is_(False))
            .filter(Draft.draft_text.isnot(None))
            .all()
        )

        print(f"✅ Found {len(payments)} appeals ready for mailing")

        if not payments:
            print("⚠️  No appeals found. CSV file will be empty.")
            # Create empty CSV with headers
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'name', 'address_line1', 'address_line2', 'address_city',
                    'address_state', 'address_zip', 'address_country',
                    'citation_number', 'appeal_type', 'letter_text',
                    'user_name', 'user_address_line1', 'user_address_line2',
                    'user_city', 'user_state', 'user_zip',
                    'violation_date', 'license_plate'
                ])
            print(f"📄 Created empty CSV: {output_file}")
            return

        # Prepare CSV rows
        rows = []

        for payment in payments:
            intake = payment.intake
            draft = (
                session.query(Draft)
                .filter(Draft.intake_id == intake.id)
                .filter(Draft.appeal_type == payment.appeal_type)
                .first()
            )

            if not draft or not draft.draft_text:
                print(f"⚠️  Skipping payment {payment.id}: No draft text found")
                continue

            # Get agency mailing address
            # This automatically supports all cities via city_registry
            # New cities added to cities/ directory will be automatically detected
            city_id = None
            section_id = None

            # Try to match citation to city via city registry
            if mail_service.city_registry:
                try:
                    match = mail_service.city_registry.match_citation(intake.citation_number)
                    if match:
                        city_id, section_id = match
                        print(f"📍 Matched citation {intake.citation_number} to city_id={city_id}, section_id={section_id}")
                except Exception as e:
                    print(f"⚠️  Citation matching failed for {intake.citation_number}: {e}")

            try:
                agency_address = mail_service._get_agency_address(
                    intake.citation_number,
                    city_id=city_id,  # Will use city registry if available
                    section_id=section_id
                )
            except Exception as e:
                print(f"⚠️  Error getting address for citation {intake.citation_number}: {e}")
                # Use default SFMTA address as fallback
                from src.services.mail import MailingAddress
                agency_address = MailingAddress(
                    name="SFMTA Citation Review",
                    address_line1="1 South Van Ness Avenue",
                    address_line2="Floor 7",
                    city="San Francisco",
                    state="CA",
                    zip_code="94103"
                )

            # Prepare letter text - escape newlines for CSV
            letter_text = draft.draft_text.replace('\n', '\\n').replace('\r', '')

            # Truncate name if too long (Lob limit: 40 chars)
            recipient_name = agency_address.name[:40]

            # Truncate address_line1 if too long (Lob limit: 64 chars)
            address_line1 = agency_address.address_line1[:64]

            # Truncate address_line2 if too long (Lob limit: 64 chars)
            address_line2 = (agency_address.address_line2 or "")[:64]

            # Truncate city if too long (Lob limit: 200 chars)
            address_city = agency_address.city[:200]

            # Truncate user name if too long (Lob limit: 40 chars for return address)
            user_name = intake.user_name[:40]

            # Truncate user address_line1 if too long (Lob limit: 64 chars)
            user_address_line1 = intake.user_address_line1[:64]

            # Truncate user address_line2 if too long (Lob limit: 64 chars)
            user_address_line2 = (intake.user_address_line2 or "")[:64]

            # Ensure ZIP code preserves leading zeros (format as string)
            recipient_zip = str(agency_address.zip_code).zfill(5)
            user_zip = str(intake.user_zip).zfill(5)

            # Create row
            row = [
                recipient_name,                    # name
                address_line1,                      # address_line1
                address_line2,                      # address_line2
                address_city,                       # address_city
                agency_address.state,               # address_state
                recipient_zip,                     # address_zip
                'US',                              # address_country
                intake.citation_number,            # citation_number
                payment.appeal_type.value,         # appeal_type
                letter_text,                       # letter_text
                user_name,                         # user_name
                user_address_line1,                 # user_address_line1
                user_address_line2,                 # user_address_line2
                intake.user_city,                  # user_city
                intake.user_state,                 # user_state
                user_zip,                          # user_zip
                intake.violation_date or '',       # violation_date
                intake.license_plate or '',        # license_plate
                city_id or '',                     # city_id (for tracking)
                section_id or '',                  # section_id (for tracking)
            ]

            rows.append(row)
            print(f"✅ Added appeal for citation {intake.citation_number}")

        # Write CSV file
        print(f"\n📝 Writing CSV file: {output_file}")

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                'name', 'address_line1', 'address_line2', 'address_city',
                'address_state', 'address_zip', 'address_country',
                'citation_number', 'appeal_type', 'letter_text',
                'user_name', 'user_address_line1', 'user_address_line2',
                'user_city', 'user_state', 'user_zip',
                'violation_date', 'license_plate', 'city_id', 'section_id'
            ])

            # Write data rows
            writer.writerows(rows)

        print(f"✅ Successfully generated CSV with {len(rows)} recipients")
        print(f"📄 File saved to: {output_file}")
        print("\n✨ Multi-City Support:")
        print("   - Automatically detected cities from citations")
        print("   - New cities in cities/ directory are automatically supported")
        print("   - No code changes needed when adding cities!")
        print("\n📋 Next steps:")
        print("   1. Review the CSV file")
        print("   2. Upload to Lob Dashboard > Campaigns > Step 2: Add Audience")
        print("   3. Map columns to Lob fields and merge variables")
        print("   4. Configure return address (single or personalized)")

if __name__ == "__main__":
    import os

    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    output_file = project_root / "lob_campaign_audience.csv"

    try:
        generate_lob_csv(str(output_file))
    except Exception as e:
        print(f"❌ Error generating CSV: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

