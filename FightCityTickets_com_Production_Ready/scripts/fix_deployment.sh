#!/bin/bash
# Fix deployment for www.fightcitytickets.com
# This script fixes common deployment issues

set -e

DOMAIN="fightcitytickets.com"
SERVER_IP="${SERVER_IP:-178.156.215.100}"

echo "🔧 Fixing deployment for $DOMAIN"
echo "============================================================"

# Check if we're on the server or local
if [ -d "/var/www/fightcitytickets" ]; then
    echo "✅ Running on server"
    DEPLOY_DIR="/var/www/fightcitytickets"
    cd "$DEPLOY_DIR"
else
    echo "⚠️  Running locally - will SSH to server"
    echo "   Make sure you have SSH access to $SERVER_IP"
fi

echo ""
echo "Step 1: Checking Docker containers..."
if command -v docker &> /dev/null; then
    docker ps -a
    echo ""
    echo "Stopping existing containers..."
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
else
    echo "⚠️  Docker not found"
fi

echo ""
echo "Step 2: Verifying nginx configuration..."
if [ ! -d "nginx/conf.d" ]; then
    echo "⚠️  Creating nginx directory structure..."
    mkdir -p nginx/conf.d
fi

if [ ! -f "nginx/conf.d/fightcitytickets.conf" ]; then
    echo "⚠️  nginx config missing - this should be created by deployment"
fi

echo ""
echo "Step 3: Checking docker-compose.yml..."
if grep -q "nginx:" docker-compose.yml 2>/dev/null; then
    echo "✅ nginx service found in docker-compose.yml"
else
    echo "❌ nginx service NOT found in docker-compose.yml"
    echo "   This is the main issue - nginx needs to be added!"
    exit 1
fi

echo ""
echo "Step 4: Starting services..."
docker-compose up -d --build 2>/dev/null || docker compose up -d --build

echo ""
echo "Step 5: Waiting for services to start..."
sleep 10

echo ""
echo "Step 6: Checking service health..."
docker-compose ps 2>/dev/null || docker compose ps

echo ""
echo "Step 7: Testing endpoints..."
echo "Testing HTTP (port 80)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q "200\|301\|302"; then
    echo "✅ HTTP is responding"
else
    echo "❌ HTTP not responding"
fi

echo ""
echo "Testing API endpoint..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health | grep -q "200"; then
    echo "✅ API is responding"
else
    echo "❌ API not responding"
fi

echo ""
echo "Step 8: Checking nginx logs..."
docker-compose logs --tail=20 nginx 2>/dev/null || docker compose logs --tail=20 nginx || echo "No nginx logs"

echo ""
echo "============================================================"
echo "✅ Deployment fix complete!"
echo ""
echo "Next steps:"
echo "1. Verify DNS is pointing to $SERVER_IP:"
echo "   nslookup $DOMAIN"
echo "   nslookup www.$DOMAIN"
echo ""
echo "2. Set up SSL certificate:"
echo "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "3. Test the site:"
echo "   curl http://$DOMAIN"
echo "   curl https://$DOMAIN (after SSL setup)"

