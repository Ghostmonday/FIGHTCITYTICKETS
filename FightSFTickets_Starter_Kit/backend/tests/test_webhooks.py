"""
Tests for webhook endpoints.
"""

import json
import pytest
from fastapi import status


def test_webhook_missing_signature(client):
    """Test webhook endpoint without signature header."""
    payload = {"type": "checkout.session.completed", "data": {}}
    
    response = client.post(
        "/api/webhook/stripe",
        json=payload,
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "signature" in response.json()["detail"].lower()


def test_webhook_invalid_signature(client):
    """Test webhook endpoint with invalid signature."""
    payload = {"type": "checkout.session.completed", "data": {}}
    
    response = client.post(
        "/api/webhook/stripe",
        json=payload,
        headers={"stripe-signature": "invalid_signature"},
    )
    
    # Should return 400 for invalid signature
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_webhook_invalid_json(client):
    """Test webhook endpoint with invalid JSON."""
    response = client.post(
        "/api/webhook/stripe",
        content="invalid json",
        headers={"Content-Type": "application/json", "stripe-signature": "test"},
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_webhook_health(client):
    """Test webhook health check endpoint."""
    response = client.get("/api/webhook/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

