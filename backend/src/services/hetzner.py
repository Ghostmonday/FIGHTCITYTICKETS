"""
Hetzner Cloud Service for FIGHTCITYTICKETS.com

Handles Hetzner Cloud droplet management, including suspension on failure.
Used for infrastructure management and failure recovery.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from ..config import settings

# Set up logger
logger = logging.getLogger(__name__)

# Hetzner API configuration
HETZNER_API_BASE = "https://api.hetzner.cloud/v1"


@dataclass
class DropletStatus:
    """Droplet status information."""

    id: str
    name: str
    status: str  # "running", "of", "suspended", etc.
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    server_type: Optional[str] = None


@dataclass
class SuspensionResult:
    """Result from droplet suspension operation."""

    success: bool
    droplet_id: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    error_message: Optional[str] = None


class HetznerService:
    """Service for managing Hetzner Cloud droplets."""

    def __init__(self):
        """Initialize Hetzner service."""
        self.api_token = getattr(settings, "hetzner_api_token", None)
        self.is_available = bool(self.api_token and self.api_token != "change-me")

        if not self.is_available:
            logger.warning("Hetzner API token not configured")

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Hetzner API."""
        if not self.api_token:
            raise ValueError("Hetzner API token not configured")

        return {
            "Authorization": "Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def get_droplet_by_name(self, name: str) -> Optional[DropletStatus]:
        """
        Get droplet information by name.

        Args:
            name: Droplet/server name

        Returns:
            DropletStatus if found, None otherwise
        """
        if not self.is_available:
            logger.warning("Hetzner API not available")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "{HETZNER_API_BASE}/servers",
                    headers=self._get_headers(),
                )

                if response.status_code == 200:
                    data = response.json()
                    servers = data.get("servers", [])

                    for server in servers:
                        if server.get("name") == name:
                            public_net = server.get("public_net", {})
                            ipv4 = None
                            ipv6 = None

                            if public_net.get("ipv4"):
                                ipv4 = public_net["ipv4"].get("ip")

                            if public_net.get("ipv6"):
                                ipv6 = public_net["ipv6"].get("ip")

                            return DropletStatus(
                                id=str(server.get("id")),
                                name=server.get("name", ""),
                                status=server.get("status", "unknown"),
                                ipv4=ipv4,
                                ipv6=ipv6,
                                server_type=server.get("server_type", {}).get("name"),
                            )

                    logger.warning("Droplet '{name}' not found")
                    return None

                else:
                    logger.error(
                        "Hetzner API error getting droplets: {response.status_code}"
                    )
                    return None

        except httpx.TimeoutException:
            logger.error("Hetzner API timeout")
            return None
        except Exception as e:
            logger.error("Error getting droplet by name: {e}")
            return None

    async def get_droplet_by_id(self, droplet_id: str) -> Optional[DropletStatus]:
        """
        Get droplet information by ID.

        Args:
            droplet_id: Droplet/server ID

        Returns:
            DropletStatus if found, None otherwise
        """
        if not self.is_available:
            logger.warning("Hetzner API not available")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "{HETZNER_API_BASE}/servers/{droplet_id}",
                    headers=self._get_headers(),
                )

                if response.status_code == 200:
                    server = response.json().get("server", {})

                    public_net = server.get("public_net", {})
                    ipv4 = None
                    ipv6 = None

                    if public_net.get("ipv4"):
                        ipv4 = public_net["ipv4"].get("ip")

                    if public_net.get("ipv6"):
                        ipv6 = public_net["ipv6"].get("ip")

                    return DropletStatus(
                        id=str(server.get("id")),
                        name=server.get("name", ""),
                        status=server.get("status", "unknown"),
                        ipv4=ipv4,
                        ipv6=ipv6,
                        server_type=server.get("server_type", {}).get("name"),
                    )

                else:
                    logger.error(
                        "Hetzner API error getting droplet {droplet_id}: {response.status_code}"
                    )
                    return None

        except httpx.TimeoutException:
            logger.error("Hetzner API timeout")
            return None
        except Exception as e:
            logger.error("Error getting droplet by ID: {e}")
            return None

    async def suspend_droplet(self, droplet_id: str) -> SuspensionResult:
        """
        Suspend a droplet (power off).

        Args:
            droplet_id: Droplet/server ID

        Returns:
            SuspensionResult with operation status
        """
        if not self.is_available:
            return SuspensionResult(
                success=False,
                error_message="Hetzner API token not configured",
            )

        try:
            # Get current status
            current_status = await self.get_droplet_by_id(droplet_id)
            if not current_status:
                return SuspensionResult(
                    success=False,
                    error_message="Droplet {droplet_id} not found",
                )

            previous_status = current_status.status

            # If already off or suspended, return success
            if previous_status in ("of", "suspended"):
                logger.info(
                    "Droplet {droplet_id} already {previous_status}, no action needed"
                )
                return SuspensionResult(
                    success=True,
                    droplet_id=droplet_id,
                    previous_status=previous_status,
                    new_status=previous_status,
                )

            # Power off the droplet
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "{HETZNER_API_BASE}/servers/{droplet_id}/actions/poweroff",
                    headers=self._get_headers(),
                    json={},
                )

                if response.status_code == 201:
                    logger.warning(
                        "Successfully suspended droplet {droplet_id} "
                        "(status: {previous_status} -> off)"
                    )
                    return SuspensionResult(
                        success=True,
                        droplet_id=droplet_id,
                        previous_status=previous_status,
                        new_status="of",
                    )
                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get(
                        "message", "Unknown Hetzner API error"
                    )

                    logger.error(
                        "Hetzner API error suspending droplet {droplet_id}: "
                        "{response.status_code} - {error_msg}"
                    )

                    return SuspensionResult(
                        success=False,
                        droplet_id=droplet_id,
                        previous_status=previous_status,
                        error_message="Hetzner API error: {error_msg}",
                    )

        except httpx.TimeoutException:
            logger.error("Hetzner API timeout suspending droplet {droplet_id}")
            return SuspensionResult(
                success=False,
                droplet_id=droplet_id,
                error_message="Hetzner API timeout",
            )
        except Exception as e:
            logger.error("Error suspending droplet {droplet_id}: {e}")
            return SuspensionResult(
                success=False,
                droplet_id=droplet_id,
                error_message="Unexpected error: {str(e)}",
            )

    async def suspend_droplet_by_name(self, name: str) -> SuspensionResult:
        """
        Suspend a droplet by name.

        Args:
            name: Droplet/server name

        Returns:
            SuspensionResult with operation status
        """
        droplet = await self.get_droplet_by_name(name)
        if not droplet:
            return SuspensionResult(
                success=False,
                error_message="Droplet '{name}' not found",
            )

        return await self.suspend_droplet(droplet.id)


# Global service instance
_hetzner_service = None


def get_hetzner_service() -> HetznerService:
    """Get the global Hetzner service instance."""
    global _hetzner_service
    if _hetzner_service is None:
        _hetzner_service = HetznerService()
    return _hetzner_service

