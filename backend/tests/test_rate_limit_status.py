import sys
import os
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Mock DB service BEFORE importing status router
mock_db = MagicMock()
mock_intake = MagicMock()
mock_intake.id = 1
mock_intake.citation_number = "123"
mock_payment = MagicMock()
mock_payment.status.value = "paid"
mock_payment.is_fulfilled = False
mock_payment.amount_total = 5000
mock_payment.appeal_type.value = "standard"
mock_payment.paid_at = None
mock_payment.fulfilled_at = None
mock_payment.lob_tracking_id = None

mock_db.get_intake_by_email_and_citation.return_value = mock_intake
mock_db.get_latest_payment.return_value = mock_payment

import src.routes.status
src.routes.status.get_db_service = MagicMock(return_value=mock_db)

from src.routes.status import router as status_router, limiter

# Create app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(status_router, prefix="/status")

client = TestClient(app)

def test_rate_limit():
    print("Attempting to hit /status/lookup 10 times...")
    rate_limited = False
    for i in range(10):
        # We need to simulate distinct requests, but TestClient reuses session by default?
        # Actually TestClient is just a requests Session.
        # But for rate limiting by IP, TestClient requests usually come from "testclient" or "127.0.0.1".
        # Since we use the same IP, the rate limit counter should increment.

        response = client.post(
            "/status/lookup",
            json={"email": "test@example.com", "citation_number": "123"}
        )
        print(f"Request {i+1}: Status {response.status_code}")
        if response.status_code == 429:
            rate_limited = True
            break

    if not rate_limited:
        print("❌ FAILED: Was not rate limited")
        sys.exit(1)
    else:
        print("✅ SUCCESS: Rate limiting works!")

if __name__ == "__main__":
    test_rate_limit()
