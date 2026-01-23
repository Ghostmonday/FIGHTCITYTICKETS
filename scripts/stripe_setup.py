#!/usr/bin/env python3
"""
Stripe Setup Script - Automated configuration using restricted API key
"""
import os
import urllib.request
import urllib.parse
import json
import base64

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
    
    # Prepare authentication
    auth_str = f"{api_key}:"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    # Prepare request
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Handle POST data
    post_data = None
    if data and method == "POST":
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

def main():
    print("🔧 STRIPE AUTOMATION SETUP")
    print("=" * 50)
    
    load_env()
    api_key = os.environ.get("RESTRICTED_STRIPE_KEY")
    
    if not api_key:
        print("❌ RESTRICTED_STRIPE_KEY not found in .env")
        return
    
    print(f"✅ Found API Key: {api_key[:15]}...")
    
    # Test 1: Retrieve account info
    print("\n📊 Testing API connectivity...")
    account = stripe_api_call("account", api_key)
    
    if account:
        print(f"✅ Connected to Stripe Account")
        print(f"   Account ID: {account.get('id')}")
        print(f"   Email: {account.get('email')}")
        print(f"   Country: {account.get('country')}")
        print(f"   Charges Enabled: {account.get('charges_enabled')}")
        print(f"   Payouts Enabled: {account.get('payouts_enabled')}")
    else:
        print("❌ Failed to connect to Stripe")
        return
    
    # Test 2: List existing products
    print("\n📦 Checking existing products...")
    products = stripe_api_call("products?limit=10", api_key)
    
    if products and products.get('data'):
        print(f"✅ Found {len(products['data'])} existing product(s):")
        for prod in products['data']:
            print(f"   - {prod['name']} (ID: {prod['id']})")
    else:
        print("ℹ️  No existing products found")
    
    # Test 3: Check webhook endpoints
    print("\n🔗 Checking webhook endpoints...")
    webhooks = stripe_api_call("webhook_endpoints?limit=10", api_key)
    
    if webhooks and webhooks.get('data'):
        print(f"✅ Found {len(webhooks['data'])} webhook(s):")
        for wh in webhooks['data']:
            print(f"   - {wh['url']}")
            print(f"     Events: {', '.join(wh['enabled_events'][:3])}...")
    else:
        print("ℹ️  No webhook endpoints configured")
    
    print("\n" + "=" * 50)
    print("✅ STRIPE CONNECTIVITY VERIFIED")
    print("\nNext steps available:")
    print("  1. Create products for 'Regular Mail' and 'Certified Mail'")
    print("  2. Set up webhook endpoint for payment notifications")
    print("  3. Configure publishable key for frontend")

if __name__ == "__main__":
    main()
