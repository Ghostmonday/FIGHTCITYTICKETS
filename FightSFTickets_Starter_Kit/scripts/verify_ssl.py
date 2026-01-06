#!/usr/bin/env python3
"""Verify SSL certificate is working"""

import requests
import socket
import ssl

DOMAIN = "fightcitytickets.com"

print("=" * 60)
print("SSL Verification")
print("=" * 60)
print("Domain: {DOMAIN}")
print()

# Check HTTPS
print("1. Testing HTTPS connection...")
try:
    response = requests.get("https://{DOMAIN}", timeout=10, verify=True)
    print("   [OK] HTTPS Status: {response.status_code}")
    print("   [OK] SSL Certificate is valid!")
except requests.exceptions.SSLError as e:
    print("   [ERROR] SSL Error: {e}")
except Exception as e:
    print("   [WARNING] Connection issue: {e}")

print()

# Check certificate details
print("2. Checking certificate details...")
try:
    context = ssl.create_default_context()
    with socket.create_connection((DOMAIN, 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=DOMAIN) as ssock:
            cert = ssock.getpeercert()
            print("   [OK] Certificate issuer: {cert.get('issuer', 'Unknown')}")
            print("   [OK] Certificate valid until: {cert.get('notAfter', 'Unknown')}")
except Exception as e:
    print("   [WARNING] Could not check certificate: {e}")

print()
print("=" * 60)
print("Your site should be accessible at:")
print("  https://{DOMAIN}")
print("  https://www.{DOMAIN}")
print("=" * 60)

