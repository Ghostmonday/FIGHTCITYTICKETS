#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify DNS records for fightcitytickets.com using Namecheap API"""

import requests
import sys
import os
import warnings
# Security: Use defusedxml to prevent XML attacks
try:
    from defusedxml.ElementTree import fromstring as safe_fromstring
    # Defuse the standard library XML parsers as additional protection
    import defusedxml.ElementTree
    defusedxml.ElementTree.defuse_stdlib()
except ImportError:
    # Fallback: warn if defusedxml not available
    import xml.etree.ElementTree as ET
    warnings.warn(
        "defusedxml not installed. Install with: pip install defusedxml",
        category=UserWarning,
        stacklevel=2
    )
    safe_fromstring = ET.fromstring

# Get credentials from environment variables
NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "")
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "")
DOMAIN = "fightcitytickets.com"
EXPECTED_IP = "178.156.215.100"

if not NAMECHEAP_USERNAME or not NAMECHEAP_API_KEY:
    print("ERROR: NAMECHEAP_USERNAME and NAMECHEAP_API_KEY environment variables must be set")
    sys.exit(1)

def get_client_ip():
    """Get the client IP address."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except Exception:
        return "127.0.0.1"

def get_dns_hosts(domain):
    """Get DNS host records for a domain."""
    client_ip = get_client_ip()

    params = {
        "ApiUser": NAMECHEAP_USERNAME,
        "ApiKey": NAMECHEAP_API_KEY,
        "UserName": NAMECHEAP_USERNAME,
        "Command": "namecheap.domains.dns.getHosts",
        "ClientIp": client_ip,
        "SLD": domain.split('.')[0],  # e.g., "fightcitytickets"
        "TLD": domain.split('.')[1]    # e.g., "com"
    }

    try:
        response = requests.get("https://api.namecheap.com/xml.response", params=params, timeout=30)
        return response.text
    except Exception as e:
        print("Error calling Namecheap API: {e}")
        return None

def parse_dns_records(xml_response):
    """Parse DNS records from XML response."""
    try:
        # Security: Use safe XML parser to prevent XXE attacks
        root = safe_fromstring(xml_response)

        # Define namespace (Namecheap uses this namespace)
        ns = {'nc': 'http://api.namecheap.com/xml.response'}

        # Check for errors
        errors = root.findall(".//nc:Error", ns)
        if errors:
            error_msgs = [err.text for err in errors if err.text]
            if error_msgs:
                print("❌ API Error: {', '.join(error_msgs)}")
                return None

        # Extract host records (handle both with and without namespace)
        hosts = []
        for host in root.findall(".//host") + root.findall(".//nc:host", ns):
            host_data = {}
            # Get attributes from the host element itself
            host_data['Name'] = host.get('Name', '')
            host_data['Type'] = host.get('Type', '')
            host_data['Address'] = host.get('Address', '')
            host_data['TTL'] = host.get('TTL', '')
            host_data['HostId'] = host.get('HostId', '')
            host_data['IsActive'] = host.get('IsActive', '')
            hosts.append(host_data)

        return hosts
    except ET.ParseError as e:
        print("❌ Error parsing XML: {e}")
        print("Response: {xml_response[:500]}")
        return None

def verify_dns_records(domain, expected_ip):
    """Verify DNS records are correctly configured."""
    print("🔍 Checking DNS records for {domain}...")
    print("Expected IP: {expected_ip}")
    print("=" * 60)

    xml_response = get_dns_hosts(domain)
    if not xml_response:
        return False

    hosts = parse_dns_records(xml_response)
    if hosts is None:
        return False

    if not hosts:
        print("⚠️  No DNS records found!")
        return False

    print("\n📋 Found {len(hosts)} DNS record(s):\n")

    # Check for A records pointing to root domain and www
    root_a_record = None
    www_a_record = None
    www_cname_record = None

    issues = []

    for host in hosts:
        hostname = host.get('Name', '')
        record_type = host.get('Type', '')
        address = host.get('Address', '')
        ttl = host.get('TTL', '')

        print("  Host: {hostname or '@'}")
        print("  Type: {record_type}")
        print("  Address: {address}")
        print("  TTL: {ttl}")
        print()

        # Check for root domain A record
        if hostname == '@' and record_type == 'A':
            root_a_record = address
            if address != expected_ip:
                issues.append("❌ Root domain (@) A record points to {address}, expected {expected_ip}")
            else:
                print("  ✅ Root domain A record is correct")

        # Check for www A record
        if hostname == 'www' and record_type == 'A':
            www_a_record = address
            if address != expected_ip:
                issues.append("❌ www A record points to {address}, expected {expected_ip}")
            else:
                print("  ✅ www A record is correct")

        # Check for www CNAME
        if hostname == 'www' and record_type == 'CNAME':
            www_cname_record = address
            if address != domain:
                issues.append("❌ www CNAME points to {address}, expected {domain}")
            else:
                print("  ✅ www CNAME is correct")

    print("=" * 60)

    # Summary
    if not root_a_record:
        issues.append("❌ Missing A record for root domain (@)")

    if not www_a_record and not www_cname_record:
        issues.append("⚠️  No www record found (A or CNAME)")

    # Check for incorrect domain references
    for host in hosts:
        address = host.get('Address', '').lower()
        if 'fightcitytickets' in address or 'flight' in address:
            issues.append("❌ Found incorrect domain reference: {address}")

    if issues:
        print("\n🚨 ISSUES FOUND:\n")
        for issue in issues:
            print("  {issue}")
        return False
    else:
        print("\n✅ DNS configuration looks correct!")
        print("   Root domain (@) → {expected_ip}")
        if www_a_record:
            print("   www → {expected_ip} (A record)")
        elif www_cname_record:
            print("   www → {domain} (CNAME)")
        return True

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    success = verify_dns_records(DOMAIN, EXPECTED_IP)
    sys.exit(0 if success else 1)

