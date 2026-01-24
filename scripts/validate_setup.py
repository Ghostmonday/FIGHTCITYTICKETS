import os
import sys
import urllib.request
import base64
import json

def load_env_manual(filepath=".env"):
    """Manually parse .env file to avoid dependencies"""
    if not os.path.exists(filepath):
        print(f"❌ .env file not found at {filepath}")
        return
    
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                # Remove loose quotes if present
                value = value.strip(' "\'')
                os.environ[key] = value

def check_var(name, prefix=None):
    val = os.environ.get(name)
    if not val:
        print(f"❌ MISSING: {name} is not set.")
        return False
    if "placeholder" in val or "your_" in val:
        print(f"⚠️  WARNING: {name} appears to be a placeholder.")
        return False
    if prefix and not val.startswith(prefix):
        print(f"❌ INVALID FORMAT: {name} should start with '{prefix}'")
        return False
    print(f"✅ FOUND: {name}")
    return True

def validate_stripe():
    print("\n--- Checking Stripe ---")
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        return
    
    try:
        url = "https://api.stripe.com/v1/balance"
        # Basic Auth for Stripe
        auth_str = f"{key}:"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Basic {b64_auth}")
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ STRIPE CONNECTIVITY: SUCCESS")
            else:
                print(f"❌ STRIPE CONNECTIVITY: FAILED ({response.status})")
    except urllib.error.HTTPError as e:
         print(f"❌ STRIPE CONNECTIVITY: FAILED ({e.code}) - {e.reason}")
    except Exception as e:
        print(f"❌ STRIPE CONNECTIVITY: ERROR - {e}")

def validate_lob():
    print("\n--- Checking Lob ---")
    key = os.environ.get("LOB_API_KEY")
    if not key:
        return
        
    try:
        url = "https://api.lob.com/v1/addresses"
        auth_str = f"{key}:"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Basic {b64_auth}")
        
        # Lob requires at least a limit or something to list, but checking auth works on list endpoint
        # usually defaults to 10
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ LOB CONNECTIVITY: SUCCESS")
            else:
                print(f"❌ LOB CONNECTIVITY: FAILED ({response.status})")
    except urllib.error.HTTPError as e:
         print(f"❌ LOB CONNECTIVITY: FAILED ({e.code}) - {e.reason}")
    except Exception as e:
        print(f"❌ LOB CONNECTIVITY: ERROR - {e}")

def main():
    print("🔍 VALIDATING ENVIRONMENT CONFIGURATION (StdLib Mode)...\n")
    load_env_manual()
    
    # Check existence and format
    ok = True
    ok &= check_var("STRIPE_SECRET_KEY", "sk_")
    ok &= check_var("STRIPE_PUBLISHABLE_KEY", "pk_")
    ok &= check_var("LOB_API_KEY")
    ok &= check_var("DEEPSEEK_API_KEY")
    ok &= check_var("DATABASE_URL", "postgresql")

    if ok:
        print("\nUsing keys to test connectivity...")
        validate_stripe()
        validate_lob()
    else:
        print("\n⚠️  Please fix the missing or invalid variables in your .env file.")

if __name__ == "__main__":
    main()
