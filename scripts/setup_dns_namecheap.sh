#!/bin/bash

# DNS Setup Script for Namecheap
# Domain: fightcitytickets.com
# Server IP: 178.156.215.100

# IMPORTANT: This script contains credentials - DO NOT commit to git!
# Run this script locally and delete it after use, or store credentials securely

set -e

# Configuration
DOMAIN="fightcitytickets.com"
SERVER_IP="178.156.215.100"
NAMECHEAP_USERNAME="AMIRPIX"
NAMECHEAP_API_TOKEN="673e306c449b4a68b5996f044684ad56"
NAMECHEAP_API_PASSWORD="wungum-tajxu2-rAfsov"

# Namecheap API endpoint
API_URL="https://api.namecheap.com/xml.response"

echo "=========================================="
echo "Namecheap DNS Configuration"
echo "Domain: $DOMAIN"
echo "Server IP: $SERVER_IP"
echo "=========================================="
echo ""

# Function to make API call
make_api_call() {
    local command=$1
    local params=$2
    
    local url="${API_URL}?ApiUser=${NAMECHEAP_USERNAME}&ApiKey=${NAMECHEAP_API_TOKEN}&UserName=${NAMECHEAP_USERNAME}&Command=${command}&ClientIp=$(curl -s ifconfig.me)&${params}"
    
    echo "Making API call: $command"
    curl -s "$url"
    echo ""
}

# Check current DNS records
echo "Step 1: Checking current DNS records..."
make_api_call "namecheap.domains.dns.getHosts" "SLD=fightcitytickets&TLD=com"

echo ""
echo "=========================================="
echo "Manual DNS Configuration Instructions"
echo "=========================================="
echo ""
echo "Since Namecheap API requires whitelisted IP addresses, you'll need to"
echo "configure DNS manually through the Namecheap dashboard."
echo ""
echo "Go to: https://ap.www.namecheap.com/domains/list/"
echo "Click on 'Manage' next to $DOMAIN"
echo "Go to 'Advanced DNS' tab"
echo ""
echo "Add/Update these DNS records:"
echo ""
echo "Type: A Record"
echo "Host: @"
echo "Value: $SERVER_IP"
echo "TTL: Automatic (or 1800)"
echo ""
echo "Type: A Record"
echo "Host: www"
echo "Value: $SERVER_IP"
echo "TTL: Automatic (or 1800)"
echo ""
echo "Type: CNAME Record (optional - for www)"
echo "Host: www"
echo "Value: $DOMAIN"
echo "TTL: Automatic"
echo ""
echo "=========================================="
echo "After DNS is configured, wait 5-30 minutes for propagation"
echo "Then test with: nslookup $DOMAIN"
echo "=========================================="

