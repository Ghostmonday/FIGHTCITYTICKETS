#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check what domains are in Namecheap account"""

import requests
import os
import sys

# Get credentials from environment variables
NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "")
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "")

if not NAMECHEAP_USERNAME or not NAMECHEAP_API_KEY:
    print("ERROR: NAMECHEAP_USERNAME and NAMECHEAP_API_KEY environment variables must be set")
    sys.exit(1)

def get_client_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except Exception:
        return "127.0.0.1"

def list_domains():
    """List all domains in Namecheap account."""
    client_ip = get_client_ip()

    params = {
        "ApiUser": NAMECHEAP_USERNAME,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_USERNAME,
        "Command": "namecheap.domains.getList",
        "ClientIp": client_ip,
        "PageSize": "100"
    }

    try:
        response = requests.get("https://api.namecheap.com/xml.response", params=params, timeout=30)
        print("Domains in your Namecheap account:")
        print("=" * 60)
        print(response.text)
        print("=" * 60)

        # Parse and show domain names
        if "Domain" in response.text:
            import re
            domains = re.findall(r'<Domain>([^<]+)</Domain>', response.text)
            if domains:
                print("\nFound domains:")
                for domain in domains:
                    print("  - {domain}")
            else:
                print("\nNo domains found in response")
        else:
            print("\nNo domains found or error in response")

    except Exception as e:
        print("Error: {e}")

if __name__ == "__main__":
    list_domains()


