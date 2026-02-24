"""
City Configuration Routes

Provides access to city configuration data and eligibility.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Query

from ..services.city_registry import get_city_registry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]])
def list_cities(eligible: bool = Query(True, description="Filter for eligible cities only")):
    """
    List available cities.

    By default, returns only cities eligible for the current strategy (Tier 1).
    """
    registry = get_city_registry()
    return registry.get_all_cities(eligible_only=eligible)
