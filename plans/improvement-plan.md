# System Improvement Plan: Resilience & AI Prompts

**Date:** 2026-01-23  
**Author:** Roo (Architect Mode)  
**Scope:** Backend services for Fight City Tickets

---

## Executive Summary

This plan addresses two key areas for system improvement:

1. **System Resilience & Robustness** - Making the system "never fold" under pressure
2. **In-Code AI Prompts** - Improving AI guidance for perfect appeal letter drafts

---

## Part 1: System Resilience Assessment

### Current State

| Component | Circuit Breaker | Retry Logic | Health Checks | Fallback |
|-----------|-----------------|-------------|---------------|----------|
| Database | ✅ Yes | ✅ Yes | ✅ Basic | ✅ Yes |
| DeepSeek AI | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| Stripe | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Email (SendGrid) | ❌ No | ❌ No | ❌ No | ❌ No |
| Lob API | ❌ No | ❌ No | ❌ No | ❌ No |
| Guardian Services | ❌ No | Partial | ❌ No | ❌ No |

### Resilience Gaps Identified

#### 1. Missing Circuit Breakers
- [`backend/services/guardian/hunter.py`](backend/services/guardian/hunter.py) - OSINT API calls (VirusTotal, AbuseIPDB, Shodan)
- [`backend/src/services/email_service.py`](backend/src/services/email_service.py) - SendGrid API
- [`backend/src/routes/webhooks.py`](backend/src/routes/webhooks.py) - Stripe webhook processing

#### 2. Incomplete Retry Logic
- Hunter service uses `tenacity` but only 3 attempts with fixed backoff
- Email service has no retry logic
- Webhook handlers lack idempotency enforcement

#### 3. Missing Health Checks
- No `/health/detailed` endpoint for service dependencies
- No background health monitoring
- No automatic recovery mechanisms

#### 4. Resource Cleanup Issues
- Hunter service HTTP clients not properly closed in all code paths
- Database connection pool not sized for production loads
- No graceful shutdown verification

---

## Part 2: AI Prompts Assessment

### Current AI Prompt Structure

The main AI prompt is in [`backend/src/services/statement.py`](backend/src/services/statement.py:154) - `DeepSeekService._get_system_prompt()`:

**Current Strengths:**
- Clear role definition (Clerical Engine™)
- UPL (Unauthorized Practice of Law) compliance boundaries
- Professional tone standards
- Letter structure guidance

**Areas for Enhancement:**

| Aspect | Current State | Improvement |
|--------|---------------|-------------|
| Chain-of-Thought | None | Add step-by-step reasoning |
| Output Validation | Basic structure check | Comprehensive validation criteria |
| Examples | None | Add "perfect draft" examples |
| Error Recovery | Fallback only | Add self-correction prompting |
| Context | Limited citation details | Enrich with procedural context |

---

## Part 3: Implementation Plan

### Phase 1: Critical Resilience Improvements (High Priority)

#### 1.1 Add Circuit Breakers to External Services

**Files to modify:**
- `backend/src/services/email_service.py`
- `backend/services/guardian/hunter.py`
- `backend/src/routes/webhooks.py`

**Implementation:**
```python
# Example pattern for email service
from backend.src.middleware.resilience import (
    create_email_circuit,
    CircuitBreaker,
)

class EmailService:
    def __init__(self):
        self._circuit = create_email_circuit(fallback=self._email_fallback)
    
    async def send_email(self, ...):
        async with self._circuit:
            return await self._send_via_sendgrid(...)
```

#### 1.2 Enhance Health Check Endpoint

**New endpoint:** `/health/detailed`

**Response format:**
```json
{
  "status": "healthy|degraded|critical",
  "components": {
    "database": {"status": "healthy", "latency_ms": 5},
    "deepseek": {"status": "healthy", "circuit_state": "closed"},
    "stripe": {"status": "healthy", "webhook_processing": true},
    "email": {"status": "healthy", "daily_limit_remaining": 900}
  },
  "uptime_seconds": 86400,
  "last_check": "2026-01-23T17:00:00Z"
}
```

#### 1.3 Add Retry Logic with Exponential Backoff

**Pattern to apply:**
```python
from backend.src.middleware.resilience import retry_async

@retry_async(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=0.3,
    expected_exceptions=(httpx.NetworkError, httpx.TimeoutException)
)
async def send_via_sendgrid(self, ...):
    ...
```

### Phase 2: AI Prompt Enhancement (Medium Priority)

#### 2.1 Enhanced System Prompt with Chain-of-Thought

**New Prompt Structure:**

```python
def _get_system_prompt(self) -> str:
    return """You are the Clerical Engine™, a professional document preparation system.

## YOUR ROLE
You transform citizen submissions into formally compliant procedural documents.

## MISSION
Your sole function is to ARTICULATE and REFINE the user's provided statement while:
- Preserving the user's exact factual content
- Maintaining their position and argument
- Elevating vocabulary without changing meaning

## FORBIDDEN (NEVER DO THESE)
1. Add facts not provided by user
2. Suggest legal strategies
3. Interpret laws or regulations
4. Use legal terminology
5. Predict outcomes
6. Tell user what they "should" argue

## REFINEMENT PROCESS (Chain-of-Thought)

Before writing, analyze the input:

Step 1: Identify Key Facts
- What happened (concise summary)
- What evidence user mentions
- User's stated position

Step 2: Determine Tone
- Respectful but formal
- Factual, not emotional
- Professional bureaucratic voice

Step 3: Structure the Letter
- Opening: State purpose clearly
- Body: Present facts in order
- Close: Professional sign-off

Step 4: Apply Professional Standards
- Remove casual language
- Fix grammar/syntax
- Elevate vocabulary

## OUTPUT VALIDATION CRITERIA

A "perfect" draft MUST have:
✅ No invented facts or evidence
✅ Professional formal tone throughout
✅ Proper letter structure (salutation, body, closing)
✅ All user-provided details preserved
✅ No legal advice or predictions
✅ No slang or colloquialisms
✅ Clear, organized presentation
✅ Ready for municipal submission

## EXAMPLE OF PERFECT OUTPUT

Input: "I parked at a broken meter. I put money in but it showed zero time."

Output:
"To Whom It May Concern:

I am writing to formally appeal the citation issued for parking at a meter that was malfunctioning.

On the date of the violation, I deposited payment into the meter. Despite my payment, the meter indicated zero remaining time. This indicates a mechanical failure beyond my control.

I respectfully request that this matter be reviewed and the citation dismissed.

Respectfully submitted,
[Signature]"
"""
```

