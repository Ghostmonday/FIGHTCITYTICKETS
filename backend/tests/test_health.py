from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_metrics():
    # Metrics endpoint might need DB, but if DB is not available it returns empty metrics without crashing
    r = client.get("/health/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "metrics" in data
    assert "requests_total" in data["metrics"]
    assert "uptime_seconds" in data["metrics"]
