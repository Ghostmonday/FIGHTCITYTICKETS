
import asyncio
import time
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app

# Mock the database service to simulate latency
class MockSession:
    def __init__(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def query(self, *args):
        # Sleep to simulate blocking DB call
        time.sleep(1.0)
        return self
    def scalar(self):
        return 0
    def filter(self, *args):
        return self
    def close(self):
        pass

class MockDBService:
    def health_check(self):
        return True
    def get_session(self):
        return MockSession()

@pytest.mark.asyncio
async def test_metrics_performance():
    """
    Test that the metrics endpoint does not block the event loop
    while performing slow database operations.
    """
    # Patch the get_db_service in the module where it is defined,
    # so that when health.py imports it, it gets the mock.
    with patch("src.services.database.get_db_service", return_value=MockDBService()) as mock_get_db:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:

            async def fast_task():
                start = time.time()
                await asyncio.sleep(0.1)
                end = time.time()
                return end - start

            # Fire off the fast task FIRST
            task2 = asyncio.create_task(fast_task())

            # Allow fast task to start and hit the sleep
            await asyncio.sleep(0.01)

            # Fire off the slow request
            task1 = asyncio.create_task(client.get("/health/metrics"))

            # Wait for both
            duration_fast = await task2
            response = await task1

            # Since the DB calls are now in a thread, the event loop should NOT be blocked.
            # fast_task (which sleeps 0.1s) should finish quickly, even while metrics is running.
            # It shouldn't wait for the 3.0s of metrics DB calls.
            # So duration should be approx 0.1s + overhead, definitely < 1.0s

            assert duration_fast < 1.0, f"Expected non-blocking behavior (duration < 1.0s), but task took {duration_fast}s"
            assert response.status_code == 200
