#!/usr/bin/env python3
"""
Store Stripe credentials in ProtonPass format and update .env file
"""
import os
import json
import secrets
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path("/home/evan/Documents/FightCityTickets")
ENV_FILE = PROJECT_ROOT / ".env"
PROTONPASS_DIR = Path("/home/evan/Documents/ProtonPass")
CREDENTIALS_FILE = PROTONPASS_DIR / "stripe_credentials.json"
BACKUP_FILE = PROTONPASS_DIR / f"stripe_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def get_input(prompt, secret=False, validate=None):
    """Get user input with optional validation"""
    if secret:
        import getpass
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()
    
    if validate and not validate(value):
        print(f"❌ Invalid format. Please try again.")
        return get_input(prompt, secret, validate)
    
    return value

def validate_stripe_secret_key(key):
    """Validate Stripe secret key format"""
    return key.startswith(("sk_live_", "sk_test_")) and len(key) > 20

def validate_stripe_publishable_key(key):
    """Validate Stripe publishable key format"""
    return key.startswith(("pk_live_", "pk_test_")) and len(key) > 20

def validate_webhook_secret(key):
    """Validate webhook secret format"""
    return key.startswith("whsec_") and len(key) > 20

def validate_price_id(price_id):
    """Validate Stripe price ID format"""
    return price_id.startswith("price_") and len(price_id) > 10

def update_env_file(credentials):
    """Update .env file with Stripe credentials"""
    if not ENV_FILE.exists():
        print(f"❌ .env file not found at {ENV_FILE}")
        return False
    
    # Read current .env
    with open(ENV_FILE, 'r') as f:
        lines = f.readlines()
    
    # Update Stripe-related lines
    updated_lines = []
    stripe_keys = {
        'STRIPE_SECRET_KEY': credentials['secret_key'],
        'STRIPE_PUBLISHABLE_KEY': credentials['publishable_key'],
        'STRIPE_WEBHOOK_SECRET': credentials['webhook_secret'],
        'STRIPE_PRICE_CERTIFIED': credentials['price_certified'],
    }
    
    keys_found = set()
    
    for line in lines:
        updated = False
        for key, value in stripe_keys.items():
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}\n")
                keys_found.add(key)
                updated = True
                break
        
        if not updated:
            updated_lines.append(line)
    
    # Add any missing keys
    for key, value in stripe_keys.items():
        if key not in keys_found:
            # Find where to insert (after STRIPE section comment)
            inserted = False
            for i, line in enumerate(updated_lines):
                if 'STRIPE PAYMENT PROCESSING' in line or 'STRIPE_PRICE_CERTIFIED' in line:
                    # Insert after this section
                    updated_lines.insert(i + 1, f"{key}={value}\n")
                    inserted = True
                    break
            if not inserted:
                updated_lines.append(f"{key}={value}\n")
    
    # Write back
    with open(ENV_FILE, 'w') as f:
        f.writelines(updated_lines)
    
    return True

