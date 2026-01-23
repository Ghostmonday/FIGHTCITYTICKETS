#!/bin/bash
# Connection diagnostic script

LOG_FILE="/home/evan/Documents/Projects/FightSFTickets/.cursor/debug.log"
SERVER_ENDPOINT="http://127.0.0.1:7242/ingest/24d298b8-9a2b-48c9-8de9-4066eb332ccc"

log_debug() {
    local hypothesis_id=$1
    local message=$2
    local data=$3
    local json=$(cat <<EOF
{"sessionId":"debug-session","runId":"connection-test","hypothesisId":"$hypothesis_id","location":"scripts/diagnostics/test_connection.sh","message":"$message","data":$data,"timestamp":$(date +%s000)}
EOF
)
    echo "$json" >> "$LOG_FILE"
    curl -s -X POST "$SERVER_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$json" > /dev/null 2>&1 || true
}

# Test 1: Check if ports are listening
log_debug "A" "Checking port 80 listener" '{"port":80}'
PORT80=$(sudo lsof -i :80 2>/dev/null | wc -l)
log_debug "A" "Port 80 listeners" '{"count":'$PORT80'}'

log_debug "B" "Checking port 3000 listener" '{"port":3000}'
PORT3000=$(sudo lsof -i :3000 2>/dev/null | wc -l)
log_debug "B" "Port 3000 listeners" '{"count":'$PORT3000'}'

# Test 2: Try IPv4 connection
log_debug "C" "Testing IPv4 connection to port 80" '{"ip":"127.0.0.1","port":80}'
RESULT80=$(curl -4 -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80 2>&1 || echo "FAILED")
log_debug "C" "IPv4 port 80 result" '{"result":"'$RESULT80'"}'

log_debug "C" "Testing IPv4 connection to port 3000" '{"ip":"127.0.0.1","port":3000}'
RESULT3000=$(curl -4 -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:3000 2>&1 || echo "FAILED")
log_debug "C" "IPv4 port 3000 result" '{"result":"'$RESULT3000'"}'

# Test 3: Check Docker containers
log_debug "D" "Checking Docker container status" '{}'
cd /home/evan/Documents/Projects/FightSFTickets
CONTAINERS=$(sudo docker compose ps --format json 2>/dev/null | jq -r '.Name' 2>/dev/null || echo "ERROR")
log_debug "D" "Docker containers" '{"containers":"'$CONTAINERS'"}'

# Test 4: Check nginx error logs
log_debug "E" "Checking nginx error logs" '{}'
NGINX_ERRORS=$(sudo docker compose exec -T nginx cat /var/log/nginx/error.log 2>&1 | tail -5 | wc -l)
log_debug "E" "Nginx error log lines" '{"count":'$NGINX_ERRORS'}'

# Test 5: Test from inside nginx container
log_debug "A" "Testing web connectivity from nginx" '{}'
NGINX_TO_WEB=$(sudo docker compose exec -T nginx wget -qO- --timeout=5 http://web:3000 2>&1 | head -c 100 | wc -c)
log_debug "A" "Nginx to web result" '{"bytes":'$NGINX_TO_WEB'}'

echo "Diagnostics complete. Check $LOG_FILE for details."
