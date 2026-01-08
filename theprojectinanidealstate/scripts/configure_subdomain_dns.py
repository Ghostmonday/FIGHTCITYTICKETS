#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configure wildcard subdomain DNS for city routing"""

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

# Domains to configure
DOMAINS = [
    ("fightcitytickets", "com"),
    ("fightcitytickets", "city"),
]

def get_client_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except Exception:
        return "127.0.0.1"

def set_wildcard_dns(domain_sld, domain_tld):
    """Set wildcard subdomain DNS (*.domain.com -> server IP)."""
    client_ip = get_client_ip()

    # First get existing records
    params_get = {
        "ApiUser": NAMECHEAP_USERNAME,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_USERNAME,
        "Command": "namecheap.domains.dns.getHosts",
        "ClientIp": client_ip,
        "SLD": domain_sld,
        "TLD": domain_tld,
    }

    try:
        response = requests.get("https://api.namecheap.com/xml.response", params=params_get, timeout=30)
        print("\nCurrent DNS records for {domain_sld}.{domain_tld}:")
        print(response.text[:500])
    except Exception:
        pass

    # Set DNS records including wildcard
    params_set = {
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
        "HostName3": "*",
        "RecordType3": "A",
        "Address3": SERVER_IP,
        "TTL3": "1800",
    }

    try:
        response = requests.get("https://api.namecheap.com/xml.response", params=params_set, timeout=30)
        xml = response.text

        if "Status=\"OK\"" in xml or "<Status>OK</Status>" in xml:
            print("SUCCESS! Wildcard DNS configured for {domain_sld}.{domain_tld}")
            print("  *.{domain_sld}.{domain_tld} -> {SERVER_IP}")
            return True
        else:
            print("ERROR for {domain_sld}.{domain_tld}:")
            print(xml[:500])
            return False
    except Exception as e:
        print("Error: {e}")
        return False

print("=" * 60)
print("Configuring Wildcard Subdomain DNS")
print("=" * 60)
print("Server IP: {SERVER_IP}")
print("Your IP: {get_client_ip()}")
print()

for domain_sld, domain_tld in DOMAINS:
    print("Configuring {domain_sld}.{domain_tld}...")
    set_wildcard_dns(domain_sld, domain_tld)
    print()

print("=" * 60)
print("Subdomain DNS Configuration Complete!")
print("=" * 60)
print()
print("Now these subdomains will work:")
print("  - sf.fightcitytickets.com")
print("  - nyc.fightcitytickets.com")
print("  - sd.fightcitytickets.com")
print("  - (and all other city subdomains)")
print()
print("DNS will propagate in 5-30 minutes")


