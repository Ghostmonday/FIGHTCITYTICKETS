#!/bin/bash
# FIGHTCITYTICKETS Production Deployment Script
# Generic deployment script - works with any Linux server

set -e

# Configuration - Set these environment variables or edit below
SERVER_IP="${SERVER_IP:-}"
SSH_USER="${SSH_USER:-root}"
SSH_KEY="${SSH_KEY:-~/.ssh/id_rsa}"
PROJECT_DIR="${PROJECT_DIR:-/var/www/fightcitytickets}"
DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-}"

# Validate required variables
if [ -z "$SERVER_IP" ]; then
    echo "❌ Error: SERVER_IP environment variable is required"
    echo "Usage: SERVER_IP=1.2.3.4 SSH_USER=root SSH_KEY=~/.ssh/key ./scripts/deploy-fightcity.sh"
    exit 1
fi

echo "🚀 Deploying FIGHTCITYTICKETS to production..."
echo "Server: $SERVER_IP"
echo "User: $SSH_USER"
echo "Project: $PROJECT_DIR"

# Wait for server to be ready
echo "⏳ Waiting for SSH to be available..."
while ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "echo 'SSH ready'" 2>/dev/null; do
    echo "Waiting for SSH..."
    sleep 2
done
echo "✅ SSH is available"

# Install Docker on server
echo "🐳 Installing Docker on server..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'INSTALL_DOCKER'
apt-get update -qq
apt-get install -y -qq apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/docker.gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update -qq
apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker
systemctl start docker
usermod -aG docker $USER || true
INSTALL_DOCKER

echo "✅ Docker installed"

# Create project directory
echo "📁 Creating project directory..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "mkdir -p $PROJECT_DIR"

# Clone repository
echo "📥 Cloning repository..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << CLONE_REPO
cd $PROJECT_DIR
if [ -d .git ]; then
    git pull origin main
else
    git clone https://github.com/Ghostmonday/FightSFTickets.git .
fi
CLONE_REPO

echo "✅ Repository cloned"

# Copy environment file
echo "⚙️  Setting up environment..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << SETUP_ENV
cd $PROJECT_DIR

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_change_this
POSTGRES_DB=fightcitytickets

# Stripe (USE TEST KEYS FOR TESTING)
STRIPE_SECRET_KEY=sk_test_your_test_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Lob (USE TEST KEY FOR TESTING)
LOB_API_KEY=test_your_lob_test_key

# DeepSeek AI
DEEPSEEK_API_KEY=sk_your_deepseek_api_key

# Google Places
NEXT_PUBLIC_GOOGLE_PLACES_API_KEY=your_google_api_key

# Application
NEXT_PUBLIC_API_BASE=http://localhost:8000
APP_ENV=prod
FRONTEND_URL=${DOMAIN:+https://$DOMAIN}
API_URL=http://localhost:8000
ENVEOF
fi
SETUP_ENV

echo "✅ Environment configured"

# Build and start containers
echo "🔨 Building Docker containers..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << BUILD_CONTAINERS
cd $PROJECT_DIR
docker compose down --remove-orphans 2>/dev/null || true
docker compose build --no-cache
docker compose up -d
sleep 10
docker ps
BUILD_CONTAINERS

echo "✅ Containers built and started"

# Setup Nginx
echo "🌐 Setting up Nginx..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << SETUP_NGINX
apt-get install -y -qq nginx

# Create nginx config
cat > /etc/nginx/sites-available/fightcitytickets << NGINXCONF
server {
    listen 80;
    server_name ${DOMAIN:-_} www.${DOMAIN:-_};

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
NGINXCONF

ln -sf /etc/nginx/sites-available/fightcitytickets /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
systemctl enable nginx
SETUP_NGINX

echo "✅ Nginx configured"

# Setup Certbot for SSL (optional)
if [ -n "$DOMAIN" ] && [ -n "$EMAIL" ]; then
    echo "🔒 SSL Certificate Setup..."
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << SETUP_SSL
apt-get install -y -qq certbot python3-certbot-nginx || true
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL || echo "SSL setup skipped (domain not pointing here yet)"
SETUP_SSL
else
    echo "⚠️  SSL setup skipped - set DOMAIN and EMAIL environment variables to enable"
fi

# Final status check
echo ""
echo "✅ Deployment Complete!"
echo "================================"
echo "Server IP: $SERVER_IP"
if [ -n "$DOMAIN" ]; then
    echo "Domain: $DOMAIN"
    echo "Website: https://$DOMAIN"
else
    echo "Website: http://$SERVER_IP"
fi
echo "API: http://$SERVER_IP:8000"
echo ""
echo "Quick Commands:"
echo "  Check status: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd $PROJECT_DIR && docker compose ps'"
echo "  View logs: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd $PROJECT_DIR && docker compose logs -f'"
echo "  Restart: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'cd $PROJECT_DIR && docker compose restart'"
echo ""
if [ -z "$DOMAIN" ]; then
    echo "Next Steps:"
    echo "1. Set DOMAIN environment variable and point DNS to $SERVER_IP"
    echo "2. Run certbot for SSL: ssh -i $SSH_KEY $SSH_USER@$SERVER_IP 'certbot --nginx -d \$DOMAIN -d www.\$DOMAIN'"
    echo ""
fi
