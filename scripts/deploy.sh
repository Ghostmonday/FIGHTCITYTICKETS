#!/bin/bash
# =============================================
# FIGHTCITYTICKETS - Deployment Script
# =============================================
# One-command deployment with health verification
# =============================================

set -e

# Configuration
DEPLOY_DIR="${DEPLOY_DIR:-/var/www/fightcitytickets}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-60}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prereqs() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker not found!"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        error "Docker Compose not found!"
        exit 1
    fi
    
    # Check if docker is running
    if ! docker ps &> /dev/null; then
        error "Docker daemon not running!"
        exit 1
    fi
    
    log "Prerequisites OK"
}

# Pre-deployment backup
pre_backup() {
    if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
        log "Creating pre-deployment backup..."
        bash "$(dirname "$0")/backup_db.sh"
    fi
}

# Pull latest code
pull_code() {
    log "Pulling latest code..."
    cd "$DEPLOY_DIR"
    
    if [ -d .git ]; then
        git pull origin main
    else
        warn "Not a git repository - skipping pull"
    fi
}

# Build and start services
deploy() {
    log "Building and starting services..."
    cd "$DEPLOY_DIR"
    
    docker compose down --remove-orphans
    docker compose up -d --build
    
    log "Services started"
}

# Verify health
verify_health() {
    log "Verifying health (timeout: ${HEALTH_TIMEOUT}s)..."
    
    API_URL="${API_URL:-http://localhost:8000}"
    FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
    
    ELAPSED=0
    while [ $ELAPSED -lt $HEALTH_TIMEOUT ]; do
        # Check API health
        if curl -sf "${API_URL}/health" > /dev/null 2>&1; then
            log "API health: OK"
            
            # Check database connectivity
            if curl -sf "${API_URL}/health/ready" > /dev/null 2>&1; then
                log "Database: OK"
                log "Deployment SUCCESSFUL"
                return 0
            fi
        fi
        
        sleep 2
        ELAPSED=$((ELAPSED + 2))
        echo -n "."
    done
    
    echo ""
    error "Health check timed out!"
    error "Check logs with: docker compose logs"
    return 1
}

# Show status
show_status() {
    log "Service status:"
    cd "$DEPLOY_DIR"
    docker compose ps
}

# Main execution
main() {
    echo "============================================="
    echo "  FIGHTCITYTICKETS DEPLOYMENT"
    echo "============================================="
    
    check_prereqs
    pre_backup
    pull_code
    deploy
    
    if verify_health; then
        show_status
        echo ""
        log "Deployment complete!"
        log "Frontend: ${FRONTEND_URL:-http://localhost:3000}"
        log "API: ${API_URL:-http://localhost:8000}"
        log "Docs: ${API_URL:-http://localhost:8000}/docs"
    else
        error "Deployment may have issues - check logs"
        exit 1
    fi
}

main "$@"
