#!/bin/bash
set -e

# Manual Deployment Script for FightCityTickets.com
# Uses scp instead of rsync (works on Windows Git Bash)
# Addresses zombie processes and memory issues

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SERVER_IP="${SERVER_IP:-178.156.215.100}"
SERVER_USER="${SERVER_USER:-root}"
DEPLOY_PATH="${DEPLOY_PATH:-/var/www/fightcitytickets}"
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

# Step 1: Locate project directory on server
locate_project_dir() {
    log_info "Locating project directory on server..."
    
    PROJECT_DIR=$(ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
        "find / -name 'docker-compose.yml' -o -name 'docker-compose.prod.yml' 2>/dev/null | head -1 | xargs dirname" 2>/dev/null || echo "")
    
    if [ -z "$PROJECT_DIR" ]; then
        log_warning "Project directory not found, using default: $DEPLOY_PATH"
        PROJECT_DIR="$DEPLOY_PATH"
    else
        log_success "Found project directory: $PROJECT_DIR"
    fi
    
    echo "$PROJECT_DIR"
}

# Step 2: Check for zombie processes
check_zombies() {
    log_info "Checking for zombie processes on server..."
    
    ZOMBIE_COUNT=$(ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
        "ps aux | grep -c '<defunct>' || echo '0'" 2>/dev/null || echo "0")
    
    if [ "$ZOMBIE_COUNT" -gt 0 ]; then
        log_warning "Found $ZOMBIE_COUNT zombie processes"
        log_info "These will be cleared by container restart"
        return 1
    else
        log_success "No zombie processes found"
        return 0
    fi
}

# Step 3: Check memory usage
check_memory() {
    log_info "Checking server memory usage..."
    
    MEMORY_INFO=$(ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
        "free -m | grep Mem | awk '{used=\$3; total=\$2; pct=int(used*100/total); print pct}'" 2>/dev/null || echo "0")
    
    if [ "$MEMORY_INFO" -gt 80 ]; then
        log_error "Memory usage is high: ${MEMORY_INFO}%"
        log_warning "Consider restarting containers to free memory"
        return 1
    else
        log_success "Memory usage: ${MEMORY_INFO}%"
        return 0
    fi
}

# Step 4: Create deployment package
create_deployment_package() {
    log_info "Creating deployment package..."
    
    TEMP_DIR=$(mktemp -d)
    DEPLOY_FILE="$TEMP_DIR/deploy.tar.gz"
    
    # Create tar.gz excluding unnecessary files
    tar -czf "$DEPLOY_FILE" \
        --exclude='node_modules' \
        --exclude='.next' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='.env' \
        --exclude='venv' \
        --exclude='.venv' \
        --exclude='*.log' \
        --exclude='.pytest_cache' \
        --exclude='coverage' \
        --exclude='dist' \
        --exclude='build' \
        -C .. . 2>/dev/null
    
    if [ ! -f "$DEPLOY_FILE" ]; then
        log_error "Failed to create deployment package"
        return 1
    fi
    
    PACKAGE_SIZE=$(du -h "$DEPLOY_FILE" | cut -f1)
    log_success "Deployment package created: $PACKAGE_SIZE"
    echo "$DEPLOY_FILE"
}

# Step 5: Upload to server
upload_to_server() {
    local package_file="$1"
    log_info "Uploading deployment package to server..."
    
    scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no \
        "$package_file" "$SERVER_USER@$SERVER_IP:/tmp/deploy.tar.gz"
    
    if [ $? -eq 0 ]; then
        log_success "Package uploaded successfully"
        return 0
    else
        log_error "Failed to upload package"
        return 1
    fi
}

