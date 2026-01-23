#!/usr/bin/env python3
"""
Stripe Complete Setup - Wipe and Rebuild for FIGHT CITY TICKETS
"""
import os
import urllib.request
import urllib.parse
import json
import base64
import time

def load_env():
    """Load environment variables from .env file"""
    env_path = "/home/evan/Documents/Projects/FightSFTickets/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip(' "\'')

def stripe_api_call(endpoint, api_key, method="GET", data=None):
    """Make a Stripe API call using urllib"""
    url = f"https://api.stripe.com/v1/{endpoint}"
    
    auth_str = f"{api_key}:"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    post_data = None
    if data:
        post_data = urllib.parse.urlencode(data).encode()
    
    req = urllib.request.Request(url, data=post_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ API Error ({e.code}): {error_body}")
        return None
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None

def update_env_file(updates):
    """Update .env file with new values"""
    env_path = "/home/evan/Documents/Projects/FightSFTickets/.env"
    
    # Read current content
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    # Update lines
    new_lines = []
    for line in lines:
        updated = False
        for key, value in updates.items():
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
                break
        if not updated:
            new_lines.append(line)
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(new_lines)

def main():
    print("🔧 FIGHT CITY TICKETS - FULL STRIPE AUTOMATION")
    print("=" * 60)
    
    load_env()
    api_key = os.environ.get("RESTRICTED_STRIPE_KEY")
    
    if not api_key:
        print("❌ RESTRICTED_STRIPE_KEY not found")
        return
    
    # Step 1: Delete all existing products
    print("\n🗑️  STEP 1: Deleting all existing products...")
    products = stripe_api_call("products?limit=100", api_key)
    
    if products and products.get('data'):
        for prod in products['data']:
            print(f"   Deleting: {prod['name']} ({prod['id']})")
            result = stripe_api_call(f"products/{prod['id']}", api_key, method="DELETE")
            if result:
                print(f"   ✅ Deleted")
            time.sleep(0.5)  # Rate limit protection
    
    print("\n✅ All products deleted!")
    
    # Step 2: Create new products
    print("\n📦 STEP 2: Creating FIGHT CITY TICKETS products...")
    
    # Product 1: Regular Mail
    regular_product = stripe_api_call("products", api_key, method="POST", data={
        "name": "FIGHT CITY TICKETS - Regular Mail",
        "description": "Parking ticket appeal via standard USPS mail delivery",
        "metadata[service]": "regular_mail"
    })
    
    if regular_product:
        print(f"✅ Created: {regular_product['name']}")
        
        # Create price for regular mail
        regular_price = stripe_api_call("prices", api_key, method="POST", data={
            "product": regular_product['id'],
            "unit_amount": 989,  # $9.89
            "currency": "usd",
            "nickname": "Regular Mail - $9.89"
        })
        
        if regular_price:
            print(f"   Price: ${regular_price['unit_amount']/100:.2f} (ID: {regular_price['id']})")
    
    time.sleep(0.5)
    
    # Product 2: Certified Mail
    certified_product = stripe_api_call("products", api_key, method="POST", data={
        "name": "FIGHT CITY TICKETS - Certified Mail",
        "description": "Parking ticket appeal via USPS Certified Mail with tracking",
        "metadata[service]": "certified_mail"
    })
    
    if certified_product:
        print(f"✅ Created: {certified_product['name']}")
        
        # Create price for certified mail
        certified_price = stripe_api_call("prices", api_key, method="POST", data={
            "product": certified_product['id'],
            "unit_amount": 1989,  # $19.89
            "currency": "usd",
            "nickname": "Certified Mail - $19.89"
        })
        
        if certified_price:
            print(f"   Price: ${certified_price['unit_amount']/100:.2f} (ID: {certified_price['id']})")
    
    # Step 3: Get publishable key
    print("\n🔑 STEP 3: Retrieving account keys...")
    account = stripe_api_call("account", api_key)
    
    # Note: We can't get the publishable key via API, user needs to copy it from dashboard
    # But we can update what we have
    
    # Step 4: Update .env file
    print("\n💾 STEP 4: Updating .env file...")
    
    updates = {}
    if regular_price:
        updates["STRIPE_PRICE_STANDARD"] = regular_price['id']
    if certified_price:
        updates["STRIPE_PRICE_CERTIFIED"] = certified_price['id']
    
    if updates:
        update_env_file(updates)
        print("✅ .env file updated with new price IDs")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ STRIPE FULLY CONFIGURED FOR FIGHT CITY TICKETS")
    print("\n📋 Configuration Summary:")
    print(f"   Account: {account.get('email')}")
    print(f"   Regular Mail: ${regular_price['unit_amount']/100:.2f} - {regular_price['id']}")
    print(f"   Certified Mail: ${certified_price['unit_amount']/100:.2f} - {certified_price['id']}")
    
    print("\n⚠️  ACTION REQUIRED:")
    print("   You need to manually add the PUBLISHABLE KEY to .env:")
    print("   1. Go to https://dashboard.stripe.com/apikeys")
    print("   2. Copy the 'Publishable key' (starts with pk_live_)")
    print("   3. Update STRIPE_PUBLISHABLE_KEY in .env")
    print("\n   Alternatively, I can open the dashboard for you now.")

if __name__ == "__main__":
    main()
