# End-to-End Integration Testing Guide

## Overview

This document describes the comprehensive E2E integration test suite for FightSFTickets.com. These tests verify that **all four critical endpoints work together**:

1. **Stripe Webhook Integration** - Tests that Stripe actually sends webhooks and they're processed correctly
2. **Lob Mail Sending** - Tests that Lob actually prints and sends physical mail
3. **Hetzner Droplet Suspension** - Tests that droplets can be suspended on failure
4. **Main Python Service** - Tests that all services communicate with the FastAPI backend

**If all four endpoints work, you've got a real product! 🚀**

## Prerequisites

### Required API Keys

Set these environment variables before running tests:

```bash
# Stripe (required for webhook tests)
export STRIPE_SECRET_KEY="sk_live_..." or "sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Lob (required for mail tests)
export LOB_API_KEY="live_..." or "test_..."

# Hetzner (required for droplet tests)
export HETZNER_API_TOKEN="your-hetzner-token"
export HETZNER_DROPLET_NAME="your-droplet-name"

# Database (required for all tests)
export DATABASE_URL="postgresql+psycopg://user:pass@host:5432/dbname"
```

### Python Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
```

## Running Tests

### Run All E2E Tests

```bash
cd backend
python run_e2e_tests.py
```

### Run Specific Test Suites

```bash
# Stripe webhook tests only
python run_e2e_tests.py --stripe-only

# Lob mail tests only
python run_e2e_tests.py --lob-only

# Hetzner droplet tests only
python run_e2e_tests.py --hetzner-only

# Full integration flow test
python run_e2e_tests.py --full-flow
```

### Using pytest Directly

```bash
# Run all integration tests
pytest backend/tests/test_e2e_integration.py -v -m integration

# Run specific test class
pytest backend/tests/test_e2e_integration.py::TestStripeWebhookIntegration -v

# Run with verbose output
pytest backend/tests/test_e2e_integration.py -v -s
```

## Test Structure

### 1. Stripe Webhook Integration (`TestStripeWebhookIntegration`)

Tests that Stripe webhooks are:
- ✅ Properly signed and verified
- ✅ Received by the webhook endpoint
- ✅ Processed correctly by the FastAPI service

**Key Tests:**
- `test_stripe_webhook_signature_verification` - Verifies signature validation
- `test_stripe_webhook_endpoint_receives_events` - Tests webhook endpoint

### 2. Lob Mail Integration (`TestLobMailIntegration`)

Tests that Lob API:
- ✅ Can connect to Lob service
- ✅ Actually sends physical mail (in live mode)
- ✅ Returns tracking numbers and letter IDs

**Key Tests:**
- `test_lob_mail_service_sends_letter` - Sends real mail via Lob
- `test_lob_mail_service_connectivity` - Verifies connectivity

### 3. Hetzner Droplet Integration (`TestHetznerDropletIntegration`)

Tests that Hetzner Cloud:
- ✅ Can retrieve droplet information
- ✅ Can suspend droplets on failure
- ✅ Handles errors gracefully

**Key Tests:**
- `test_hetzner_service_can_get_droplet` - Retrieves droplet info
- `test_hetzner_suspension_on_failure` - Suspends droplet (test env only!)

### 4. Full Integration Flow (`TestFullIntegrationFlow`)

Tests the complete end-to-end flow:
1. Create intake and payment in database
2. Simulate Stripe webhook
3. Verify Lob mail is sent
4. Verify database is updated
5. Verify all services communicate

**Key Tests:**
- `test_full_payment_to_mail_flow` - Complete flow test
- `test_all_services_communicate_with_main_service` - Service communication

## Test Results Interpretation

### ✅ All Tests Pass

If all tests pass, you have:
- ✅ Stripe webhook integration working
- ✅ Lob mail sending working
- ✅ Hetzner droplet management working
- ✅ All services communicating with FastAPI

**You've got a real product! 🚀**

### ⚠️ Some Tests Skipped

Tests may be skipped if:
- API keys are not configured (expected in dev)
- Services are in test mode (Lob test mode)
- Droplet not found (Hetzner)

This is **normal** - tests will skip gracefully.

### ❌ Tests Fail

If tests fail:
1. Check API keys are set correctly
2. Verify services are accessible
3. Check network connectivity
4. Review error messages in test output

## Integration Points

### Stripe → FastAPI

```
Stripe Webhook → /api/webhook/stripe → Webhook Handler → Database Update → Lob Mail
```

### Lob → FastAPI

```
FastAPI → Lob Service → Lob API → Physical Mail Sent → Tracking Number → Database
```

### Hetzner → FastAPI

```
Failure Detected → Hetzner Service → Hetzner API → Droplet Suspended
```

### Database → All Services

```
All Services → Database Service → PostgreSQL → Data Persisted
```

## Failure Handling

### Automatic Droplet Suspension

If a critical failure occurs (e.g., Lob mail fails in production), the system will:
1. Log the error
2. Attempt to suspend the Hetzner droplet
3. Alert via logs

**Note:** Suspension only happens in production mode and only for critical failures.

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run E2E tests
        env:
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
          STRIPE_WEBHOOK_SECRET: ${{ secrets.STRIPE_WEBHOOK_SECRET }}
          LOB_API_KEY: ${{ secrets.LOB_API_KEY }}
          HETZNER_API_TOKEN: ${{ secrets.HETZNER_API_TOKEN }}
        run: |
          cd backend
          python run_e2e_tests.py
```

## Troubleshooting

### "Stripe webhook secret not configured"

Set `STRIPE_WEBHOOK_SECRET` environment variable.

### "Lob API key not configured"

Set `LOB_API_KEY` environment variable.

### "Hetzner API token not configured"

Set `HETZNER_API_TOKEN` environment variable.

### "Droplet not found"

Set `HETZNER_DROPLET_NAME` to match your actual droplet name.

### Tests timeout

Check network connectivity and API service status.

## Best Practices

1. **Run tests before deployment** - Always run E2E tests before deploying to production
2. **Use test mode for development** - Use Stripe test mode and Lob test mode during development
3. **Monitor test results** - Track which integrations are working
4. **Fix failures immediately** - Don't deploy if critical tests fail
5. **Document changes** - Update tests when adding new integrations

## Summary

These E2E integration tests verify that your entire system works end-to-end:

- ✅ **Stripe** sends webhooks → FastAPI processes them
- ✅ **Lob** sends mail → FastAPI tracks it
- ✅ **Hetzner** suspends droplets → FastAPI triggers it
- ✅ **Database** stores everything → All services use it

**If all four endpoints work, you've got a real product! 🚀**

