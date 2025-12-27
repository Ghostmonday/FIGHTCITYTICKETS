#!/bin/bash
set -e

# Deployment and Verification Script for FightCityTickets.com
# This script deploys the application and verifies DNS and page loading

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="${DOMAIN:-fightcitytickets.com}"
SERVER_IP="${SERVER_IP:-178.156.215.100}"
DEPLOY_PATH="/var/www/fightsftickets"
SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"

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

# Step 1: Check DNS Configuration
check_dns() {
    log_info "Checking DNS configuration for $DOMAIN..."
    
    # Check root domain
    RESOLVED_IP=$(nslookup $DOMAIN 2>/dev/null | grep -A 1 "Name:" | tail -1 | awk '{print $2}' || echo "")
    
    if [ -z "$RESOLVED_IP" ]; then
        log_error "DNS lookup failed for $DOMAIN"
        log_warning "DNS may not be configured yet. Expected IP: $SERVER_IP"
        log_info "Please configure DNS records:"
        echo "  Type: A, Name: @, Value: $SERVER_IP"
        echo "  Type: A, Name: www, Value: $SERVER_IP"
        return 1
    fi
    
    if [ "$RESOLVED_IP" == "$SERVER_IP" ]; then
        log_success "DNS is correctly configured: $DOMAIN -> $RESOLVED_IP"
        return 0
    else
        log_warning "DNS points to different IP: $RESOLVED_IP (expected $SERVER_IP)"
        log_info "This might be okay if you're using a different server"
        return 0
    fi
}

# Step 2: Check Server Connectivity
check_server() {
    log_info "Checking server connectivity ($SERVER_IP)..."
    
    if ping -c 1 -W 2 $SERVER_IP > /dev/null 2>&1; then
        log_success "Server is reachable"
        return 0
    else
        log_error "Server is not reachable at $SERVER_IP"
        return 1
    fi
}

# Step 3: Deploy Application
deploy_application() {
    log_info "Deploying application to server..."
    
    if [ ! -f "$SSH_KEY_PATH" ]; then
        log_error "SSH key not found at $SSH_KEY_PATH"
        log_info "Please set SSH_KEY_PATH or ensure key exists"
        return 1
    fi
    
    # Create deployment package
    log_info "Creating deployment package..."
    TEMP_DIR=$(mktemp -d)
    tar -czf "$TEMP_DIR/deploy.tar.gz" \
        --exclude='node_modules' \
        --exclude='.next' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='.env' \
        --exclude='venv' \
        --exclude='.venv' \
        --exclude='*.log' \
        -C .. .
    
    # Upload to server
    log_info "Uploading to server..."
    scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no \
        "$TEMP_DIR/deploy.tar.gz" root@"$SERVER_IP":/tmp/deploy.tar.gz
    
    # Extract and deploy on server
    log_info "Extracting and deploying on server..."
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no root@"$SERVER_IP" << ENDSSH
set -e
cd $DEPLOY_PATH || mkdir -p $DEPLOY_PATH && cd $DEPLOY_PATH

# Backup current deployment
if [ -d "backup" ]; then
    rm -rf backup.old
    mv backup backup.old
fi
mkdir -p backup
if [ -f "docker-compose.prod.yml" ]; then
    cp docker-compose.prod.yml backup/ 2>/dev/null || true
fi

# Extract new deployment
tar -xzf /tmp/deploy.tar.gz -C .
rm /tmp/deploy.tar.gz

# Ensure .env exists
if [ ! -f .env ]; then
    log_warning ".env file not found, creating template..."
    cat > .env << 'EOF'
APP_ENV=production
APP_URL=https://$DOMAIN
API_URL=https://$DOMAIN/api
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
NEXT_PUBLIC_API_BASE=https://$DOMAIN/api
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=fightsf
DATABASE_URL=postgresql+psycopg://postgres:changeme@db:5432/fightsf
EOF
fi

# Build and restart services
log_info "Building and starting services..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate

# Wait for services
sleep 30

# Check service status
docker-compose -f docker-compose.prod.yml ps

log_success "Deployment complete!"
ENDSSH
    
    rm -rf "$TEMP_DIR"
    log_success "Application deployed!"
}

# Step 4: Verify Page Loads
verify_page_loads() {
    log_info "Verifying page loads..."
    
    # Test HTTP connection
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$SERVER_IP 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" == "200" ] || [ "$HTTP_STATUS" == "301" ] || [ "$HTTP_STATUS" == "302" ]; then
        log_success "Server responds with HTTP $HTTP_STATUS"
        
        # Test domain if DNS is configured
        if check_dns > /dev/null 2>&1; then
            DOMAIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$DOMAIN 2>/dev/null || echo "000")
            if [ "$DOMAIN_STATUS" == "200" ] || [ "$DOMAIN_STATUS" == "301" ] || [ "$DOMAIN_STATUS" == "302" ]; then
                log_success "Domain responds with HTTP $DOMAIN_STATUS"
                log_success "Page is loading correctly!"
                return 0
            else
                log_warning "Domain responds with HTTP $DOMAIN_STATUS (may need DNS propagation)"
            fi
        fi
        
        return 0
    else
        log_error "Server not responding correctly (HTTP $HTTP_STATUS)"
        return 1
    fi
}

# Step 5: Check SSL
check_ssl() {
    log_info "Checking SSL configuration..."
    
    HTTPS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://$DOMAIN 2>/dev/null || echo "000")
    
    if [ "$HTTPS_STATUS" == "200" ] || [ "$HTTPS_STATUS" == "301" ] || [ "$HTTPS_STATUS" == "302" ]; then
        log_success "SSL is configured and working"
        return 0
    else
        log_warning "SSL not configured or not working (HTTP $HTTPS_STATUS)"
        log_info "To set up SSL, run on server:"
        echo "  ssh root@$SERVER_IP 'certbot --nginx -d $DOMAIN -d www.$DOMAIN'"
        return 1
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  FightCityTickets Deployment & Verification"
    echo "=========================================="
    echo ""
    echo "Domain: $DOMAIN"
    echo "Server IP: $SERVER_IP"
    echo ""
    
    # Check prerequisites
    if ! command -v curl > /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v ssh > /dev/null; then
        log_error "ssh is required but not installed"
        exit 1
    fi
    
    # Run checks and deployment
    check_server || exit 1
    check_dns || log_warning "DNS check failed, but continuing..."
    
    # Deploy
    read -p "Deploy application? (yes/no): " deploy_confirm
    if [ "$deploy_confirm" == "yes" ]; then
        deploy_application || exit 1
    else
        log_info "Skipping deployment"
    fi
    
    # Verify
    verify_page_loads || log_warning "Page verification failed"
    check_ssl || log_warning "SSL check failed"
    
    echo ""
    echo "=========================================="
    log_success "Deployment verification complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Verify DNS propagation: nslookup $DOMAIN"
    echo "  2. Test site: curl http://$DOMAIN"
    echo "  3. Set up SSL if needed: ssh root@$SERVER_IP 'certbot --nginx -d $DOMAIN -d www.$DOMAIN'"
    echo "  4. Check logs: ssh root@$SERVER_IP 'cd $DEPLOY_PATH && docker-compose -f docker-compose.prod.yml logs -f'"
    echo ""
}

main



