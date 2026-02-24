"""
City Information Route

Provides information about supported cities and eligibility.
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.city_registry import get_city_registry, CityRegistry

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter placeholder - will be injected by app.py
limiter = Limiter(key_func=get_remote_address)

# Cache registry instance
_city_registry: CityRegistry = None


def get_registry() -> CityRegistry:
    """Get or initialize the global city registry instance."""
    global _city_registry
    if _city_registry is None:
        logger.info("Initializing CityRegistry for cities route")
        _city_registry = get_city_registry()
    return _city_registry


@router.get("/")
@limiter.limit("60/minute")
async def get_cities(
    request: Request,
    eligible: bool = Query(
        False,
        description="Filter only eligible cities (no POA required, no corporate block)",
    ),
) -> List[Dict[str, Any]]:
    """
    Get list of supported cities.

    Optional 'eligible' parameter filters for cities where:
    - No Power of Attorney is required
    - Corporate/Fleet appeals are not blocked
    - Wet-ink signatures are not required
    """
    try:
        registry = get_registry()
        cities = registry.get_all_cities(eligible_only=eligible)
        return cities
    except Exception as e:
        logger.error(f"Error retrieving cities: {e}")
        raise
