#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick DNS Fix for fightcitytickets.com using Namecheap API
"""

import requests
import socket
import time
import os
import sys

# Get credentials from environment variables
NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "")
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "")
NAMECHEAP_API_PASSWORD = os.getenv("NAMECHEAP_API_PASSWORD", "")

if not NAMECHEAP_USERNAME or not NAMECHEAP_API_KEY:
    print("ERROR: NAMECHEAP_USERNAME and NAMECHEAP_API_KEY environment variables must be set")
    sys.exit(1)

# Domain Configuration
DOMAIN = "fightcitytickets.com"
DOMAIN_SLD = "fightcitytickets"
DOMAIN_TLD = "com"
SERVER_IP = "178.156.215.100"

API_URL = "https://api.namecheap.com/xml.response"

def get_client_ip():
    """Get client IP address."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except Exception:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

def make_api_call(command, params):
    """Make Namecheap API call."""
    client_ip = get_client_ip()

    api_params = {
        "ApiUser": NAMECHEAP_USERNAME,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_USERNAME,
        "Command": command,
        "ClientIp": client_ip,
    }
    api_params.update(params)

    try:
        response = requests.get(API_URL, params=api_params, timeout=30)
        return response.text, response.status_code
    except Exception as e:
        print("API Error: {e}")
        return None, None

def set_dns_records():
    """Set DNS A records for domain."""
    print("Setting DNS records for {DOMAIN}...")
    print("Pointing to server: {SERVER_IP}")
    print("Your IP: {get_client_ip()}")
    print()

    params = {
        "SLD": DOMAIN_SLD,
        "TLD": DOMAIN_TLD,
        "HostName1": "@",
        "RecordType1": "A",
        "Address1": SERVER_IP,
        "TTL1": "1800",
        "HostName2": "www",
        "RecordType2": "A",
        "Address2": SERVER_IP,
        "TTL2": "1800",
    }

    xml_response, status_code = make_api_call("namecheap.domains.dns.setHosts", params)

    if not xml_response:
        print("ERROR: Failed to contact Namecheap API")
        return False

    print("API Response:")
    print(xml_response)
    print()

    if "Status=\"OK\"" in xml_response or "<Status>OK</Status>" in xml_response:
        print("SUCCESS! DNS records configured!")
        return True
    elif "Error" in xml_response:
        print("ERROR: API returned an error")
        if "2019166" in xml_response:
            print("Domain not found or not using Namecheap DNS")
            print("Make sure:")
            print("  1. Domain is in your Namecheap account")
            print("  2. Domain uses Namecheap nameservers")
        elif "whitelist" in xml_response.lower() or "ip" in xml_response.lower():
            print("Your IP ({get_client_ip()}) may need to be whitelisted")
            print("Go to: https://ap.www.namecheap.com/settings/tools/apiaccess/")
        return False
    else:
        print("WARNING: Unexpected response")
        return False

def verify_dns():
    """Verify DNS propagation."""
    print("Verifying DNS...")
    print("(This can take 5 minutes to 48 hours)")
    print()

    for i in range(6):
        try:
            root_ip = socket.gethostbyname(DOMAIN)
            www_ip = socket.gethostbyname("www.{DOMAIN}")

            print("DNS is resolving!")
            print("  {DOMAIN} -> {root_ip}")
            print("  www.{DOMAIN} -> {www_ip}")

            if root_ip == SERVER_IP and www_ip == SERVER_IP:
                print("\nSUCCESS! DNS is correctly configured!")
                return True
            else:
                print("DNS points to different IPs - may still be propagating")
        except socket.gaierror:
            print("Attempt {i+1}/6: DNS not resolving yet...")

        if i < 5:
            time.sleep(10)

    print("\nDNS not fully propagated yet - this is normal")
    print("Check again in a few minutes")
    return False

def main():
    print("=" * 60)
    print("FightCityTickets.com DNS Configuration")
    print("=" * 60)
    print("Domain: {DOMAIN}")
    print("Server IP: {SERVER_IP}")
    print()

    if set_dns_records():
        print("\nWaiting 5 seconds before verification...")
        time.sleep(5)
        verify_dns()
    else:
        print("\nFailed to set DNS records")
        print("\nYou can also configure DNS manually:")
        print("1. Go to: https://ap.www.namecheap.com/domains/list/")
        print("2. Click 'Manage' next to fightcitytickets.com")
        print("3. Go to 'Advanced DNS'")
        print("4. Add A record: @ -> 178.156.215.100")
        print("5. Add A record: www -> 178.156.215.100")

if __name__ == "__main__":
    main()


