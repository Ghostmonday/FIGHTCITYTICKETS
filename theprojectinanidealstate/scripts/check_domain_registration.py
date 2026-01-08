#!/usr/bin/env python3
"""
Check where fightcitytickets.com is actually registered
"""

import socket
import subprocess
import sys

DOMAIN = "fightcitytickets.com"

print("=" * 60)
print("Checking Domain Registration")
print("=" * 60)
print("Domain: {DOMAIN}")
print()

# Check DNS resolution
print("1. Checking DNS resolution...")
try:
    ip = socket.gethostbyname(DOMAIN)
    print("   [OK] Domain resolves to: {ip}")
except socket.gaierror:
    print("   [ERROR] Domain does not resolve")
    print("   Domain might not be registered or DNS not configured")

print()

# Check WHOIS (if available)
print("2. Checking domain registration...")
print("   (This requires 'whois' command - may not work on Windows)")
try:
    result = subprocess.run(
        ["whois", DOMAIN],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        whois_output = result.stdout.lower()
        if "namecheap" in whois_output:
            print("   [INFO] Domain appears to be with Namecheap")
        elif "registrar" in whois_output:
            print("   [INFO] Domain registrar info found")
            # Extract registrar if possible
            for line in result.stdout.split('\n'):
                if 'registrar' in line.lower():
                    print("   {line.strip()}")
        else:
            print("   [INFO] WHOIS data retrieved")
            print("   Check output above for registrar information")
    else:
        print("   [WARNING] WHOIS command not available or failed")
except FileNotFoundError:
    print("   [INFO] 'whois' command not available on this system")
except Exception as e:
    print("   [WARNING] Could not check WHOIS: {e}")

print()
print("=" * 60)
print("SOLUTION")
print("=" * 60)
print()
print("The domain 'fightcitytickets.com' is NOT in your Namecheap account.")
print()
print("To fix this:")
print("1. Check which account the domain is actually in")
print("2. Log into THAT account's Namecheap")
print("3. Configure DNS there")
print()
print("OR if the domain is with a different registrar:")
print("1. Log into that registrar's control panel")
print("2. Configure DNS records there:")
print("   - A Record: @ -> 178.156.215.100")
print("   - A Record: www -> 178.156.215.100")
print()
print("=" * 60)

