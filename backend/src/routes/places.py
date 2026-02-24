"""
Google Places API Proxy Route

Proxies Google Places API requests through the backend to protect API keys.
"""

import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Google Places API key from environment
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")


@router.get("/autocomplete")
@limiter.limit("30/minute")
async def google_places_autocomplete(
    request: Request,
    input: str = Query(..., description="Address input to autocomplete"),
    session_token: Optional[str] = Query(None, description="Session token for billing"),
):
    """
    Proxy Google Places Autocomplete API requests.
    
    This endpoint protects the Google API key by proxying requests through the backend.
    """
    if not GOOGLE_PLACES_API_KEY:
        logger.error("GOOGLE_PLACES_API_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Address autocomplete service not configured",
        )
    
    if not input or len(input) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input must be at least 3 characters",
        )
    
    try:
        client = request.app.state.client
        params = {
            "input": input,
            "key": GOOGLE_PLACES_API_KEY,
            "components": "country:us",  # US addresses only
            "types": "address",  # Only addresses, not businesses
        }

        if session_token:
            params["sessiontoken"] = session_token

        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/autocomplete/json",
            params=params,
        )

        if response.status_code != 200:
            logger.error(f"Google Places API returned {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Address autocomplete service unavailable",
            )

        data = response.json()

        # Remove API key from response if present
        if "error_message" in data:
            logger.warning(f"Google Places API error: {data.get('error_message')}")

        return data
            
    except httpx.TimeoutException:
        logger.error("Google Places API timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Address autocomplete service timeout",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error proxying Google Places API request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process address autocomplete request",
        )


@router.get("/details")
@limiter.limit("30/minute")
async def google_places_details(
    request: Request,
    place_id: str = Query(..., description="Place ID from autocomplete result"),
    session_token: Optional[str] = Query(None, description="Session token for billing"),
):
    """
    Proxy Google Places Details API requests.

    This endpoint retrieves detailed address components for a selected place.
    """
    if not GOOGLE_PLACES_API_KEY:
        logger.error("GOOGLE_PLACES_API_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Address service not configured",
        )

    if not place_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Place ID is required",
        )

    try:
        client = request.app.state.client
        params = {
            "place_id": place_id,
            "key": GOOGLE_PLACES_API_KEY,
            "fields": "address_components,formatted_address",
        }

        if session_token:
            params["sessiontoken"] = session_token

        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params=params,
        )

        if response.status_code != 200:
            logger.error(f"Google Places Details API returned {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Address details service unavailable",
            )

        data = response.json()

        if data.get("status") != "OK":
            logger.warning(f"Google Places Details API error: {data.get('status')}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Address lookup failed: {data.get('status')}",
            )

        return data

    except httpx.TimeoutException:
        logger.error("Google Places Details API timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Address details service timeout",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error proxying Google Places Details API request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process address details request",
        )
