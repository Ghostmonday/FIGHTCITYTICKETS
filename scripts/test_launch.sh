#!/bin/bash
# Pre-Launch Testing Script for FIGHT CITY TICKETS
# This script tests the application locally before going live

set -e  # Exit on error

echo "🧪 FIGHT CITY TICKETS - PRE-LAUNCH TEST"
echo "========================================"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Docker is running
echo -e "\n${YELLOW}Test 1:${NC} Checking Docker..."
if sudo docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Test 2: Configuration is valid
echo -e "\n${YELLOW}Test 2:${NC} Validating docker-compose.yml..."
if sudo docker compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Configuration is valid${NC}"
else
    echo -e "${RED}❌ Configuration has errors${NC}"
    exit 1
fi

# Test 3: Build images (without starting)
echo -e "\n${YELLOW}Test 3:${NC} Building Docker images..."
sudo docker compose build --no-cache 2>&1 | tail -5

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Images built successfully${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Test 4: Check .env critical variables
echo -e "\n${YELLOW}Test 4:${NC} Checking critical .env variables..."
source .env 2>/dev/null || true

check_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo -e "${RED}❌ $var_name is not set${NC}"
        return 1
    elif [[ "$var_value" == *"PLACEHOLDER"* ]] || [[ "$var_value" == *"xxx"* ]]; then
        echo -e "${YELLOW}⚠️  $var_name is a placeholder${NC}"
        return 2
    else
        echo -e "${GREEN}✅ $var_name is set${NC}"
        return 0
    fi
}

CRITICAL_VARS=0
PLACEHOLDER_VARS=0

check_var "STRIPE_SECRET_KEY" || ((CRITICAL_VARS+=$?))
check_var "STRIPE_PRICE_CERTIFIED" || ((CRITICAL_VARS+=$?))
check_var "DATABASE_URL" || ((CRITICAL_VARS+=$?))

check_var "LOB_API_KEY"; RET=$?
if [ $RET -eq 2 ]; then ((PLACEHOLDER_VARS++)); fi

check_var "STRIPE_PUBLISHABLE_KEY"; RET=$?
if [ $RET -eq 2 ]; then ((PLACEHOLDER_VARS++)); fi

# Summary
echo -e "\n========================================"
echo -e "${YELLOW}PRE-LAUNCH SUMMARY${NC}"
echo -e "========================================"

if [ $CRITICAL_VARS -eq 0 ] && [ $PLACEHOLDER_VARS -le 2 ]; then
    echo -e "${GREEN}✅ READY FOR TEST LAUNCH${NC}"
    echo -e "\nTo start the application:"
    echo -e "  ${YELLOW}sudo docker compose up -d${NC}"
    echo -e "\nTo view logs:"
    echo -e "  ${YELLOW}sudo docker compose logs -f${NC}"
    echo -e "\nTo access:"
    echo -e "  Frontend: ${YELLOW}http://localhost${NC}"
    echo -e "  API: ${YELLOW}http://localhost/api/health${NC}"
    exit 0
else
    echo -e "${RED}❌ NOT READY - Missing critical configuration${NC}"
    echo -e "\nPlease fix the issues above before launching."
    exit 1
fi
