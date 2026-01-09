#!/usr/bin/env python3
"""
DNS Setup Helper for fightcitytickets.com
Helps verify DNS configuration and provides setup instructions.
"""

import subprocess
import socket
import sys
from datetime import datetime

DOMAIN = "fightcitytickets.com"
EXPECTED_IP = "178.156.215.100"

def print_header():
    print("=" * 60)
    print("DNS Setup Helper - fightcitytickets.com")
    print("=" * 60)
    print("Domain: {DOMAIN}")
    print("Expected Server IP: {EXPECTED_IP}")
    print("=" * 60)
    print()

def check_dns_resolution(hostname):
    """Check if DNS resolves to expected IP."""
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        return None

def check_http_connectivity(hostname):
    """Check if HTTP connection works."""
    try:
        import urllib.request
        response = urllib.request.urlopen("http://{hostname}", timeout=5)
        return response.getcode()
    except Exception as e:
        return None

def main():
    print_header()

    print("STEP 1: Manual DNS Configuration Required")
    print("-" * 60)
    print("Go to Namecheap and configure DNS:")
    print("URL: https://ap.www.namecheap.com/domains/list/")
    print()
    print("1. Click 'Manage' next to fightcitytickets.com")
    print("2. Go to 'Advanced DNS' tab")
    print("3. Add/Update these A records:")
    print()
    print("   Record 1:")
    print("   Type:  A Record")
    print("   Host:  @ (or leave blank)")
    print("   Value: 178.156.215.100")
    print("   TTL:   Automatic")
    print()
    print("   Record 2:")
    print("   Type:  A Record")
    print("   Host:  www")
    print("   Value: 178.156.215.100")
    print("   TTL:   Automatic")
    print()
    print("4. Save changes")
    print()
    print("-" * 60)
    print()

    # Check current DNS status
    print("STEP 2: Checking Current DNS Status...")
    print("-" * 60)

    # Check root domain
    root_ip = check_dns_resolution(DOMAIN)
    if root_ip:
        if root_ip == EXPECTED_IP:
            print("[OK] {DOMAIN} -> {root_ip} (CORRECT)")
        else:
            print("[ERROR] {DOMAIN} -> {root_ip} (WRONG - expected {EXPECTED_IP})")
    else:
        print("[WARNING] {DOMAIN} -> Not resolving yet")

    # Check www subdomain
    www_domain = "www.{DOMAIN}"
    www_ip = check_dns_resolution(www_domain)
    if www_ip:
        if www_ip == EXPECTED_IP:
            print("[OK] {www_domain} -> {www_ip} (CORRECT)")
        else:
            print("[ERROR] {www_domain} -> {www_ip} (WRONG - expected {EXPECTED_IP})")
    else:
        print("[WARNING] {www_domain} -> Not resolving yet")

    print()

    # Check HTTP connectivity
    print("STEP 3: Checking HTTP Connectivity...")
    print("-" * 60)

    http_status = check_http_connectivity(DOMAIN)
    if http_status:
        print("[OK] HTTP connection successful (Status: {http_status})")
    else:
        print("[WARNING] HTTP connection failed (DNS may not be propagated yet)")

    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)

    if root_ip == EXPECTED_IP and www_ip == EXPECTED_IP:
        print("[OK] DNS is configured correctly!")
        print()
        print("1. Set up SSL certificate:")
        print("   ssh root@178.156.215.100")
        print("   certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com")
        print()
        print("2. Update .env file with your domain")
        print("3. Test your site: https://fightcitytickets.com")
    else:
        print("[WARNING] DNS is not configured yet or still propagating")
        print()
        print("1. Complete the DNS setup in Namecheap (see Step 1 above)")
        print("2. Wait 5-30 minutes for DNS propagation")
        print("3. Run this script again to verify:")
        print("   python scripts/setup_dns.py")
        print()
        print("Check DNS globally:")
        print("   https://www.whatsmydns.net/#A/{DOMAIN}")

    print()
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print("\n[ERROR] Error: {e}")
        sys.exit(1)