# Step 6: Deploy on server
deploy_on_server() {
    local project_dir="$1"
    log_info "Deploying on server (directory: $project_dir)..."
    
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << ENDSSH
set -e

cd "$project_dir" || (mkdir -p "$project_dir" && cd "$project_dir")

# Backup current deployment
log_info() { echo "[INFO] \$1"; }
log_success() { echo "[SUCCESS] \$1"; }
log_warning() { echo "[WARNING] \$1"; }

log_info "Backing up current deployment..."
if [ -f "docker-compose.prod.yml" ] || [ -f "docker-compose.yml" ]; then
    mkdir -p backup
    cp docker-compose*.yml backup/ 2>/dev/null || true
    cp .env backup/ 2>/dev/null || true
fi

# Stop containers to clear zombies and free memory
log_info "Stopping containers..."
docker-compose down 2>/dev/null || docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Wait a moment for cleanup
sleep 5

# Extract new deployment
log_info "Extracting deployment package..."
tar -xzf /tmp/deploy.tar.gz -C . --strip-components=1 || tar -xzf /tmp/deploy.tar.gz -C .
rm /tmp/deploy.tar.gz

# Ensure .env exists
if [ ! -f .env ]; then
    log_warning "Creating .env template..."
    cat > .env << 'EOF'
APP_ENV=production
APP_URL=https://fightcitytickets.com
API_URL=https://fightcitytickets.com/api
NEXT_PUBLIC_API_BASE=https://fightcitytickets.com/api
CORS_ORIGINS=https://fightcitytickets.com,https://www.fightcitytickets.com
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=fightsf
DATABASE_URL=postgresql+psycopg://postgres:changeme@db:5432/fightsf
EOF
fi

# Build and start services
log_info "Building and starting services..."
COMPOSE_FILE="docker-compose.prod.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

docker-compose -f "$COMPOSE_FILE" up -d --build --force-recreate

# Wait for services to start
log_info "Waiting for services to start..."
sleep 30

# Check service status
log_info "Service status:"
docker-compose -f "$COMPOSE_FILE" ps

# Check for zombies after restart
ZOMBIES=\$(ps aux | grep -c '<defunct>' || echo '0')
if [ "\$ZOMBIES" -gt 0 ]; then
    log_warning "Still \$ZOMBIES zombie processes (may clear on next check)"
else
    log_success "No zombie processes detected"
fi

# Check memory
MEM_USAGE=\$(free -m | grep Mem | awk '{used=\$3; total=\$2; pct=int(used*100/total); print pct}')
log_info "Memory usage: \$MEM_USAGE%"

log_success "Deployment complete!"
ENDSSH

    if [ $? -eq 0 ]; then
        log_success "Deployment completed successfully"
        return 0
    else
        log_error "Deployment failed"
        return 1
    fi
}

# Step 7: Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if services are running
    SERVICE_STATUS=$(ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
        "cd $DEPLOY_PATH && docker-compose ps 2>/dev/null | grep -c 'Up' || docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -c 'Up' || echo '0'" 2>/dev/null || echo "0")
    
    if [ "$SERVICE_STATUS" -gt 0 ]; then
        log_success "Services are running"
        return 0
    else
        log_warning "Services may not be running correctly"
        return 1
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  Manual Deployment - FightCityTickets"
    echo "=========================================="
    echo ""
    echo "Server: $SERVER_IP"
    echo "User: $SERVER_USER"
    echo ""
    
    # Prerequisites
    if [ ! -f "$SSH_KEY_PATH" ]; then
        log_error "SSH key not found at $SSH_KEY_PATH"
        log_info "Please set SSH_KEY_PATH or ensure key exists"
        exit 1
    fi
    
    # Pre-deployment checks
    check_zombies
    check_memory
    
    # Locate project directory
    PROJECT_DIR=$(locate_project_dir)
    
    # Create and upload package
    PACKAGE_FILE=$(create_deployment_package)
    if [ -z "$PACKAGE_FILE" ]; then
        exit 1
    fi
    
    upload_to_server "$PACKAGE_FILE" || exit 1
    
    # Deploy
    deploy_on_server "$PROJECT_DIR" || exit 1
    
    # Cleanup
    rm -rf "$(dirname "$PACKAGE_FILE")"
    
    # Verify
    verify_deployment
    
    echo ""
    echo "=========================================="
    log_success "Deployment complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Check logs: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_DIR && docker-compose logs -f'"
    echo "  2. Verify services: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_DIR && docker-compose ps'"
    echo "  3. Test endpoints: curl http://$SERVER_IP/health"
    echo "  4. Configure DNS: Point fightcitytickets.com to $SERVER_IP"
    echo "  5. Set up SSL: ssh $SERVER_USER@$SERVER_IP 'certbot --nginx -d fightcitytickets.com'"
    echo ""
}

main


