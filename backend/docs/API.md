# Fight City Tickets API Documentation

## Overview

Database-first parking ticket appeal system for San Francisco and other cities. Handles citation validation, AI-assisted appeal letter writing (UPL-compliant), checkout, and webhook processing.

**Base URL:** `https://api.fightcitytickets.com`  
**Local URL:** `http://localhost:8000`

---

## Architecture

- **Database-First**: All data persisted in PostgreSQL before payment
- **Minimal Metadata**: Only IDs stored in Stripe metadata
- **Idempotent Webhooks**: Safe retry handling for production
- **UPL Compliance**: Never provides legal advice or recommends evidence

---

## Endpoints

### Root

#### GET `/`

Returns basic API information and links to documentation.

**Response:**
```json
{
  "name": "Fight City Tickets API",
  "version": "1.0.0",
  "documentation": "/docs",
  "health_check": "/health"
}
```

---

### Health

#### GET `/health`

Basic health check endpoint.

---

### Status

#### GET `/status`

Comprehensive status endpoint with database, Stripe, Lob, and AI services status.

**Response:**
```json
{
  "status": "operational",
  "timestamp": "2026-02-22T00:00:00Z",
  "services": {
    "database": {"status": "connected", "type": "PostgreSQL"},
    "stripe": {"status": "configured", "mode": "test"},
    "lob": {"status": "configured", "mode": "test"},
    "ai_services": {"deepseek": "configured"}
  },
  "architecture": {
    "approach": "database-first",
    "metadata_strategy": "ids-only"
  }
}
```

---

### Tickets

#### POST `/tickets/validate`

Validate a parking citation number and check against selected city.

**Request:**
```json
{
  "citation_number": "12345678",
  "license_plate": "ABC1234",
  "city_id": "san_francisco"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `citation_number` | string | Yes | The citation/ticket number |
| `license_plate` | string | No | Vehicle license plate |
| `violation_date` | string | No | Violation date (ISO format) |
| `city_id` | string | No | City ID for mismatch detection |

**Response:**
```json
{
  "is_valid": true,
  "citation_number": "12345678",
  "agency": "San Francisco Municipal Transportation Agency",
  "deadline_date": "2026-03-15",
  "days_remaining": 21,
  "is_past_deadline": false,
  "is_urgent": false,
  "city_id": "san_francisco",
  "appeal_deadline_days": 21
}
```

---

### Statement Refinement

#### POST `/statement/refine`

AI-assisted appeal letter refinement (UPL-compliant).

**Request:**
```json
{
  "statement": "I was parked legally. The sign was obscured by a tree branch.",
  "city": "san_francisco"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `statement` | string | Yes | User's original statement |
| `city` | string | Yes | City code |

**Response:**
```json
{
  "refined_statement": "Dear Sir or Madam,\n\nI am writing to formally contest...",
  "word_count": 245,
  "compliance_verified": true
}
```

---

### Checkout

#### POST `/checkout/create-session`

Create a Stripe checkout session using database-first approach.

**Request:**
```json
{
  "citation_id": "550e8400-e29b-41d4-a716-446655440000",
  "service_type": "standard",
  "success_url": "https://fightcitytickets.com/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "https://fightcitytickets.com/cancel"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `citation_id` | string | Yes | UUID of the citation |
| `service_type` | string | Yes | "standard" or "certified" |
| `success_url` | string | Yes | Redirect on success |
| `cancel_url` | string | Yes | Redirect on cancel |

**Response:**
```json
{
  "session_id": "cs_test_abc123",
  "checkout_url": "https://checkout.stripe.com/c/abcd1234",
  "clerical_id": "ND-A1B2-C3D4"
}
```

---

### Appeals

#### POST `/api/appeals`

Submit a parking ticket appeal.

**Request:**
```json
{
  "citation_id": "550e8400-e29b-41d4-a716-446655440000",
  "statement": "I am writing to contest the citation...",
  "payment_session_id": "cs_test_abc123",
  "service_type": "standard"
}
```

#### GET `/api/appeals`

List appeals with optional filtering.

#### GET `/api/appeals/{appeal_id}`

Get a specific appeal by ID.

---

### Webhooks

#### POST `/webhook/stripe`

Handle Stripe webhook events. Uses idempotent processing.

**Headers:**
- `Stripe-Signature`: Stripe webhook signature

**Event Types:**
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

---

### Places

#### GET `/places/search`

Search for supported cities/locations.

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search query |

**Response:**
```json
[
  {"id": "san_francisco", "name": "San Francisco", "state": "CA"}
]
```

---

### Admin

#### GET `/admin/appeals`

List all appeals (admin only).

#### GET `/admin/analytics`

Get analytics and reporting (admin only).

---

### Telemetry

#### POST `/telemetry/ocr`

Submit OCR performance telemetry (opt-in).

**Request:**
```json
{
  "image_hash": "abc123def456",
  "extracted_text": "12345678",
  "confidence": 0.95,
  "processing_time_ms": 250
}
```

---

## Compliance

### UPL (Unlicensed Practice of Law)

This API is designed to be UPL-compliant:
- Never provides legal advice
- Never recommends evidence to use
- Helps users articulate their own appeals
- Provides templates and suggestions only

### Data Privacy

- All data stored in PostgreSQL before payment
- Only IDs stored in Stripe metadata
- PII encrypted at rest
- GDPR compliant data handling

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at: `/docs/openapi.json`

You can visualize it at: https://swagger.io/tools/swagger-ui/
