#!/usr/bin/env python3
"""
Add Mercury Bank Account to Stripe for Payouts
"""
import os
import urllib.request
import urllib.parse
import json
import base64

def load_env():
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
    url = f"https://api.stripe.com/v1/{endpoint}"
    auth_str = f"{api_key}:"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    post_data = None
    if data:
        # Handle nested parameters for external accounts
        post_data = urllib.parse.urlencode(data).encode()
    
    req = urllib.request.Request(url, data=post_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ API Error ({e.code}): {error_body}")
        return None

def add_bank_account(api_key, routing_number, account_number, account_holder_name):
    """Add external bank account to Stripe"""
    
    print("🏦 Adding Mercury account to Stripe...")
    
    # Get account ID first
    account = stripe_api_call("account", api_key)
    if not account:
        print("❌ Failed to retrieve account")
        return False
    
    account_id = account['id']
    print(f"   Account ID: {account_id}")
    
    # Add external account (bank account)
    data = {
        'external_account[object]': 'bank_account',
        'external_account[country]': 'US',
        'external_account[currency]': 'usd',
        'external_account[routing_number]': routing_number,
        'external_account[account_number]': account_number,
        'external_account[account_holder_name]': account_holder_name,
        'external_account[account_holder_type]': 'company'  # Mercury is business banking
    }
    
    result = stripe_api_call(f"accounts/{account_id}/external_accounts", api_key, 
                            method="POST", data=data)
    
    if result:
        print(f"✅ Bank account added successfully!")
        print(f"   Bank: {result.get('bank_name', 'N/A')}")
        print(f"   Last 4: ****{result.get('last4')}")
        print(f"   Status: {result.get('status')}")
        return True
    else:
        return False

def main():
    print("🏦 MERCURY → STRIPE CONNECTION")
    print("=" * 60)
    
    load_env()
    api_key = os.environ.get("RESTRICTED_STRIPE_KEY")
    
    if not api_key:
        print("❌ No Stripe API key found")
        return
    
    # Check for Mercury credentials in env
    routing = os.environ.get("MERCURY_ROUTING_NUMBER")
    account = os.environ.get("MERCURY_ACCOUNT_NUMBER")
    holder = os.environ.get("MERCURY_ACCOUNT_HOLDER_NAME")
    
    if routing and account and holder:
        print("✅ Found Mercury credentials in .env")
        print(f"   Routing: {routing}")
        print(f"   Account: ****{account[-4:]}")
        print(f"   Holder: {holder}")
        
        confirm = input("\nProceed with adding this account? (yes/no): ")
        if confirm.lower() == 'yes':
            add_bank_account(api_key, routing, account, holder)
        else:
            print("❌ Aborted")
    else:
        print("ℹ️  No Mercury credentials found in .env")
        print("\nTo automate, add to your .env file:")
        print("   MERCURY_ROUTING_NUMBER=your_routing_number")
        print("   MERCURY_ACCOUNT_NUMBER=your_account_number")
        print("   MERCURY_ACCOUNT_HOLDER_NAME=Your Business Name")
        print("\nThen run this script again.")
        print("\n--- OR ---\n")
        print("Enter details now:")
        
        routing = input("Mercury Routing Number (9 digits): ").strip()
        account = input("Mercury Account Number: ").strip()
        holder = input("Account Holder Name (business name): ").strip()
        
        if routing and account and holder:
            add_bank_account(api_key, routing, account, holder)

if __name__ == "__main__":
    main()
