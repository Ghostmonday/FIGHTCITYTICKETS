#!/bin/bash
set -e

# ============================================================================
# FightSFTickets - Simplified Deployment Script
# ============================================================================
# This script deploys FightSFTickets to Hetzner Cloud without jq dependency
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="fightcitytickets"
SERVER_NAME="${PROJECT_NAME}-prod"
DOMAIN="${DOMAIN:-fightcitytickets.com}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
DEPLOY_PATH="/var/www/${PROJECT_NAME}"
SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"

# Hetzner Configuration
HETZNER_API_TOKEN="${HETZNER_API_TOKEN}"
SERVER_TYPE="${SERVER_TYPE:-cx21}"  # 2 vCPU, 4GB RAM
SERVER_LOCATION="${SERVER_LOCATION:-ash}"  # Ashburn, VA
SERVER_IMAGE="${SERVER_IMAGE:-ubuntu-22.04}"

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to extract JSON value (simple grep/sed approach)
extract_json_value() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*\"" | head -1 | cut -d'"' -f4
}

extract_json_value_num() {
    echo "$1" | grep -o "\"$2\":[0-9]*" | head -1 | cut -d':' -f2
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if [ -z "$HETZNER_API_TOKEN" ]; then
        log_error "HETZNER_API_TOKEN environment variable is not set!"
        log_info "Please set it with: export HETZNER_API_TOKEN='your-token'"
        exit 1
    fi

    if ! command -v curl >/dev/null 2>&1; then
        log_error "curl is not installed. Please install it first."
        exit 1
    fi

    log_success "Prerequisites check completed!"
}

# Function to create or get SSH key in Hetzner
setup_ssh_key() {
    log_info "Setting up SSH key in Hetzner..."

    # Check if SSH key exists locally
    if [ ! -f "$SSH_KEY_PATH.pub" ]; then
        log_warning "SSH key not found at $SSH_KEY_PATH.pub"
        log_info "Generating new SSH key..."
        ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "deploy@${PROJECT_NAME}"
    fi

    SSH_PUBLIC_KEY=$(cat "$SSH_KEY_PATH.pub")
    SSH_KEY_NAME="${PROJECT_NAME}-deploy-key"

    # Check if key already exists in Hetzner
    log_info "Checking for existing SSH key in Hetzner..."
    EXISTING_KEYS=$(curl -s -H "Authorization: Bearer $HETZNER_API_TOKEN" \
        "https://api.hetzner.cloud/v1/ssh_keys")

    # Simple check for existing key
    if echo "$EXISTING_KEYS" | grep -q "\"name\":\"$SSH_KEY_NAME\""; then
        log_info "SSH key already exists in Hetzner"
        # Extract key ID
        SSH_KEY_ID=$(echo "$EXISTING_KEYS" | grep -B2 -A2 "\"name\":\"$SSH_KEY_NAME\"" | grep "\"id\":" | head -1 | grep -o '[0-9]*')
    else
        log_info "Creating new SSH key in Hetzner..."
        RESPONSE=$(curl -s -X POST \
            -H "Authorization: Bearer $HETZNER_API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"name\":\"$SSH_KEY_NAME\",\"public_key\":\"$SSH_PUBLIC_KEY\"}" \
            "https://api.hetzner.cloud/v1/ssh_keys")

        SSH_KEY_ID=$(extract_json_value_num "$RESPONSE" "id")
        if [ -z "$SSH_KEY_ID" ]; then
            log_error "Failed to create SSH key!"
            echo "Response: $RESPONSE"
            exit 1
        fi
        log_success "SSH key created (ID: $SSH_KEY_ID)"
    fi
}

