#!/usr/bin/env python3
"""
Quick DNS Fix for fightcitytickets.com
Sets up DNS records to point to server IP
"""

import requests
import socket
import time
import os

# Configuration
DOMAIN = "fightcitytickets.com"
DOMAIN_SLD = "fightcitytickets"
DOMAIN_TLD = "com"
SERVER_IP = "178.156.215.100"

# Namecheap API Configuration
# Get these from: https://ap.www.namecheap.com/settings/tools/apiaccess/
NAMECHEAP_API_USER = os.getenv("NAMECHEAP_API_USER", "")
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "")
NAMECHEAP_API_PASSWORD = os.getenv("NAMECHEAP_API_PASSWORD", "")
NAMECHEAP_CLIENT_IP = os.getenv("NAMECHEAP_CLIENT_IP", "")

API_URL = "https://api.namecheap.com/xml.response"

def get_client_ip():
    """Get client IP address."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except Exception:
        return ""

def make_api_call(command, params):
    """Make Namecheap API call."""
    if not NAMECHEAP_API_USER or not NAMECHEAP_API_KEY:
        print("❌ ERROR: Namecheap API credentials not set!")
        print("\nSet these environment variables:")
        print("  export NAMECHEAP_API_USER='your_username'")
        print("  export NAMECHEAP_API_KEY='your_api_key'")
        print("  export NAMECHEAP_API_PASSWORD='your_api_password'")
        print("\nOr get them from: https://ap.www.namecheap.com/settings/tools/apiaccess/")
        return None, None

    client_ip = NAMECHEAP_CLIENT_IP or get_client_ip()

    api_params = {
        "ApiUser": NAMECHEAP_API_USER,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_API_USER,
        "Command": command,
        "ClientIp": client_ip,
        **params
    }

    try:
        response = requests.get(API_URL, params=api_params, timeout=30)
        return response.text, response.status_code
    except Exception as e:
        print("❌ API Error: {e}")
        return None, None

def get_current_dns():
    """Get current DNS records."""
    print("📡 Getting current DNS records for {DOMAIN}...")

    params = {
        "SLD": DOMAIN_SLD,
        "TLD": DOMAIN_TLD,
    }

    xml_response, status_code = make_api_call("namecheap.domains.dns.getHosts", params)

    if not xml_response:
        return None

    if "Error" in xml_response:
        print("❌ Error getting DNS: {xml_response}")
        return None

    print("✅ Current DNS records retrieved")
    return xml_response

def set_dns_records():
    """Set DNS A records for domain."""
    print("\n🔧 Setting DNS records for {DOMAIN}...")
    print("   Pointing to server: {SERVER_IP}")

    # Get current records first
    current_dns = get_current_dns()

    # Set DNS records
    params = {
        "SLD": DOMAIN_SLD,
        "TLD": DOMAIN_TLD,
        "RecordType1": "A",
        "HostName1": "@",
        "Address1": SERVER_IP,
        "TTL1": "1800",
        "RecordType2": "A",
        "HostName2": "www",
        "Address2": SERVER_IP,
        "TTL2": "1800",
    }

    xml_response, status_code = make_api_call("namecheap.domains.dns.setHosts", params)

    if not xml_response:
        print("❌ Failed to set DNS records")
        return False

    if "Error" in xml_response:
        print("❌ Error setting DNS: {xml_response}")
        if "Error 2019166" in xml_response:
            print("\n⚠️  Domain not found or not using Namecheap DNS")
            print("   1. Make sure domain is in your Namecheap account")
            print("   2. Make sure domain uses Namecheap nameservers")
            print("   3. Check: https://ap.www.namecheap.com/domains/list/")
        return False

    if "CommandResponse" in xml_response and "OK" in xml_response:
        print("✅ DNS records set successfully!")
        return True
    else:
        print("⚠️  Unexpected response: {xml_response[:200]}")
        return False

def verify_dns():
    """Verify DNS propagation."""
    print("\n🔍 Verifying DNS propagation...")
    print("   (This can take 5 minutes to 48 hours)")

    max_attempts = 10
    for i in range(max_attempts):
        try:
            root_ip = socket.gethostbyname(DOMAIN)
            www_ip = socket.gethostbyname("www.{DOMAIN}")

            print("\n✅ DNS is resolving!")
            print("   {DOMAIN} → {root_ip}")
            print("   www.{DOMAIN} → {www_ip}")

            if root_ip == SERVER_IP and www_ip == SERVER_IP:
                print("\n🎉 SUCCESS! DNS is correctly pointing to your server!")
                return True
            else:
                print("\n⚠️  DNS points to different IPs:")
                if root_ip != SERVER_IP:
                    print("   {DOMAIN} → {root_ip} (expected {SERVER_IP})")
                if www_ip != SERVER_IP:
                    print("   www.{DOMAIN} → {www_ip} (expected {SERVER_IP})")
                print("   DNS may still be propagating...")
        except socket.gaierror:
            print("   Attempt {i+1}/{max_attempts}: DNS not resolving yet...")

        if i < max_attempts - 1:
            time.sleep(10)

    print("\n⚠️  DNS not resolving yet. This is normal - it can take time.")
    print("   Check again later with: nslookup fightcitytickets.com")
    return False

def main():
    print("=" * 60)
    print("  FightCityTickets.com DNS Configuration")
    print("=" * 60)
    print("\nDomain: {DOMAIN}")
    print("Server IP: {SERVER_IP}")
    print()

    # Check credentials
    if not NAMECHEAP_API_USER or not NAMECHEAP_API_KEY:
        print("❌ Namecheap API credentials not configured!")
        print("\nTo configure:")
        print("1. Get API credentials from: https://ap.www.namecheap.com/settings/tools/apiaccess/")
        print("2. Set environment variables:")
        print("   export NAMECHEAP_API_USER='your_username'")
        print("   export NAMECHEAP_API_KEY='your_api_key'")
        print("   export NAMECHEAP_API_PASSWORD='your_api_password'")
        print("\n3. Run this script again")
        return

    # Set DNS records
    if set_dns_records():
        print("\n⏳ Waiting 5 seconds before verification...")
        time.sleep(5)
        verify_dns()
    else:
        print("\n❌ Failed to set DNS records. Check the errors above.")

if __name__ == "__main__":
    main()


