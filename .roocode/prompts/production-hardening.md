# Roo Code Prompt: Production Hardening - Fallbacks & Rate Limits

## Objective
Strengthen FightSFTickets for production reliability by adding fallbacks, rate limits, and resilience patterns across the entire stack.

## Critical Requirements

### 1. System Fallbacks
Implement graceful degradation for all external service dependencies:

**DeepSeek/AI Fallbacks** (`backend/src/services/statement.py`):
- If DeepSeek API fails → return template-based fallback response
- If API timeout → return "appeal_writing_needed" status
- Log failure to telemetry for monitoring

**Stripe Fallbacks** (`backend/src/services/stripe_service.py`):
- If webhook processing fails → store event in failed_webhooks table
- Implement idempotent retry with exponential backoff (3 attempts)
- Send admin alert after 3 failures

**Email Fallbacks** (`backend/src/services/email_service.py`):
- If email fails → queue to database for deferred sending
- Implement dead letter queue for repeated failures
- Provide "check dashboard" fallback message to user

**Database Fallbacks** (`backend/src/services/database.py`):
- If connection fails → return 503 with retry-after header
- Implement circuit breaker pattern (5 failures = 5 min cooldown)
- Cache recent lookups for read operations during outage

**City Config Fallbacks** (`backend/src/services/city_registry.py`):
- If city config missing → fall back to SF defaults
- Cache city configs in memory with 1-hour TTL
- Log config errors but don't crash

### 2. Rate Limits (missing from current implementation)
Add rate limiting to currently unprotected endpoints:

**Webhook Rate Limits** (`backend/src/routes/webhooks.py`):
- Max 100 webhooks/minute per IP
- Max 10 retries per webhook event
- Signature validation on all Stripe webhooks

**Email Rate Limits** (`backend/src/services/email_service.py`):
- Max 10 emails/minute per user
- Max 50 emails/hour per IP
- Rate limit headers in response

**AI API Rate Limits** (`backend/src/services/statement.py`):
- Max 5 refinement requests/minute per user
- Max 1000 tokens/day per IP (configurable)
- Queue requests during rate limit, respond with 202

**Upload Rate Limits**:
- Max 5MB per upload
- Max 10 uploads/hour per IP
- Validate file types before processing

### 3. Resilience Patterns

**Circuit Breaker** for:
- Stripe API calls
- Email service calls
- DeepSeek API calls
- Database connections

**Retry Logic** with exponential backoff:
- Max 3 retries
- Base delay: 100ms, multiplier: 2x
- Jitter: ±25%

**Health Check Enhancements** (`backend/src/routes/health.py`):
- Check all external dependencies
- Return detailed status: healthy/degraded/outage
- Include dependency versions and response times

**Graceful Degradation**:
- If non-critical service fails → continue with reduced functionality
- Show user-friendly messages (not stack traces)
- Log detailed errors to telemetry, return generic to user

## Implementation Guidelines

### Execution Order
1. Add circuit breaker base class
2. Implement retry decorator
3. Add fallback responses to each service
4. Add rate limits to unprotected endpoints
5. Update health check to report dependency status
6. Add tests for all new patterns

### Completion Criteria
- All tests pass: `pytest -q` and `npm test`
- Health endpoint reports all dependencies correctly
- Rate limit headers appear on protected endpoints
- Fallback responses tested with simulated failures
- No uncaught exceptions in logs during failure scenarios

### Constraints
- Do NOT modify: `frontend/package.json` dependencies, Dockerfiles
- Keep backward compatibility with existing API contracts
- Use existing logging/telemetry infrastructure
- Don't break the appeal flow: camera → review → checkout → success

## Success Metrics
After implementation:
```
✓ Stripe webhook processing retries on failure
✓ Email queued on failure, sent on retry
✓ AI fallback returns template when API fails
✓ Rate limit headers on all protected endpoints
✓ Health check shows: healthy, degraded, or outage
✓ Circuit breaker trips after 5 failures, recovers after 5 min
```

### Brand Consistency Update
Update all instances of "FIGHT SF TICKETS" → "Fight City Tickets" across:
- Backend docstrings and comments
- Frontend page titles and metadata
- Email templates
- Any hardcoded strings

**Execute after all other tasks are complete.**

## Output Requirements
When finished, provide:
1. Summary of changes made
2. Any files that need environment variables
3. Migration steps (if database changes)
4. Commands to verify implementation