# Function to create server
create_server() {
    log_info "Checking for existing server..."

    # Check if server already exists
    SERVERS=$(curl -s -H "Authorization: Bearer $HETZNER_API_TOKEN" \
        "https://api.hetzner.cloud/v1/servers")

    if echo "$SERVERS" | grep -q "\"name\":\"$SERVER_NAME\""; then
        log_warning "Server '$SERVER_NAME' already exists"
        # Extract server info
        SERVER_INFO=$(echo "$SERVERS" | grep -B5 -A15 "\"name\":\"$SERVER_NAME\"")
        SERVER_ID=$(echo "$SERVER_INFO" | grep "\"id\":" | head -1 | grep -o '[0-9]*')
        SERVER_IP=$(echo "$SERVER_INFO" | grep "\"ip\":" | head -1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+')

        log_info "Server IP: $SERVER_IP"
        return 0
    fi

    log_info "Creating new Hetzner Cloud server..."
    log_info "Server Type: $SERVER_TYPE"
    log_info "Location: $SERVER_LOCATION"
    log_info "Image: $SERVER_IMAGE"

    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $HETZNER_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$SERVER_NAME\",
            \"server_type\": \"$SERVER_TYPE\",
            \"location\": \"$SERVER_LOCATION\",
            \"image\": \"$SERVER_IMAGE\",
            \"ssh_keys\": [$SSH_KEY_ID],
            \"start_after_create\": true,
            \"labels\": {
                \"project\": \"$PROJECT_NAME\",
                \"environment\": \"production\"
            }
        }" \
        "https://api.hetzner.cloud/v1/servers")

    SERVER_ID=$(extract_json_value_num "$RESPONSE" "id")
    # Extract IP from response
    SERVER_IP=$(echo "$RESPONSE" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)

    if [ -z "$SERVER_ID" ] || [ -z "$SERVER_IP" ]; then
        log_error "Failed to create server!"
        echo "Response: $RESPONSE"
        exit 1
    fi

    log_success "Server created successfully!"
    log_info "Server ID: $SERVER_ID"
    log_info "Server IP: $SERVER_IP"

    # Wait for server to be ready
    log_info "Waiting for server to be ready (this may take 1-2 minutes)..."
    sleep 60

    # Wait for SSH to be available
    log_info "Waiting for SSH to be available..."
    for i in {1..30}; do
        if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "$SSH_KEY_PATH" root@"$SERVER_IP" "echo 'SSH ready'" 2>/dev/null; then
            log_success "SSH is available!"
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""
}

# Function to install dependencies on server
install_dependencies() {
    log_info "Installing dependencies on server..."

    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" root@"$SERVER_IP" << 'ENDSSH'
set -e

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw \
    nginx \
    certbot \
    python3-certbot-nginx

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed"
fi

# Configure firewall
echo "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload

echo "Dependencies installed successfully!"
ENDSSH

    log_success "Dependencies installed!"
}

# Function to create deploy user
create_deploy_user() {
    log_info "Creating deploy user..."

    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" root@"$SERVER_IP" << ENDSSH
set -e

# Create deploy user if doesn't exist
if ! id -u $DEPLOY_USER > /dev/null 2>&1; then
    useradd -m -s /bin/bash $DEPLOY_USER
    usermod -aG docker $DEPLOY_USER

    # Set up SSH for deploy user
    mkdir -p /home/$DEPLOY_USER/.ssh
    cp /root/.ssh/authorized_keys /home/$DEPLOY_USER/.ssh/
    chown -R $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh
    chmod 700 /home/$DEPLOY_USER/.ssh
    chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys

    echo "$DEPLOY_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$DEPLOY_USER

    echo "Deploy user created!"
else
    echo "Deploy user already exists"
fi
ENDSSH

    log_success "Deploy user configured!"
}

# Function to deploy application
deploy_application() {
    log_info "Deploying application to server..."

    # Create deployment directory
    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" "mkdir -p $DEPLOY_PATH && chown -R $DEPLOY_USER:$DEPLOY_USER $DEPLOY_PATH"

    # Copy project files using tar (works without rsync)
    log_info "Copying project files..."
    tar czf - --exclude='node_modules' --exclude='.next' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='.env' --exclude='venv' --exclude='.venv' . | \
        ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" "tar xzf - -C $DEPLOY_PATH"

    log_success "Project files copied!"
}

