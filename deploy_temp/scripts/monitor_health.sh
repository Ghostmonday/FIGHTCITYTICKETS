#!/bin/bash
# Simple Health Monitoring Script for FightCityTickets
# Run every 5 minutes via cron: */5 * * * * /path/to/monitor_health.sh

set -e

# Configuration
API_URL="https://fightcitytickets.com/api/health"
ALERT_EMAIL="${ALERT_EMAIL:-support@fightcitytickets.com}"  # Set via environment or edit here
LOG_FILE="/var/log/fightcitytickets_health.log"
MAX_FAILURES=3
FAILURE_COUNT_FILE="/tmp/fightcitytickets_health_failures"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check health endpoint
check_health() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL" || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# Get failure count
get_failure_count() {
    if [ -f "$FAILURE_COUNT_FILE" ]; then
        cat "$FAILURE_COUNT_FILE"
    else
        echo "0"
    fi
}

# Increment failure count
increment_failure() {
    COUNT=$(get_failure_count)
    NEW_COUNT=$((COUNT + 1))
    echo "$NEW_COUNT" > "$FAILURE_COUNT_FILE"
    echo "$NEW_COUNT"
}

# Reset failure count
reset_failure() {
    rm -f "$FAILURE_COUNT_FILE"
}

# Send alert
send_alert() {
    SUBJECT="🚨 FightCityTickets Health Check Failed"
    MESSAGE="The health check for $API_URL has failed $1 consecutive times.\n\nTime: $(date)\nURL: $API_URL\n\nPlease investigate immediately."
    
    # Try to send email (requires mailutils or similar)
    if command -v mail &> /dev/null; then
        echo -e "$MESSAGE" | mail -s "$SUBJECT" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    
    # Also log to syslog
    logger -t fightcitytickets_health "$SUBJECT"
    
    log "ALERT: $SUBJECT"
}

# Main check
if check_health; then
    FAILURE_COUNT=$(get_failure_count)
    if [ "$FAILURE_COUNT" -gt 0 ]; then
        log "✅ Health check passed (recovered from $FAILURE_COUNT failures)"
        reset_failure
    else
        log "✅ Health check passed"
    fi
else
    FAILURE_COUNT=$(increment_failure)
    log "❌ Health check failed (consecutive failures: $FAILURE_COUNT)"
    
    if [ "$FAILURE_COUNT" -ge "$MAX_FAILURES" ]; then
        send_alert "$FAILURE_COUNT"
    fi
fi

