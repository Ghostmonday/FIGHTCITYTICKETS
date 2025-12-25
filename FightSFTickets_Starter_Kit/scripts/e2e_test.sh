#!/bin/bash

# Comprehensive E2E Test Script for FightSFTickets
# This script tests the complete user flow and API endpoints

set -e  # Exit on error

echo "========================================="
echo "FIGHTSFTICKETS COMPREHENSIVE E2E TEST"
echo "========================================="
echo "Timestamp: $(date)"
echo ""

# Configuration
BASE_URL="https://fightsftickets.com"
API_URL="${BASE_URL}"
TEST_CITATION="912345678"
TEST_DATE="2024-01-15"
TEST_LICENSE="ABC123"
TEST_EMAIL="test@example.com"
TEST_NAME="Test User"
TEST_ADDRESS="123 Test St"
TEST_CITY="San Francisco"
TEST_STATE="CA"
TEST_ZIP="94102"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_info() {
    echo -e "ℹ $1"
}

test_endpoint() {
    local url=$1
    local expected_code=${2:-200}
    local description=$3
    local method=${4:-GET}
    local data=${5:-""}

    echo -n "Testing $description... "

    if [ -z "$data" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi

    if [ "$response" -eq "$expected_code" ]; then
        log_success "HTTP $response"
        return 0
    else
        log_error "Expected HTTP $expected_code, got HTTP $response"
        return 1
    fi
}

test_json_endpoint() {
    local url=$1
    local description=$2
    local method=${3:-GET}
    local data=${4:-""}

    echo -n "Testing $description... "

    if [ -z "$data" ]; then
        response=$(curl -s -X "$method" "$url")
    else
        response=$(curl -s -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi

    if echo "$response" | jq . >/dev/null 2>&1; then
        log_success "Valid JSON response"
        return 0
    else
        log_error "Invalid JSON response"
        echo "Response: $response"
        return 1
    fi
}

# Check if required tools are installed
echo "Checking dependencies..."
command -v curl >/dev/null 2>&1 || { log_error "curl is required but not installed"; exit 1; }
command -v jq >/dev/null 2>&1 || { log_warning "jq is not installed, JSON tests will be limited"; }

echo ""
echo "Phase 1: Basic Connectivity Tests"
echo "---------------------------------"

# Test 1: Home page accessibility
test_endpoint "$BASE_URL/" 200 "Home page accessibility"

# Test 2: API health endpoint
test_endpoint "$API_URL/health" 200 "API health endpoint"

# Test 3: API documentation
test_endpoint "$API_URL/docs" 200 "API documentation (Swagger UI)"

# Test 4: Terms of Service page
test_endpoint "$BASE_URL/terms" 200 "Terms of Service page"

# Test 5: Privacy Policy page
test_endpoint "$BASE_URL/privacy" 200 "Privacy Policy page"

echo ""
echo "Phase 2: Appeal Flow Pages"
echo "--------------------------"

# Test 6: Appeal entry page
test_endpoint "$BASE_URL/appeal" 200 "Appeal entry page"

# Test 7: Appeal entry with standard type
test_endpoint "$BASE_URL/appeal?type=standard" 200 "Appeal entry (standard)"

# Test 8: Appeal entry with certified type
test_endpoint "$BASE_URL/appeal?type=certified" 200 "Appeal entry (certified)"

# Test 9: Camera/photo upload page
test_endpoint "$BASE_URL/appeal/camera" 200 "Photo upload page"

# Test 10: Review page
test_endpoint "$BASE_URL/appeal/review" 200 "Letter review page"

# Test 11: Signature page
test_endpoint "$BASE_URL/appeal/signature" 200 "Signature page"

# Test 12: Checkout page
test_endpoint "$BASE_URL/appeal/checkout" 200 "Checkout page"

# Test 13: Checkout with standard type
test_endpoint "$BASE_URL/appeal/checkout?type=standard" 200 "Checkout (standard)"

# Test 14: Checkout with certified type
test_endpoint "$BASE_URL/appeal/checkout?type=certified" 200 "Checkout (certified)"

# Test 15: Success page
test_endpoint "$BASE_URL/success" 200 "Success page"

# Test 16: Admin page
test_endpoint "$BASE_URL/admin" 200 "Admin dashboard"

echo ""
echo "Phase 3: API Functional Tests"
echo "-----------------------------"

# Test 17: Citation validation API (should work with test keys)
VALIDATION_DATA="{\"citation_number\":\"$TEST_CITATION\",\"violation_date\":\"$TEST_DATE\",\"license_plate\":\"$TEST_LICENSE\"}"
test_json_endpoint "$API_URL/tickets/validate" "Citation validation API" "POST" "$VALIDATION_DATA"

# Test 18: Test checkout endpoint (should return error with test keys)
CHECKOUT_DATA="{
  \"citation_number\": \"$TEST_CITATION\",
  \"appeal_type\": \"standard\",
  \"user_name\": \"$TEST_NAME\",
  \"user_address_line1\": \"$TEST_ADDRESS\",
  \"user_city\": \"$TEST_CITY\",
  \"user_state\": \"$TEST_STATE\",
  \"user_zip\": \"$TEST_ZIP\",
  \"violation_date\": \"$TEST_DATE\",
  \"vehicle_info\": \"Test Vehicle\",
  \"appeal_reason\": \"Test appeal reason for testing purposes.\",
  \"draft_text\": \"This is a test appeal letter for automated testing. Please ignore this submission.\",
  \"license_plate\": \"$TEST_LICENSE\"
}"
test_endpoint "$API_URL/checkout/create-session" "400" "Checkout API (expecting 400 with test keys)" "POST" "$CHECKOUT_DATA"

# Test 19: Test statement refinement API (should work or fail gracefully)
REFINEMENT_DATA="{\"original_statement\":\"The parking meter was broken.\",\"citation_number\":\"$TEST_CITATION\"}"
test_endpoint "$API_URL/api/statement/refine" "Check statement refinement API" "POST" "$REFINEMENT_DATA"

echo ""
echo "Phase 4: Navigation Flow Tests"
echo "------------------------------"

# Test 20: Check that all internal links are valid
echo "Checking internal link consistency..."

# Check home page links
echo -n "Checking home page → appeal page link... "
if curl -s "$BASE_URL/" | grep -q "href=\"/appeal\""; then
    log_success "Found"
else
    log_error "Missing appeal link on home page"
fi

# Check appeal page continues to camera
echo -n "Checking appeal → camera page flow... "
if curl -s "$BASE_URL/appeal" | grep -q "href=\"/appeal/camera\"" || curl -s "$BASE_URL/appeal" | grep -q "action.*camera"; then
    log_success "Found camera navigation"
else
    log_warning "Camera navigation not found in HTML (may be JavaScript-driven)"
fi

echo ""
echo "Phase 5: Content Validation"
echo "---------------------------"

# Test 21: Check for UPL disclaimers
echo -n "Checking for UPL disclaimer on home page... "
if curl -s "$BASE_URL/" | grep -qi "not a law firm\|does not provide legal advice"; then
    log_success "Found UPL disclaimer"
else
    log_error "Missing UPL disclaimer"
fi

# Test 22: Check for required legal pages
echo -n "Checking Terms of Service content... "
if curl -s "$BASE_URL/terms" | grep -qi "terms of service\|agreement"; then
    log_success "Terms page has content"
else
    log_warning "Terms page may be empty"
fi

# Test 23: Check pricing information
echo -n "Checking pricing on home page... "
if curl -s "$BASE_URL/" | grep -qi "\$9\|\$19\|standard.*certified"; then
    log_success "Pricing information found"
else
    log_error "Missing pricing information"
fi

echo ""
echo "Phase 6: Error Handling Tests"
echo "-----------------------------"

# Test 24: Test 404 page
test_endpoint "$BASE_URL/nonexistent-page" 404 "Non-existent page (should return 404)"

# Test 25: Test invalid API endpoint
test_endpoint "$API_URL/invalid-endpoint" 404 "Invalid API endpoint"

echo ""
echo "Phase 7: Performance & Security"
echo "-------------------------------"

# Test 26: Check HTTPS is enforced
echo -n "Checking HTTPS redirect... "
http_response=$(curl -s -o /dev/null -w "%{http_code}" http://fightsftickets.com/)
if [ "$http_response" -eq 301 ] || [ "$http_response" -eq 308 ]; then
    log_success "HTTP redirects to HTTPS"
else
    log_warning "No HTTP to HTTPS redirect (response: $http_response)"
fi

# Test 27: Check security headers
echo -n "Checking security headers... "
headers=$(curl -s -I "$BASE_URL/" | grep -i "strict-transport-security\|x-frame-options\|x-content-type-options")
if [ -n "$headers" ]; then
    log_success "Security headers present"
else
    log_warning "Missing security headers"
fi

echo ""
echo "========================================="
echo "TEST SUMMARY"
echo "========================================="
echo "Tests completed: $(date)"
echo ""
echo "Next steps for manual testing:"
echo "1. Complete the appeal form with test citation: $TEST_CITATION"
echo "2. Test photo upload functionality"
echo "3. Test AI refinement feature"
echo "4. Test Stripe checkout flow (requires valid test keys)"
echo "5. Verify database persistence"
echo ""
echo "For production readiness:"
echo "1. Replace all dummy API keys with real test keys"
echo "2. Configure Stripe webhook endpoint"
echo "3. Set up monitoring and alerts"
echo "4. Test full payment flow with Stripe test mode"
echo "========================================="
