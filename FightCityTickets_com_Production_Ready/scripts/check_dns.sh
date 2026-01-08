#!/bin/bash

# DNS Check Script
# Verifies that DNS is correctly pointing to your server

DOMAIN="fightcitytickets.com"
EXPECTED_IP="178.156.215.100"

echo "=========================================="
echo "DNS Configuration Check"
echo "Domain: $DOMAIN"
echo "Expected IP: $EXPECTED_IP"
echo "=========================================="
echo ""

# Check root domain
echo "Checking root domain ($DOMAIN)..."
RESOLVED_IP=$(nslookup $DOMAIN | grep -A 1 "Name:" | tail -1 | awk '{print $2}')

if [ "$RESOLVED_IP" == "$EXPECTED_IP" ]; then
    echo "✅ Root domain DNS is correct: $RESOLVED_IP"
else
    echo "❌ Root domain DNS is incorrect: $RESOLVED_IP (expected $EXPECTED_IP)"
fi

echo ""

# Check www subdomain
echo "Checking www subdomain (www.$DOMAIN)..."
WWW_IP=$(nslookup www.$DOMAIN | grep -A 1 "Name:" | tail -1 | awk '{print $2}')

if [ "$WWW_IP" == "$EXPECTED_IP" ]; then
    echo "✅ WWW subdomain DNS is correct: $WWW_IP"
else
    echo "❌ WWW subdomain DNS is incorrect: $WWW_IP (expected $EXPECTED_IP)"
fi

echo ""
echo "=========================================="
echo "Testing HTTP connectivity..."
echo "=========================================="

# Test HTTP connection
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN --max-time 5)

if [ "$HTTP_STATUS" == "200" ] || [ "$HTTP_STATUS" == "301" ] || [ "$HTTP_STATUS" == "302" ]; then
    echo "✅ HTTP connection successful (Status: $HTTP_STATUS)"
else
    echo "⚠️  HTTP connection issue (Status: $HTTP_STATUS)"
    echo "   This might be normal if SSL redirect is configured"
fi

echo ""
echo "=========================================="
echo "DNS Check Complete"
echo "=========================================="
echo ""
echo "If DNS is not resolving correctly:"
echo "1. Wait 5-30 minutes for DNS propagation"
echo "2. Check Namecheap DNS settings"
echo "3. Clear your local DNS cache"
echo ""
echo "Check DNS globally:"
echo "https://www.whatsmydns.net/#A/$DOMAIN"