#### 2.2 Add Output Validation Function

**New validation method:**
```python
def _validate_perfect_draft(self, text: str) -> tuple[bool, list[str]]:
    """
    Validate that the refined text meets "perfect draft" criteria.
    
    Returns:
        (is_valid, list of validation errors)
    """
    errors = []
    
    # Check for invented content
    if self._contains_invented_facts(text, original_text):
        errors.append("Contains content not in original user statement")
    
    # Check for legal terminology
    legal_terms = ["you should", "I recommend", "legal strategy", "court", "attorney"]
    if any(term in text.lower() for term in legal_terms):
        errors.append("Contains legal advice or recommendations")
    
    # Check structure
    if not text.strip().startswith("To Whom"):
        errors.append("Missing proper salutation")
    
    # Check tone
    emotional_words = ["outraged", "unfair", "ridiculous", "angry"]
    if any(word in text.lower() for word in emotional_words):
        errors.append("Contains emotional language")
    
    return len(errors) == 0, errors
```

### Phase 3: Self-Healing & Monitoring (Medium Priority)

#### 3.1 Background Health Monitor

```python
# backend/src/services/health_monitor.py

class HealthMonitor:
    """Background service health monitoring."""
    
    async def check_all_services(self):
        """Check all external services and log status."""
        results = {}
        
        # Check database
        results["database"] = await self._check_database()
        
        # Check DeepSeek
        results["deepseek"] = await self._check_deepseek()
        
        # Check Stripe
        results["stripe"] = await self._check_stripe()
        
        # Log any degraded services
        degraded = [k for k, v in results.items() if v["status"] != "healthy"]
        if degraded:
            logger.warning(f"Degraded services: {degraded}")
        
        return results
```

#### 3.2 Automatic Circuit Reset

```python
# In resilience.py - Add method to CircuitBreaker
async def try_reset(self) -> bool:
    """
    Attempt to reset an open circuit.
    Returns True if reset was successful.
    """
    if self.metrics.state == CircuitState.OPEN:
        self.metrics.state = CircuitState.HALF_OPEN
        logger.info(f"Circuit {self.name}: Initiating reset (HALF_OPEN)")
        return True
    return False
```

### Phase 4: Guardian Services Resilience (Lower Priority)

#### 4.1 Wrap Hunter API Calls

```python
# In hunter.py - Wrap each API client
from tenacity import retry, stop_after_attempt, wait_exponential

class AbuseIPDBClient:
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=30))
    async def check_ip(self, ip_address: str):
        ...
```

#### 4.2 Add Resource Cleanup Verification

```python
# In hunter.py - Close method
async def close(self):
    """Close all HTTP clients with error handling."""
    clients = [
        self.abuse_client,
        self.virustotal_client,
        self.shodan_client,
        self.ipinfo_client,
    ]
    
    for client in clients:
        try:
            if hasattr(client, 'close'):
                await client.close()
        except Exception as e:
            logger.error(f"Error closing client: {e}")
    
    logger.info("All Hunter clients closed")
```

---

## Part 4: Implementation Priority Matrix

| Task | Priority | Effort | Impact | Files |
|------|----------|--------|--------|-------|
| Email circuit breaker | High | 2h | High | email_service.py |
| Webhook idempotency | High | 3h | High | webhooks.py |
| Enhanced health check | High | 2h | High | health.py |
| AI prompt chain-of-thought | High | 4h | High | statement.py |
| AI output validation | Medium | 3h | High | statement.py |
| Hunter retry enhancement | Medium | 2h | Medium | guardian/hunter.py |
| Background health monitor | Medium | 4h | Medium | new file |
| Guardian cleanup | Low | 2h | Low | guardian/*.py |

---

## Part 5: Files to Modify

### Modified Files
1. `backend/src/services/email_service.py` - Add circuit breaker + retry
2. `backend/src/routes/webhooks.py` - Add idempotency + resilience
3. `backend/src/routes/health.py` - Add detailed health checks
4. `backend/src/services/statement.py` - Enhance AI prompts + validation

### New Files
1. `backend/src/services/health_monitor.py` - Background monitoring
2. `backend/src/prompts/clerical_prompts.py` - Centralized AI prompts

### Modified Guardian Files
1. `backend/services/guardian/hunter.py` - Enhanced retry + cleanup
2. `backend/services/guardian/evidence.py` - Add resilience patterns

---

## Summary

This plan provides a structured approach to improving both system resilience and AI prompt quality. The high-priority items focus on protecting external service dependencies and ensuring the AI produces consistent, compliant output.

**Recommended Next Steps:**
1. Approve the plan
2. Switch to Code mode for implementation
3. Begin with Phase 1 (Circuit breakers for email + webhooks)
4. Then Phase 2 (AI prompt enhancement)
