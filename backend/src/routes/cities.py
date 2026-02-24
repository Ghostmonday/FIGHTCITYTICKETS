"""City routes."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query, Request

from ..services.city_registry import get_city_registry

router = APIRouter()

# Rate limiter - will be set from app.py after app initialization
limiter: Optional[object] = None


@router.get("", response_model=List[Dict[str, Any]])
async def list_cities(
    request: Request,
    eligible: bool = Query(True, description="Filter by eligibility"),
):
    """
    List available cities.

    By default, returns only eligible cities (Tier 1 strategy).
    Set eligible=False to see all configured cities.
    """
    registry = get_city_registry()
    return registry.get_all_cities(eligible_only=eligible)
