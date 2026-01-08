#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configure DNS for domains you already have"""

import requests
import socket
import os
import sys

# Get credentials from environment variables
NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "")
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "")
SERVER_IP = "178.156.215.100"

if not NAMECHEAP_USERNAME or not NAMECHEAP_API_KEY:
    print("ERROR: NAMECHEAP_USERNAME and NAMECHEAP_API_KEY environment variables must be set")
    sys.exit(1)

def get_client_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except Exception:
        return "127.0.0.1"

def set_dns(domain_sld, domain_tld):
    """Set DNS for a domain."""
    client_ip = get_client_ip()

    params = {
        "ApiUser": NAMECHEAP_USERNAME,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_USERNAME,
        "Command": "namecheap.domains.dns.setHosts",
        "ClientIp": client_ip,
        "SLD": domain_sld,
        "TLD": domain_tld,
        "HostName1": "@",
        "RecordType1": "A",
        "Address1": SERVER_IP,
        "TTL1": "1800",
        "HostName2": "www",
        "RecordType2": "A",
        "Address2": SERVER_IP,
        "TTL2": "1800",
    }

    try:
        response = requests.get("https://api.namecheap.com/xml.response", params=params, timeout=30)
        xml = response.text

        if "Status=\"OK\"" in xml or "<Status>OK</Status>" in xml:
            print("SUCCESS! {domain_sld}.{domain_tld} configured!")
            return True
        else:
            print("ERROR for {domain_sld}.{domain_tld}:")
            print(xml[:500])
            return False
    except Exception as e:
        print("Error: {e}")
        return False

print("=" * 60)
print("Configuring DNS for your existing domains")
print("=" * 60)
print()

# Configure fightcitytickets.com
print("1. Configuring fightcitytickets.com...")
set_dns("fightcitytickets", "com")
print()

# Configure fightcitytickets.city
print("2. Configuring fightcitytickets.city...")
set_dns("fightcitytickets", "city")
print()

print("=" * 60)
print("IMPORTANT: fightcitytickets.com is NOT registered!")
print("=" * 60)
print()
print("You have two options:")
print()
print("Option 1: Register fightcitytickets.com")
print("  - Go to: https://www.namecheap.com/domains/registration/results/?domain=fightcitytickets.com")
print("  - Register it if available")
print("  - Then run: python scripts/fix_dns_now.py")
print()
print("Option 2: Use an existing domain")
print("  - Use: https://fightcitytickets.com (already configured)")
print("  - Or: https://fightcitytickets.city (already configured)")
print()
print("DNS will propagate in 5-30 minutes")


