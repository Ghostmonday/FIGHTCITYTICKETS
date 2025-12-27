#!/bin/bash
# SSL Setup Script for fightcitytickets.com
# Run this on the server: ssh root@178.156.215.100

set -e

DOMAIN="fightcitytickets.com"
EMAIL="support@fightcitytickets.com"  # Change to your email
SERVER_IP="178.156.215.100"

echo "🔒 Setting up SSL certificate for $DOMAIN..."
echo "============================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root"
    exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Check if nginx is running (either in Docker or system)
NGINX_IN_DOCKER=false
if docker ps | grep -q nginx; then
    NGINX_IN_DOCKER=true
    echo "📦 Nginx is running in Docker"
elif systemctl is-active --quiet nginx; then
    echo "📦 Nginx is running as system service"
else
    echo "⚠️  Nginx not detected. Checking Docker Compose..."
    # Try to find docker-compose.yml
    PROJECT_DIR=$(find /var/www /root /opt -name "docker-compose.yml" -type f 2>/dev/null | head -1 | xargs dirname)
    if [ -n "$PROJECT_DIR" ]; then
        cd "$PROJECT_DIR"
        if docker-compose ps | grep -q web; then
            NGINX_IN_DOCKER=true
            echo "📦 Found Docker Compose project at $PROJECT_DIR"
        fi
    fi
fi

# Check DNS resolution
echo ""
echo "🔍 Verifying DNS resolution..."
if nslookup "$DOMAIN" | grep -q "$SERVER_IP"; then
    echo "✅ DNS is resolving correctly"
else
    echo "⚠️  DNS may not be fully propagated yet"
    echo "   Continuing anyway (certbot will verify)..."
fi

# Get certificate using standalone mode (works with Docker)
echo ""
echo "📜 Obtaining SSL certificate..."
echo "   Using standalone mode (will temporarily use port 80)..."

# Stop any service using port 80 temporarily
if [ "$NGINX_IN_DOCKER" = true ]; then
    echo "   Stopping Docker nginx/web service temporarily..."
    if [ -n "$PROJECT_DIR" ]; then
        cd "$PROJECT_DIR"
        docker-compose stop web nginx 2>/dev/null || true
    fi
else
    systemctl stop nginx 2>/dev/null || true
fi

# Wait a moment for port to be free
sleep 2

# Obtain certificate
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --preferred-challenges http

# Restart services
echo ""
echo "🔄 Restarting services..."
if [ "$NGINX_IN_DOCKER" = true ]; then
    if [ -n "$PROJECT_DIR" ]; then
        cd "$PROJECT_DIR"
        docker-compose up -d web nginx 2>/dev/null || docker-compose up -d
    fi
else
    systemctl start nginx
fi

# Check certificate location
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
if [ -d "$CERT_PATH" ]; then
    echo ""
    echo "✅ Certificate obtained successfully!"
    echo "   Certificate location: $CERT_PATH"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Configure Nginx to use SSL certificates"
    echo "   2. Update Nginx config to redirect HTTP → HTTPS"
    echo "   3. Restart Nginx"
    echo ""
    echo "   Certificate files:"
    echo "   - Full chain: $CERT_PATH/fullchain.pem"
    echo "   - Private key: $CERT_PATH/privkey.pem"
else
    echo "❌ Certificate not found at expected location"
    exit 1
fi

# Set up auto-renewal
echo ""
echo "🔄 Setting up auto-renewal..."
(crontab -l 2>/dev/null | grep -v "certbot renew" || true; echo "0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx || (cd $PROJECT_DIR && docker-compose restart web nginx)'") | crontab -
echo "✅ Auto-renewal configured (runs daily at 3 AM)"

echo ""
echo "============================================================"
echo "✅ SSL setup complete!"
echo ""
echo "⚠️  IMPORTANT: You still need to configure Nginx to use these certificates."
echo "   See scripts/configure_nginx_ssl.sh for automated configuration."
