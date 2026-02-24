
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Set environment variables before importing app
os.environ["ADMIN_SECRET"] = "test-secret"
os.environ["SECRET_KEY"] = "test-jwt-secret"

from src.app import app
from src.routes import admin

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db_service():
    with patch("src.routes.admin.get_db_service") as mock:
        mock_instance = MagicMock()
        mock_instance.health_check.return_value = True
        mock.return_value = mock_instance
        yield mock_instance

def test_admin_login_success(client):
    response = client.post("/admin/login", json={"secret": "test-secret"})
    assert response.status_code == 200
    assert "admin_session" in response.cookies
    assert response.json()["message"] == "Login successful"

def test_admin_login_failure(client):
    response = client.post("/admin/login", json={"secret": "wrong-secret"})
    assert response.status_code == 401

def test_admin_me_endpoint_with_cookie(client, mock_db_service):
    # First login to get cookie
    login_response = client.post("/admin/login", json={"secret": "test-secret"})
    assert login_response.status_code == 200
    cookie = login_response.cookies["admin_session"]

    # Then access /me
    response = client.get("/admin/me", cookies={"admin_session": cookie})
    assert response.status_code == 200
    assert response.json()["authenticated"] is True

def test_admin_me_endpoint_without_cookie(client):
    response = client.get("/admin/me")
    # Should fail if no header and no cookie
    assert response.status_code == 401 or response.status_code == 503

def test_admin_logout(client):
    # Login
    client.post("/admin/login", json={"secret": "test-secret"})

    # Logout
    response = client.post("/admin/logout")
    assert response.status_code == 200
    assert "admin_session" not in response.cookies or response.cookies["admin_session"] == ""

def test_protected_route_with_cookie(client, mock_db_service):
    # Login
    login_res = client.post("/admin/login", json={"secret": "test-secret"})
    cookie = login_res.cookies["admin_session"]

    # Access protected route
    response = client.get("/admin/stats", cookies={"admin_session": cookie})
    assert response.status_code == 200

def test_protected_route_with_header_fallback(client, mock_db_service):
    # Access with header (legacy)
    response = client.get("/admin/stats", headers={"X-Admin-Secret": "test-secret"})
    assert response.status_code == 200
