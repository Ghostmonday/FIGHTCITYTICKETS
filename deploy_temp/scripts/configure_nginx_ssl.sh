#!/bin/bash
# Configure Nginx to use SSL certificates
# Run this AFTER setup_ssl.sh

set -e

DOMAIN="fightcitytickets.com"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

echo "🔧 Configuring Nginx for SSL..."
echo "============================================================"

# Find Nginx config location
NGINX_CONF=""
PROJECT_DIR=""

# Check if nginx is in Docker
if docker ps | grep -q nginx; then
    echo "📦 Nginx is running in Docker"
    # Try to find docker-compose.yml
    PROJECT_DIR=$(find /var/www /root /opt -name "docker-compose.yml" -type f 2>/dev/null | head -1 | xargs dirname)
    if [ -n "$PROJECT_DIR" ]; then
        cd "$PROJECT_DIR"
        # Look for nginx config in the project
        NGINX_CONF=$(find . -name "*nginx*.conf" -o -name "nginx.conf" 2>/dev/null | head -1)
    fi
elif [ -f "/etc/nginx/sites-available/$DOMAIN" ]; then
    NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"
elif [ -f "/etc/nginx/nginx.conf" ]; then
    NGINX_CONF="/etc/nginx/nginx.conf"
fi

if [ -z "$NGINX_CONF" ] && [ -z "$PROJECT_DIR" ]; then
    echo "⚠️  Nginx config not found automatically"
    echo "   Creating a sample configuration..."
    
    # Create nginx config for Docker
    if [ -n "$PROJECT_DIR" ]; then
        mkdir -p "$PROJECT_DIR/nginx"
        NGINX_CONF="$PROJECT_DIR/nginx/nginx.conf"
    else
        mkdir -p /etc/nginx/sites-available
        NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"
    fi
fi

# Create/update Nginx config
echo ""
echo "📝 Creating Nginx SSL configuration..."

cat > "$NGINX_CONF" << 'NGINX_CONFIG'
# Nginx configuration for fightcitytickets.com with SSL

# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name fightcitytickets.com www.fightcitytickets.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name fightcitytickets.com www.fightcitytickets.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/fightcitytickets.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fightcitytickets.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://web:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://api:8000/health;
        access_log off;
    }
}
NGINX_CONFIG

echo "✅ Nginx configuration created at: $NGINX_CONF"

# If using Docker, update docker-compose.yml to mount certificates
if [ -n "$PROJECT_DIR" ] && [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
    echo ""
    echo "📦 Updating Docker Compose configuration..."
    
    # Check if volumes are already configured
    if ! grep -q "/etc/letsencrypt" "$PROJECT_DIR/docker-compose.yml"; then
        echo "   Adding SSL certificate volumes to docker-compose.yml..."
        # This is a simple approach - you may need to manually edit docker-compose.yml
        echo "   ⚠️  Please manually add these volumes to your nginx/web service:"
        echo "      volumes:"
        echo "        - /etc/letsencrypt:/etc/letsencrypt:ro"
        echo "        - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro"
    else
        echo "   ✅ SSL volumes already configured"
    fi
fi

# If using system nginx, enable site
if [ -f "/etc/nginx/sites-available/$DOMAIN" ]; then
    if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
        ln -s "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"
    fi
    echo ""
    echo "🔍 Testing Nginx configuration..."
    nginx -t
    echo ""
    echo "🔄 Reloading Nginx..."
    systemctl reload nginx
fi

# If using Docker, restart containers
if [ -n "$PROJECT_DIR" ]; then
    echo ""
    echo "🔄 Restarting Docker containers..."
    cd "$PROJECT_DIR"
    docker-compose restart web nginx 2>/dev/null || docker-compose restart
fi

echo ""
echo "============================================================"
echo "✅ SSL configuration complete!"
echo ""
echo "🧪 Testing HTTPS..."
sleep 2
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" | grep -q "200\|301\|302"; then
    echo "✅ HTTPS is working!"
else
    echo "⚠️  HTTPS test failed. Check logs:"
    if [ -n "$PROJECT_DIR" ]; then
        echo "   docker-compose logs web nginx"
    else
        echo "   tail -f /var/log/nginx/error.log"
    fi
fi

echo ""
echo "🌐 Your site should now be accessible at:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"

