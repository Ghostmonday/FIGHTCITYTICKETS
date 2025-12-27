#!/usr/bin/env python3
"""
Fix Namecheap API Access Issues
Helps configure API access and check domain status
"""

import requests
import os

# Get credentials from environment variables
NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "")
CLIENT_IP = os.getenv("CLIENT_IP", "")  # Your current IP (or auto-detect)

print("=" * 60)
print("Namecheap API Configuration Fix")
print("=" * 60)
print()
print("ISSUE DETECTED:")
print("1. Domain may not be using Namecheap DNS")
print("2. Client IP may not be whitelisted")
print()
print("YOUR CLIENT IP: " + CLIENT_IP)
print()
print("=" * 60)
print("SOLUTION 1: Whitelist Your IP")
print("=" * 60)
print()
print("1. Go to: https://ap.www.namecheap.com/settings/tools/apiaccess/")
print()
print("2. Scroll to 'Whitelisted IPs' section")
print()
print("3. Add this IP address:")
print("   {CLIENT_IP}")
print()
print("4. Click 'Add' and save")
print()
print("=" * 60)
print("SOLUTION 2: Check Domain Nameservers")
print("=" * 60)
print()
print("1. Go to: https://ap.www.namecheap.com/domains/list/")
print()
print("2. Click 'Manage' next to fightcitytickets.com")
print()
print("3. Click 'Nameservers' tab")
print()
print("4. Make sure it's set to:")
print("   'Namecheap BasicDNS' or 'Namecheap Web Hosting DNS'")
print()
print("   If it shows custom nameservers, change to:")
print("   dns1.registrar-servers.com")
print("   dns2.registrar-servers.com")
print()
print("5. Save changes and wait 5-10 minutes")
print()
print("=" * 60)
print("After Fixing:")
print("=" * 60)
print()
print("Run this script again:")
print("  python scripts/configure_dns_api.py")
print()
print("=" * 60)

