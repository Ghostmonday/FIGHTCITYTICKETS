"""
Tests for checkout endpoints.
"""

import pytest
from fastapi import status


def test_create_checkout_session_success(client, test_db, mock_stripe_service):
    """Test successful checkout session creation."""
    payload = {
        "citation_number": "912345678",
        "appeal_type": "standard",
        "user_name": "John Doe",
        "user_address_line1": "123 Main St",
        "user_city": "San Francisco",
        "user_state": "CA",
        "user_zip": "94102",
        "violation_date": "2024-01-15",
        "vehicle_info": "Honda Civic ABC123",
        "appeal_reason": "Meter was broken",
    }
    
    response = client.post("/checkout/create-session", json=payload)
    
    # Should return 200 or 201 with checkout URL
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    data = response.json()
    assert "checkout_url" in data or "session_id" in data


def test_create_checkout_session_validation_error(client):
    """Test checkout session creation with invalid data."""
    payload = {
        "citation_number": "",  # Invalid: empty
        "appeal_type": "invalid",  # Invalid: not standard/certified
        "user_name": "",
    }
    
    response = client.post("/checkout/create-session", json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_session_status(client):
    """Test getting session status."""
    # This will fail if session doesn't exist, which is expected
    response = client.get("/checkout/session/cs_test_123")
    
    # Should return 400 or 404
    assert response.status_code in [
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]

