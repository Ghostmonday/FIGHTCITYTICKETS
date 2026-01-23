#!/usr/bin/env python3
"""
Get Stripe Publishable Key and update .env
"""
import os
import urllib.request
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

def stripe_api_call(endpoint, api_key):
    url = f"https://api.stripe.com/v1/{endpoint}"
    auth_str = f"{api_key}:"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {"Authorization": f"Basic {b64_auth}"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_env_var(key, value):
    env_path = "/home/evan/Documents/Projects/FightSFTickets/.env"
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
    
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    return found

def main():
    print("🔑 Retrieving Stripe Publishable Key...")
    load_env()
    
    api_key = os.environ.get("RESTRICTED_STRIPE_KEY")
    if not api_key:
        print("❌ No restricted key found")
        return
    
    # Get account to find publishable key info
    account = stripe_api_call("account", api_key)
    
    if account:
        # Unfortunately, publishable keys aren't returned via API for security
        # We need to construct it or have user provide it
        print("\n⚠️  Stripe API does not return publishable keys for security.")
        print("\nOptions:")
        print("1. Log in to https://dashboard.stripe.com/apikeys")
        print("2. Copy the 'Publishable key' (starts with pk_live_)")
        print("3. I can open the dashboard for you")
        
        # Open the dashboard
        import subprocess
        try:
            subprocess.Popen(['xdg-open', 'https://dashboard.stripe.com/apikeys'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("\n✅ Opened Stripe Dashboard in browser")
            print("\nOnce you have the key, you can:")
            print("  - Manually edit .env, OR")
            print("  - Run: echo 'STRIPE_PUBLISHABLE_KEY=pk_live_xxx' >> .env")
        except:
            print("Could not open browser automatically")

if __name__ == "__main__":
    main()
