## 2025-01-26 - Blocking Synchronous Stripe Calls
**Vulnerability:** Synchronous `stripe` library calls were being made directly in an `async` function (`_with_retry_async`), blocking the asyncio event loop and causing potential Denial of Service (DoS) under load.
**Learning:** The `stripe` library (v14.x) is synchronous. Even if wrapped in an `async` function, it must be run in an executor (`loop.run_in_executor`) to avoid blocking.
**Prevention:** Always verify if a library is truly async or just synchronous. Use `run_in_executor` for CPU-bound or blocking I/O operations in async endpoints.

## 2025-01-26 - IDOR in Appeal Endpoints
**Vulnerability:** `backend/src/routes/appeals.py` exposes endpoints (`GET /appeals/{id}`, `PUT /appeals/{id}`) that use sequential integer IDs without authentication or authorization checks.
**Learning:** This allows enumeration and unauthorized access to user data (PII). The application seems designed without user accounts, relying on obscure URLs or session state, but integer IDs are easily guessable.
**Prevention:** Use UUIDs for public-facing resource identifiers or implement token-based access control (e.g., return a secret token on creation that must be provided for subsequent access).
