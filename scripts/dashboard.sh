#!/bin/bash
# =============================================
# FIGHTCITYTICKETS - System Dashboard
# =============================================
# Quick overview of system status and resources
# =============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║          FIGHTCITYTICKETS - SYSTEM DASHBOARD             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors for service status
OK() { echo -e "${GREEN}✓${NC}"; }
FAIL() { echo -e "${RED}✗${NC}"; }
WARN() { echo -e "${YELLOW}!${NC}"; }

# 1. Docker Services Status
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🐳 DOCKER SERVICES${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd /home/amir/Projects/FightSFTickets 2>/dev/null || cd "$(dirname "$0")/.."

if docker compose ps &>/dev/null; then
    docker compose ps | tail -n +2 | while read line; do
        if echo "$line" | grep -q "Up"; then
            echo -e "  $(OK) $line"
        elif echo "$line" | grep -q "Up (unhealthy)"; then
            echo -e "  $(WARN) $line"
        else
            echo -e "  $(FAIL) $line"
        fi
    done
else
    echo -e "  $(WARN) Docker Compose not accessible"
fi

echo ""

# 2. Health Endpoints
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🌐 HEALTH ENDPOINTS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

if curl -sf "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "  $(OK) API Health: ${API_URL}/health"
else
    echo -e "  $(FAIL) API Health: ${API_URL}/health"
fi

if curl -sf "${API_URL}/health/ready" > /dev/null 2>&1; then
    echo -e "  $(OK) DB Ready: ${API_URL}/health/ready"
else
    echo -e "  $(FAIL) DB Ready: ${API_URL}/health/ready"
fi

if curl -sf "${FRONTEND_URL}" > /dev/null 2>&1; then
    echo -e "  $(OK) Frontend: ${FRONTEND_URL}"
else
    echo -e "  $(FAIL) Frontend: ${FRONTEND_URL}"
fi

echo ""

# 3. Resource Usage
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}💾 RESOURCE USAGE${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "  Docker containers:"
docker stats --no-stream --format "    {{.Name}}: {{.CPUPerc}} CPU, {{.MemUsage}}" 2>/dev/null | head -5 || echo "    Unable to fetch stats"

echo ""
echo "  Disk usage (project):"
du -sh /home/amir/Projects/FightSFTickets 2>/dev/null | while read size path; do
    echo "    Project: ${size}"
done

echo ""

# 4. Recent Logs
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📋 RECENT LOGS (last 5 lines)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker compose logs --tail=5 api 2>/dev/null | sed 's/^/    /' || echo "    No logs available"

echo ""

# 5. Quick Actions
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}⚡ QUICK ACTIONS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  ./scripts/backup_db.sh     - Create database backup"
echo "  ./scripts/deploy.sh        - Deploy application"
echo "  ./scripts/monitor.sh        - Continuous monitoring"
echo "  docker compose logs -f     - Follow logs"
echo "  docker compose restart      - Restart services"
echo ""

echo "═══════════════════════════════════════════════════════════"
