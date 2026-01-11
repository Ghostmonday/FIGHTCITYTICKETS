#!/bin/bash
# FightCityTickets - Security Hardening Deployment Script
# Run this on your local machine to deploy security configurations
#
# Usage: ./scripts/deploy-security.sh
#

set -e

echo "🛡️  Deploying Security Hardening to FightCityTickets"
echo "======================================================"
echo ""

# Configuration
SERVER_IP="146.190.141.126"
SSH_USER="admin"
SSH_KEY="/c/Users/Amirp/.ssh/do_key_ed25519"
PROJECT_DIR="$(pwd)"
BACKUP_DIR="/tmp/nginx-backup-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
log_info "Checking prerequisites..."

if [ ! -f "$SSH_KEY" ]; then
    log_error "SSH key not found: $SSH_KEY"
    exit 1
fi

if [ ! -f "nginx/nginx.conf" ]; then
    log_error "nginx.conf not found in nginx/ directory"
    exit 1
fi

if [ ! -f "nginx/conf.d/fightcitytickets.conf" ]; then
    log_error "fightcitytickets.conf not found in nginx/conf.d/ directory"
    exit 1
fi

log_info "All prerequisites met ✓"
echo ""

# Create backup directory on server
log_info "Creating backup directory on server..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "mkdir -p $BACKUP_DIR" 2>/dev/null || true

# Backup existing configs
log_info "Backing up existing nginx configurations..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo cp /etc/nginx/nginx.conf $BACKUP_DIR/ 2>/dev/null || true"
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo cp /etc/nginx/conf.d/fightcitytickets.conf $BACKUP_DIR/ 2>/dev/null || true"
log_info "Backups saved to: $BACKUP_DIR"
echo ""

# Upload new configurations
log_info "Uploading new nginx configurations..."
scp -o StrictHostKeyChecking=no -i "$SSH_KEY" nginx/nginx.conf "$SSH_USER@$SERVER_IP:/tmp/nginx.conf" 2>/dev/null
scp -o StrictHostKeyChecking=no -i "$SSH_KEY" nginx/conf.d/fightcitytickets.conf "$SSH_USER@$SERVER_IP:/tmp/fightcitytickets.conf" 2>/dev/null
log_info "Files uploaded ✓"
echo ""

# Apply new configurations
log_info "Applying new nginx configurations..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo mv /tmp/nginx.conf /etc/nginx/nginx.conf" 2>/dev/null
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo mv /tmp/fightcitytickets.conf /etc/nginx/conf.d/fightcitytickets.conf" 2>/dev/null
echo ""

# Test nginx configuration
log_info "Testing nginx configuration..."
if ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo nginx -t" 2>/dev/null; then
    log_info "Nginx configuration test passed ✓"
else
    log_error "Nginx configuration test failed!"
    log_info "Restoring backup..."
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo cp $BACKUP_DIR/nginx.conf /etc/nginx/ && sudo cp $BACKUP_DIR/fightcitytickets.conf /etc/nginx/conf.d/" 2>/dev/null
    exit 1
fi
echo ""

# Reload nginx
log_info "Reloading nginx..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo systemctl reload nginx" 2>/dev/null
log_info "Nginx reloaded ✓"
echo ""

# Verify nginx is running
log_info "Verifying nginx status..."
if ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "sudo systemctl is-active nginx" 2>/dev/null | grep -q "active"; then
    log_info "Nginx is running ✓"
else
    log_warn "Nginx may not be running. Check manually: sudo systemctl status nginx"
fi
echo ""

# Test website accessibility
log_info "Testing website accessibility..."
if curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP" | grep -q "200"; then
    log_info "Website is accessible ✓"
else
    log_warn "Website may not be accessible. Check manually."
fi
echo ""

# Summary
echo "======================================================"
echo "✅  Security Hardening Deployed Successfully!"
echo "======================================================"
echo ""
echo "Security Features Applied:"
echo "  • Hidden nginx version (server_tokens off)"
echo "  • Rate limiting (10 req/s per IP)"
echo "  • Connection limits (10 per IP)"
echo "  • Security headers (HSTS, CSP, X-Frame, etc.)"
echo "  • SSL/TLS configuration (TLS 1.2/1.3)"
echo "  • Exploit pattern blocking (SQLi, traversal, shells)"
echo "  • Gzip compression"
echo "  • Upstream keepalive connections"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Quick Commands:"
echo "  View nginx status:  ssh $SSH_USER@$SERVER_IP 'sudo systemctl status nginx'"
echo "  Check logs:         ssh $SSH_USER@$SERVER_IP 'sudo tail -f /var/log/nginx/error.log'"
echo "  Rollback:           ssh $SSH_USER@$SERVER_IP 'sudo cp $BACKUP_DIR/nginx.conf /etc/nginx/'"
echo ""
