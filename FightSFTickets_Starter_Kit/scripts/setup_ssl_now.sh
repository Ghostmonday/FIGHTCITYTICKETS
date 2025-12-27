#!/bin/bash
# Quick SSL Setup - Run this on your server
# This assumes DNS will be ready soon

echo "=========================================="
echo "SSL Setup for fightcitytickets.com"
echo "=========================================="
echo ""
echo "Run these commands on your server:"
echo "  ssh root@178.156.215.100"
echo ""
echo "Then run:"
echo ""
echo "1. Install Certbot:"
echo "   apt-get update"
echo "   apt-get install -y certbot python3-certbot-nginx"
echo ""
echo "2. Get SSL certificate:"
echo "   certbot --nginx -d fightcitytickets.com -d www.fightcitytickets.com"
echo ""
echo "3. Follow prompts (choose option 2 to redirect HTTP to HTTPS)"
echo ""
echo "=========================================="

