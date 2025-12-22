"""
Tests for rate limiting functionality.
"""

import pytest
from fastapi import status


def test_rate_limiting_health_endpoint(client):
    """Test that rate limiting works on health endpoint."""
    # Make many requests quickly
    responses = []
    for _ in range(35):  # More than the 30/minute limit
        response = client.get("/health")
        responses.append(response.status_code)
    
    # At least one should be rate limited (429)
    assert status.HTTP_429_TOO_MANY_REQUESTS in responses


def test_rate_limiting_checkout_endpoint(client):
    """Test rate limiting on checkout endpoint."""
    payload = {
        "citation_number": "912345678",
        "appeal_type": "standard",
        "user_name": "Test User",
        "user_address_line1": "123 Test St",
        "user_city": "San Francisco",
        "user_state": "CA",
        "user_zip": "94102",
        "violation_date": "2024-01-15",
        "vehicle_info": "Test Vehicle",
        "appeal_reason": "Test reason",
    }
    
    responses = []
    for _ in range(15):  # More than the 10/minute limit for payment
        response = client.post("/checkout/create-session", json=payload)
        responses.append(response.status_code)
    
    # At least one should be rate limited
    assert status.HTTP_429_TOO_MANY_REQUESTS in responses

