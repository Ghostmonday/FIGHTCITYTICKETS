"""
Cities Configuration Routes

Provides access to available city configurations and eligibility status.
"""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Query

from ..services.city_registry import get_city_registry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
def list_cities(eligible: bool = Query(True, description="Filter by eligibility (e.g. Tier 1 strategy)")) -> List[Dict[str, Any]]:
    """
    List available cities.

    Args:
        eligible: If True, returns only cities eligible for the current strategy.
                 If False, returns all configured cities.
    """
    try:
        registry = get_city_registry()
        return registry.get_all_cities(eligible_only=eligible)
    except Exception as e:
        logger.error(f"Failed to list cities: {e}")
        return []
