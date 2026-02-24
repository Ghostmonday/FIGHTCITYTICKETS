
import asyncio
import time
from unittest.mock import MagicMock, patch
import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from src.services.database import DatabaseService

# Mock the database service to simulate latency
class MockSession:
    def __init__(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def query(self, *args):
        time.sleep(1.0) # Simulate blocking DB call
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
    Verify that the metrics endpoint does not block the event loop
    even when database operations are slow.
    """
    # Patch get_db_service in src.routes.health because it's imported at top level there.
    with patch("src.routes.health.get_db_service", return_value=MockDBService()) as mock_get_db:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

            async def fast_task():
                start = time.time()
                await asyncio.sleep(0.2)
                return time.time() - start

            # Fire off the fast task first
            task2 = asyncio.create_task(fast_task())

            await asyncio.sleep(0.01)

            task1 = asyncio.create_task(client.get("/health/metrics"))

            duration_fast = await task2

            print(f"Fast task duration: {duration_fast:.4f}s")

            assert duration_fast < 0.5, f"Metrics endpoint blocked the event loop! Task took {duration_fast}s"

            response = await task1
            assert response.status_code == 200
            data = response.json()
            assert "metrics" in data
            assert "total_intakes" in data["metrics"]