def save_to_protonpass_format(credentials):
    """Save credentials in ProtonPass-compatible JSON format"""
    protonpass_entry = {
        "title": "FightCityTickets - Stripe Account",
        "url": "https://dashboard.stripe.com",
        "username": credentials.get('account_email', ''),
        "password": credentials['secret_key'],  # Most sensitive credential
        "notes": f"""Stripe Account Credentials for FightCityTickets

Account Email: {credentials.get('account_email', 'N/A')}
Account ID: {credentials.get('account_id', 'N/A')}
Country: {credentials.get('country', 'N/A')}

API Keys:
- Secret Key: {credentials['secret_key']}
- Publishable Key: {credentials['publishable_key']}
- Webhook Secret: {credentials['webhook_secret']}

Products:
- Certified Mail Price ID: {credentials['price_certified']}

Created: {datetime.now().isoformat()}
Environment: Production
""",
        "custom_fields": [
            {
                "name": "Secret Key",
                "value": credentials['secret_key'],
                "type": "password"
            },
            {
                "name": "Publishable Key",
                "value": credentials['publishable_key'],
                "type": "text"
            },
            {
                "name": "Webhook Secret",
                "value": credentials['webhook_secret'],
                "type": "password"
            },
            {
                "name": "Certified Price ID",
                "value": credentials['price_certified'],
                "type": "text"
            },
            {
                "name": "Account ID",
                "value": credentials.get('account_id', ''),
                "type": "text"
            }
        ],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Ensure ProtonPass directory exists
    PROTONPASS_DIR.mkdir(exist_ok=True)
    
    # Save to JSON file (ProtonPass import format)
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(protonpass_entry, f, indent=2)
    
    # Create backup
    with open(BACKUP_FILE, 'w') as f:
        json.dump(protonpass_entry, f, indent=2)
    
    return True

def main():
    print("=" * 60)
    print("🔐 STRIPE CREDENTIALS SETUP")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Collect your Stripe credentials")
    print("  2. Store them in ProtonPass format")
    print("  3. Update your .env file")
    print("  4. Create a backup")
    print("\n⚠️  Make sure you have:")
    print("  - Created your Stripe account")
    print("  - Activated your account")
    print("  - Created the Certified Mail product")
    print("  - Set up webhook endpoint")
    print()
    
    proceed = input("Continue? (yes/no): ").strip().lower()
    if proceed != 'yes':
        print("Cancelled.")
        return
    
    print("\n" + "=" * 60)
    print("📝 ENTER STRIPE CREDENTIALS")
    print("=" * 60)
    
    credentials = {}
    
    # Account email (optional)
    print("\n1. Account Information (optional):")
    credentials['account_email'] = input("   Stripe account email: ").strip()
    credentials['account_id'] = input("   Account ID (optional): ").strip()
    credentials['country'] = input("   Country (optional): ").strip()
    
    # API Keys
    print("\n2. API Keys (from Dashboard → Developers → API keys):")
    credentials['secret_key'] = get_input(
        "   Secret Key (sk_live_...): ",
        secret=True,
        validate=validate_stripe_secret_key
    )
    
    credentials['publishable_key'] = get_input(
        "   Publishable Key (pk_live_...): ",
        validate=validate_stripe_publishable_key
    )
    
    # Webhook Secret
    print("\n3. Webhook Configuration:")
    print("   (From Dashboard → Developers → Webhooks → [your endpoint] → Signing secret)")
    credentials['webhook_secret'] = get_input(
        "   Webhook Secret (whsec_...): ",
        secret=True,
        validate=validate_webhook_secret
    )
    
    # Price IDs
    print("\n4. Product Price IDs:")
    print("   (From Dashboard → Products → [Certified Mail] → Pricing → Price ID)")
    credentials['price_certified'] = get_input(
        "   Certified Mail Price ID (price_...): ",
        validate=validate_price_id
    )
    
    # Confirm
    print("\n" + "=" * 60)
    print("📋 REVIEW CREDENTIALS")
    print("=" * 60)
    print(f"Account Email: {credentials.get('account_email', 'N/A')}")
    print(f"Secret Key: {credentials['secret_key'][:15]}...")
    print(f"Publishable Key: {credentials['publishable_key'][:15]}...")
    print(f"Webhook Secret: {credentials['webhook_secret'][:15]}...")
    print(f"Certified Price ID: {credentials['price_certified']}")
    
    confirm = input("\n✅ Save these credentials? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled. No credentials saved.")
        return
    
    # Save to ProtonPass format
    print("\n💾 Saving credentials...")
    if save_to_protonpass_format(credentials):
        print(f"✅ Saved to: {CREDENTIALS_FILE}")
        print(f"✅ Backup created: {BACKUP_FILE}")
    
    # Update .env file
    print("\n📝 Updating .env file...")
    if update_env_file(credentials):
        print("✅ .env file updated")
    else:
        print("⚠️  Could not update .env file")
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("  1. Import credentials to ProtonPass:")
    print(f"     File: {CREDENTIALS_FILE}")
    print("  2. Verify .env file has correct values")
    print("  3. Test Stripe connection:")
    print("     python3 scripts/stripe_setup.py")
    print("  4. Test webhook endpoint after deployment")
    print()

if __name__ == "__main__":
    main()