# Function to configure environment
configure_environment() {
    log_info "Configuring environment variables..."

    # Prompt for API keys
    echo ""
    echo "=== ENTER API KEYS ==="
    read -p "Stripe Secret Key: " STRIPE_SECRET_KEY
    read -p "Stripe Webhook Secret (press Enter to skip for now): " STRIPE_WEBHOOK_SECRET
    read -p "Lob API Key: " LOB_API_KEY
    read -p "OpenAI API Key: " OPENAI_API_KEY
    read -p "DeepSeek API Key: " DEEPSEEK_API_KEY
    echo ""

    # Create .env file
    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << ENDSSH
cat > $DEPLOY_PATH/.env << 'EOF'
# Application Settings
APP_ENV=production
APP_URL=https://$DOMAIN
API_URL=https://$DOMAIN/api
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=fightsf
DATABASE_URL=postgresql://postgres:\${POSTGRES_PASSWORD}@db:5432/fightsf

# API Keys
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
LOB_API_KEY=${LOB_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Frontend
NEXT_PUBLIC_API_BASE=https://$DOMAIN/api
EOF

chown $DEPLOY_USER:$DEPLOY_USER $DEPLOY_PATH/.env
chmod 600 $DEPLOY_PATH/.env
ENDSSH

    log_success "Environment configured!"
}

# Function to create production docker-compose file
create_production_compose() {
    log_info "Creating production docker-compose configuration..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << 'ENDSSH'
cat > /tmp/docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    restart: unless-stopped
    expose:
      - "8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  web:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    env_file:
      - .env
    restart: unless-stopped
    expose:
      - "3000"
    depends_on:
      - api

  db:
    image: postgres:16
    env_file:
      - .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot:ro
    depends_on:
      - web
      - api

volumes:
  postgres_data:
    driver: local

networks:
  default:
    name: fightcitytickets_network
EOF
ENDSSH

    log_success "Production docker-compose created!"
}

# Function to configure Nginx
configure_nginx() {
    log_info "Configuring Nginx..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << ENDSSH
cat > $DEPLOY_PATH/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=general_limit:10m rate=100r/s;

    upstream api_backend {
        server api:8000;
    }

    upstream web_backend {
        server web:3000;
    }

    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;

        # Let's Encrypt challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Temporary: proxy to services (before SSL)
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://api_backend/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        location /health {
            proxy_pass http://api_backend/health;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
        }

        location / {
            limit_req zone=general_limit burst=50 nodelay;
            proxy_pass http://web_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
        }
    }
}
EOF
ENDSSH

    log_success "Nginx configured!"
}

# Function to start services
start_services() {
    log_info "Starting Docker services..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << ENDSSH
cd $DEPLOY_PATH

# Copy production compose file
if [ -f /tmp/docker-compose.prod.yml ]; then
    cp /tmp/docker-compose.prod.yml docker-compose.prod.yml
fi

# Build and start services
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check service status
docker-compose -f docker-compose.prod.yml ps

echo "Services started!"
ENDSSH

    log_success "Services started!"
}

# Function to run database migrations
run_migrations() {
    log_info "Running database migrations..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << ENDSSH
cd $DEPLOY_PATH
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || echo "Migrations completed or not needed"
ENDSSH

    log_success "Migrations completed!"
}

# Function to display deployment summary
display_summary() {
    echo ""
    echo "=========================================="
    log_success "Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "Server Details:"
    echo "  IP Address: $SERVER_IP"
    echo "  Domain: $DOMAIN"
    echo "  Deploy Path: $DEPLOY_PATH"
    echo ""
    echo "Services:"
    echo "  Frontend: http://$SERVER_IP:80"
    echo "  Backend API: http://$SERVER_IP/api"
    echo "  Health Check: http://$SERVER_IP/health"
    echo "  Admin Panel: http://$SERVER_IP/admin"
    echo ""
    echo "Next Steps:"
    echo "  1. Point your domain $DOMAIN to $SERVER_IP"
    echo "  2. Wait for DNS propagation (may take up to 24 hours)"
    echo "  3. Run SSL setup: ssh root@$SERVER_IP 'certbot --nginx -d $DOMAIN -d www.$DOMAIN'"
    echo "  4. Uncomment HTTPS section in nginx.conf and restart nginx"
    echo "  5. Test Stripe webhooks: https://$DOMAIN/api/webhooks/stripe"
    echo "  6. Configure Stripe webhook URL in Stripe Dashboard"
    echo "  7. Access admin panel: https://$DOMAIN/admin"
    echo ""
    echo "Useful Commands:"
    echo "  SSH to server: ssh -i $SSH_KEY_PATH root@$SERVER_IP"
    echo "  View logs: ssh root@$SERVER_IP 'cd $DEPLOY_PATH && docker-compose -f docker-compose.prod.yml logs -f'"
    echo "  Restart services: ssh root@$SERVER_IP 'cd $DEPLOY_PATH && docker-compose -f docker-compose.prod.yml restart'"
    echo "  Update deployment: ./scripts/update_deployment.sh"
    echo ""
    echo "=========================================="
}

# Main deployment flow
main() {
    echo "=========================================="
    echo "  FightSFTickets Hetzner Deployment"
    echo "=========================================="
    echo ""

    check_prerequisites
    setup_ssh_key
    create_server
    install_dependencies
    create_deploy_user
    deploy_application
    configure_environment
    create_production_compose
    configure_nginx
    start_services
    run_migrations
    display_summary

    log_success "Deployment script completed successfully!"
}

# Run main function
main
