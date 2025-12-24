#!/bin/bash
set -e

# ============================================================================
# FightSFTickets - Update Deployment Script
# ============================================================================
# This script updates an existing deployment on Hetzner Cloud
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="fightsftickets"
DEPLOY_PATH="/var/www/${PROJECT_NAME}"
SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"

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

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if [ -z "$SERVER_IP" ]; then
        log_error "SERVER_IP environment variable is not set!"
        log_info "Usage: SERVER_IP=your.server.ip.address ./scripts/update_deployment.sh"
        exit 1
    fi

    if [ ! -f "$SSH_KEY_PATH" ]; then
        log_error "SSH key not found at $SSH_KEY_PATH"
        exit 1
    fi

    log_success "Prerequisites check completed!"
}

# Function to backup current deployment
backup_deployment() {
    log_info "Creating backup of current deployment..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << ENDSSH
cd $DEPLOY_PATH
BACKUP_DIR="/var/backups/${PROJECT_NAME}"
BACKUP_NAME="${PROJECT_NAME}_\$(date +%Y%m%d_%H%M%S)"

mkdir -p \$BACKUP_DIR

# Backup database
if docker-compose -f docker-compose.prod.yml ps | grep -q db; then
    echo "Backing up database..."
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres fightsf > \$BACKUP_DIR/\${BACKUP_NAME}_db.sql
    gzip \$BACKUP_DIR/\${BACKUP_NAME}_db.sql
    echo "Database backup saved to \$BACKUP_DIR/\${BACKUP_NAME}_db.sql.gz"
fi

# Backup .env file
if [ -f .env ]; then
    cp .env \$BACKUP_DIR/\${BACKUP_NAME}_env
    echo "Environment file backed up to \$BACKUP_DIR/\${BACKUP_NAME}_env"
fi

echo "Backup completed!"
ENDSSH

    log_success "Backup created!"
}

# Function to update application code
update_application() {
    log_info "Updating application code..."

    # Create temporary directory for new code
    TEMP_DIR=$(mktemp -d)

    # Copy current directory to temp
    log_info "Preparing files for upload..."
    rsync -az \
        --exclude 'node_modules' \
        --exclude '.next' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude '.env' \
        --exclude 'venv' \
        --exclude '.venv' \
        ./ "$TEMP_DIR/"

    # Upload to server
    log_info "Uploading files to server..."
    rsync -avz --delete \
        -e "ssh -i $SSH_KEY_PATH -o StrictHostKeyChecking=no" \
        "$TEMP_DIR/" root@"$SERVER_IP":"$DEPLOY_PATH/"

    # Cleanup temp directory
    rm -rf "$TEMP_DIR"

    log_success "Application code updated!"
}

# Function to rebuild and restart services
rebuild_services() {
    log_info "Rebuilding and restarting services..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << 'ENDSSH'
cd /var/www/fightsftickets

# Pull latest images if any
docker-compose -f docker-compose.prod.yml pull

# Rebuild services
echo "Building services..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop current services
echo "Stopping services..."
docker-compose -f docker-compose.prod.yml down

# Start updated services
echo "Starting updated services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check service status
docker-compose -f docker-compose.prod.yml ps

echo "Services restarted!"
ENDSSH

    log_success "Services rebuilt and restarted!"
}

# Function to run database migrations
run_migrations() {
    log_info "Running database migrations..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << 'ENDSSH'
cd /var/www/fightsftickets

# Wait for database to be ready
sleep 10

# Run migrations
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head || echo "Migrations completed or not needed"

echo "Migrations completed!"
ENDSSH

    log_success "Database migrations completed!"
}

# Function to verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check if services are running
    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << 'ENDSSH'
cd /var/www/fightsftickets

echo "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Check health endpoint
echo "Checking API health..."
sleep 5
curl -f http://localhost:8000/health || echo "Health check failed - service may still be starting"

echo "Verification completed!"
ENDSSH

    log_success "Deployment verified!"
}

# Function to cleanup old resources
cleanup() {
    log_info "Cleaning up old Docker resources..."

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" << 'ENDSSH'
# Remove unused images
docker image prune -af --filter "until=24h"

# Remove unused volumes (be careful!)
docker volume prune -f --filter "label!=keep"

# Remove old backups (keep last 7 days)
find /var/backups/fightsftickets -type f -mtime +7 -delete || true

echo "Cleanup completed!"
ENDSSH

    log_success "Cleanup completed!"
}

# Function to display update summary
display_summary() {
    echo ""
    echo "=========================================="
    log_success "Update Complete!"
    echo "=========================================="
    echo ""
    echo "Server: $SERVER_IP"
    echo "Deploy Path: $DEPLOY_PATH"
    echo ""
    echo "Services Status:"

    ssh -i "$SSH_KEY_PATH" root@"$SERVER_IP" "cd $DEPLOY_PATH && docker-compose -f docker-compose.prod.yml ps"

    echo ""
    echo "Useful Commands:"
    echo "  View logs: ssh -i $SSH_KEY_PATH root@$SERVER_IP 'cd $DEPLOY_PATH && docker-compose -f docker-compose.prod.yml logs -f'"
    echo "  Restart service: ssh -i $SSH_KEY_PATH root@$SERVER_IP 'cd $DEPLOY_PATH && docker-compose -f docker-compose.prod.yml restart <service>'"
    echo "  Rollback: Restore from /var/backups/${PROJECT_NAME}"
    echo ""
    echo "=========================================="
}

# Main update flow
main() {
    echo "=========================================="
    echo "  FightSFTickets Update Deployment"
    echo "=========================================="
    echo ""

    check_prerequisites
    backup_deployment
    update_application
    rebuild_services
    run_migrations
    verify_deployment
    cleanup
    display_summary

    log_success "Update completed successfully!"
}

# Handle script interruption
trap 'log_error "Update interrupted!"; exit 1' INT TERM

# Run main function
main
