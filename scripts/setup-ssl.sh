#!/bin/bash
# SSL Setup Script for FIGHTCITYTICKETS
# Run this script to obtain and renew Let's Encrypt SSL certificates

set -e

DOMAIN="fightcitytickets.com"
EMAIL="amir@example.com"  # CHANGE THIS
DATA_PATH="/var/www/certbot"
NGINX_CONTAINER="nginx"

echo "🔒 Setting up SSL for $DOMAIN"

# Stop nginx temporarily to allow certbot to verify
echo "⏹️  Stopping nginx..."
docker-compose stop nginx

# Create required directories
mkdir -p "$DATA_PATH"
mkdir -p "/etc/letsencrypt/live/$DOMAIN"

# Obtain certificate
echo "📜 Obtaining Let's Encrypt certificate..."
docker run --rm \
    -v "$DATA_PATH:/var/www/certbot" \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    certbot/certbot \
    certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --domain "$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive

# Restart nginx
echo "▶️  Starting nginx..."
docker-compose start nginx

echo "✅ SSL certificate obtained successfully!"
echo ""
echo "Certificate expires: $(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d= -f2)"
echo ""
echo "To renew: ./scripts/setup-ssl.sh"
```

```sh
#!/bin/bash
# Setup Fail2Ban for Nginx
# Protects against brute force, DDoS, and common attacks

set -e

CONTAINER_NAME="fail2ban"

echo "🛡️  Setting up Fail2Ban for Nginx..."

# Create fail2ban configuration directory
mkdir -p /opt/fail2ban

# Create jail.local configuration
cat > /opt/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8 ::1 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 10
findtime = 60
bantime = 600

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[sshd-ddos]
enabled = true
port = ssh
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 6
bantime = 3600

[dropbear]
enabled = true
port = ssh
filter = dropbear
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

# Create nginx-botsearch filter
cat > /opt/fail2ban/nginx-botsearch.conf << 'EOF'
[Definition]
failregex = ^<HOST> -.*"(GET|POST|HEAD).*?(acunetix|nikto|webshag|havij|sqlmap|python-requests|curl|wget|scan|bot|spider|crawler).*?".*?$
            ^<HOST> -.*"(GET|POST|HEAD).*?(\.php\?|_vti_|\.env|wp-admin|administrator|phpmyadmin|admin|console).*?".*? 404
ignoreregex =
EOF

echo "✅ Fail2ban configuration created at /opt/fail2ban/jail.local"
echo ""
echo "To run fail2ban:"
echo "  docker run -d --name fail2ban \\"
echo "    -v /opt/fail2ban/jail.local:/etc/fail2ban/jail.local \\"
echo "    -v /var/log:/var/log \\"
echo "    --cap-add NET_ADMIN \\"
echo "    --network host \\"
echo "    crazymax/fail2ban"
```

```sh
#!/bin/bash
# Security Audit Script
# Run this to check your server's security posture

echo "🔍 Security Audit for FIGHTCITYTICKETS"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: Not running as root. Some checks may fail."
    echo ""
fi

echo "1. 🔐 SSL/TLS Configuration"
echo "---------------------------"
if [ -f "/etc/letsencrypt/live/fightcitytickets.com/fullchain.pem" ]; then
    echo "✅ SSL Certificate installed"
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/fightcitytickets.com/fullchain.pem 2>/dev/null | cut -d= -f2)
    echo "   Expires: $EXPIRY"
else
    echo "❌ No SSL certificate found"
fi
echo ""

echo "2. 🔥 Firewall Status"
echo "---------------------"
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "✅ UFW is active"
        ufw status | head -10
    else
        echo "❌ UFW is not active"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if firewall-cmd --state &> /dev/null; then
        echo "✅ Firewalld is active"
    else
        echo "❌ Firewalld is not active"
    fi
else
    echo "⚠️  No firewall detected"
fi
echo ""

echo "3. 🚪 Open Ports"
echo "----------------"
echo "Listening ports:"
netstat -tuln 2>/dev/null | grep LISTEN || ss -tuln | grep LISTEN
echo ""

echo "4. 🔑 SSH Configuration"
echo "------------------------"
if [ -f "/etc/ssh/sshd_config" ]; then
    if grep -q "^PermitRootLogin no" /etc/ssh/sshd_config; then
        echo "✅ Root login disabled"
    else
        echo "⚠️  Root login might be enabled"
    fi
    if grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config; then
        echo "✅ Password authentication disabled"
    else
        echo "⚠️  Password authentication might be enabled"
    fi
fi
echo ""

echo "5. 🐳 Docker Security"
echo "---------------------"
if command -v docker &> /dev/null; then
    echo "Docker version: $(docker --version)"
    echo "Containers:"
    docker ps --format "  {{.Names}}: {{.Status}}" 2>/dev/null || echo "  Unable to list containers"
else
    echo "Docker not found"
fi
echo ""

echo "6. 📝 Recent Auth Failures"
echo "--------------------------"
if [ -f "/var/log/auth.log" ]; then
    echo "Recent failed SSH attempts:"
    grep "Failed password" /var/log/auth.log 2>/dev/null | tail -5 || echo "  No recent failures found"
else
    echo "Auth log not accessible"
fi
echo ""

echo "7. 🌐 Nginx Security Headers"
echo "----------------------------"
echo "Checking security headers for fightcitytickets.com..."
HEADERS=$(curl -sI https://fightcitytickets.com 2>/dev/null)
for header in "X-Frame-Options" "X-Content-Type-Options" "X-XSS-Protection" "Strict-Transport-Security" "Content-Security-Policy"; do
    if echo "$HEADERS" | grep -qi "$header"; then
        VALUE=$(echo "$HEADERS" | grep -i "$header" | cut -d: -f2- | tr -d '\r')
        echo "✅ $header: $VALUE"
    else
        echo "❌ $header: Missing"
    fi
done
echo ""

echo "======================================"
echo "✅ Security audit complete"
echo ""
echo "Quick wins:"
echo "  - Run SSL setup: ./scripts/setup-ssl.sh"
echo "  - Enable UFW: sudo ufw enable"
echo "  - Harden SSH: Edit /etc/ssh/sshd_config"
