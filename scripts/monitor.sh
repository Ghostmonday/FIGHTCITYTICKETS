#!/bin/bash
# =============================================
# FIGHTCITYTICKETS - Health Monitor
# =============================================
# Continuous monitoring with alert on failure
# =============================================

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"  # Optional: Discord/Slack webhook URL

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${RED}[FAIL]${NC} $1"; }

send_alert() {
    local msg="$1"
    echo -e "${RED}[ALERT]${NC} $msg"
    
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --json "{\"text\":\"🚨 FIGHTCITYTICKETS ALERT: $msg\"}" \
            "$ALERT_WEBHOOK" || true
    fi
}

check_api_health() {
    if curl -sf "${API_URL}/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_api_ready() {
    if curl -sf "${API_URL}/health/ready" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_frontend() {
    if curl -sf "${FRONTEND_URL}" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_status() {
    echo ""
    echo "============================================="
    echo "  FIGHTCITYTICKETS STATUS"
    echo "  $(date)"
    echo "============================================="
    
    # API Health
    if check_api_health; then
        log_info "API Health: OK"
    else
        log_error "API Health: FAIL"
        send_alert "API health check failed"
    fi
    
    # Database (via readiness check)
    if check_api_ready; then
        log_info "Database: OK"
    else
        log_error "Database: UNREACHABLE"
        send_alert "Database connection failed"
    fi
    
    # Frontend
    if check_frontend; then
        log_info "Frontend: OK"
    else
        log_error "Frontend: FAIL"
        send_alert "Frontend unavailable"
    fi
    
    # Docker services
    echo ""
    echo "Docker Services:"
    docker compose ps 2>/dev/null | tail -n +2 | while read line; do
        if echo "$line" | grep -q "Up"; then
            echo -e "  ${GREEN}$line${NC}"
        else
            echo -e "  ${RED}$line${NC}"
        fi
    done
}

# Run single check (for cron)
if [ "$1" = "--once" ]; then
    check_status
    exit 0
fi

# Continuous monitoring
echo "============================================="
echo "  FIGHTCITYTICKETS MONITOR"
echo "  Checking every ${CHECK_INTERVAL}s"
echo "  Press Ctrl+C to stop"
echo "============================================="

while true; do
    FAILED=0
    
    if ! check_api_health; then
        log_error "API health check failed"
        FAILED=1
    fi
    
    if ! check_api_ready; then
        log_error "Database check failed"
        FAILED=1
    fi
    
    if ! check_frontend; then
        log_error "Frontend check failed"
        FAILED=1
    fi
    
    if [ $FAILED -eq 1 ]; then
        send_alert "One or more services unhealthy"
        log_warn "Waiting ${CHECK_INTERVAL}s before next check..."
    else
        echo -n "."
    fi
    
    sleep $CHECK_INTERVAL
done
