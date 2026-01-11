#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Guardian Reflex Controller
===========================

The "Trigger Puller" - Executes defensive actions from Guardian security events.

This module provides:
- Firewall rule management (iptables/nftables)
- Reflex action execution (BLOCK_IP, UNBLOCK_IP, etc.)
- Rate limiting to prevent action fatigue
- Audit logging for all reflex actions
- Dashboard metrics for real-time visibility

Author: Neural Draft LLC
Version: 1.0.0
Compliance: Civil Shield v1
"""

import asyncio
import json
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - REFLEX - %(levelname)s - %(message)s",
)
logger = logging.getLogger("guardian.reflex")


class ReflexAction(Enum):
    """Supported reflex actions."""

    BLOCK_IP = "BLOCK_IP"
    UNBLOCK_IP = "UNBLOCK_IP"
    RATE_LIMIT = "RATE_LIMIT"
    LOG_EVENT = "LOG_EVENT"
    NOTIFY_ADMIN = "NOTIFY_ADMIN"
    GENERATE_REPORT = "GENERATE_REPORT"
    QUARANTINE = "QUARANTINE"


class BlockReason(Enum):
    """Reason for IP block."""

    BRUTE_FORCE = "brute_force"
    PORT_SCAN = "port_scan"
    WEB_ATTACK = "web_attack"
    SUSPICIOUS = "suspicious_activity"
    MANUAL = "manual_override"
    THREAT_INTEL = "threat_intel_match"


@dataclass
class ReflexEvent:
    """Security event requiring reflex action."""

    event_id: str
    timestamp: str
    event_type: str
    source_ip: str
    actions: List[ReflexAction]
    priority: int  # 1=critical, 5=low
    metadata: Dict[str, Any] = field(default_factory=dict)
    block_reason: Optional[BlockReason] = None


@dataclass
class BlockRule:
    """Active block rule in the firewall."""

    ip_address: str
    action: str
    timestamp: str
    reason: str
    expires_at: Optional[str] = None
    event_id: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class ReflexMetrics:
    """Real-time metrics for dashboard."""

    total_events: int = 0
    blocked_ips: int = 0
    unblocked_ips: int = 0
    rate_limits: int = 0
    admin_notifications: int = 0
    failed_actions: int = 0
    last_event_timestamp: Optional[str] = None
    blocked_ips_list: List[str] = field(default_factory=list)


class FirewallManager:
    """
    Manages firewall rules via iptables/nftables.
    Provides abstraction layer for different firewall backends.
    """

    def __init__(self, firewall_backend: str = "iptables"):
        """
        Initialize firewall manager.

        Args:
            firewall_backend: 'iptables' or 'nftables'
        """
        self.backend = firewall_backend
        self._lock = threading.Lock()
        self._active_rules: Dict[str, BlockRule] = {}

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked."""
        with self._lock:
            return ip_address in self._active_rules

    def block_ip(
        self,
        ip_address: str,
        reason: BlockReason,
        event_id: Optional[str] = None,
        duration_seconds: Optional[int] = None,
    ) -> bool:
        """
        Add IP to firewall block list.

        Args:
            ip_address: IP to block
            reason: Reason for block
            event_id: Associated event ID
            duration_seconds: Optional auto-unblock time

        Returns:
            True if successful
        """
        with self._lock:
            if ip_address in self._active_rules:
                logger.info(f"IP already blocked: {ip_address}")
                return True

        try:
            if self.backend == "iptables":
                success = self._iptables_block(ip_address, reason)
            else:
                success = self._nftables_block(ip_address, reason)

            if success:
                expires_at = None
                if duration_seconds:
                    expires_at = (
                        datetime.utcnow() + timedelta(seconds=duration_seconds)
                    ).isoformat() + "Z"

                rule = BlockRule(
                    ip_address=ip_address,
                    action="DROP",
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    reason=reason.value,
                    expires_at=expires_at,
                    event_id=event_id,
                    rule_id=f"GR-{int(time.time())}-{ip_address.replace('.', '')}",
                )

                with self._lock:
                    self._active_rules[ip_address] = rule

                logger.warning(f"BLOCKED: {ip_address} ({reason.value})")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to block {ip_address}: {e}")
            return False

    def unblock_ip(self, ip_address: str, reason: str = "manual") -> bool:
        """
        Remove IP from firewall block list.

        Args:
            ip_address: IP to unblock
            reason: Reason for unblock

        Returns:
            True if successful
        """
        with self._lock:
            if ip_address not in self._active_rules:
                logger.info(f"IP not blocked, skipping unblock: {ip_address}")
                return True

        try:
            if self.backend == "iptables":
                success = self._iptables_unblock(ip_address)
            else:
                success = self._nftables_unblock(ip_address)

            if success:
                with self._lock:
                    removed = self._active_rules.pop(ip_address, None)

                if removed:
                    logger.info(f"UNBLOCKED: {ip_address} ({reason})")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to unblock {ip_address}: {e}")
            return False

    def _iptables_block(self, ip_address: str, reason: BlockReason) -> bool:
        """Execute iptables block command."""
        comment = f"GuardianReflex-{reason.value}"

        try:
            result = subprocess.run(
                [
                    "iptables",
                    "-A",
                    "INPUT",
                    "-s",
                    ip_address,
                    "-j",
                    "DROP",
                    "-m",
                    "comment",
                    "--comment",
                    comment,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True
            logger.error(f"iptables block failed: {result.stderr}")
            return False

        except FileNotFoundError:
            logger.warning("iptables not available, simulating block")
            return True
        except subprocess.TimeoutExpired:
            logger.error(f"iptables timeout for {ip_address}")
            return False

    def _iptables_unblock(self, ip_address: str) -> bool:
        """Execute iptables unblock command."""
        try:
            result = subprocess.run(
                [
                    "iptables",
                    "-D",
                    "INPUT",
                    "-s",
                    ip_address,
                    "-j",
                    "DROP",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True
            logger.warning(f"iptables unblock (rule may not exist): {result.stderr}")
            return True  # Success even if rule didn't exist

        except Exception as e:
            logger.error(f"iptables unblock error: {e}")
            return False

    def _nftables_block(self, ip_address: str, reason: BlockReason) -> bool:
        """Execute nftables block command (placeholder)."""
        # Implementation for nftables
        logger.info(f"[nftables] Would block {ip_address}: {reason.value}")
        return True

    def _nftables_unblock(self, ip_address: str) -> bool:
        """Execute nftables unblock command (placeholder)."""
        logger.info(f"[nftables] Would unblock {ip_address}")
        return True

    def get_active_blocks(self) -> List[BlockRule]:
        """Get list of all active block rules."""
        with self._lock:
            return list(self._active_rules.values())


class ActionRateLimiter:
    """Rate limiter to prevent action fatigue."""

    def __init__(
        self,
        max_actions_per_minute: int = 10,
        cooldown_seconds: int = 60,
    ):
        """
        Initialize rate limiter.

        Args:
            max_actions_per_minute: Max actions in time window
            cooldown_seconds: Cooldown between same-IP actions
        """
        self.max_per_minute = max_actions_per_minute
        self.cooldown = cooldown_seconds
        self._action_counts: Dict[str, List[float]] = {}
        self._ip_cooldowns: Dict[str, float] = {}

    def can_execute(self, ip_address: str, action: str) -> bool:
        """Check if action can be executed for IP."""
        now = time.time()

        # Check cooldown
        if ip_address in self._ip_cooldowns:
            if now < self._ip_cooldowns[ip_address]:
                remaining = int(self._ip_cooldowns[ip_address] - now)
                logger.warning(f"IP {ip_address} in cooldown ({remaining}s)")
                return False

        # Check rate limit
        window_start = now - 60
        if ip_address not in self._action_counts:
            self._action_counts[ip_address] = []

        # Clean old entries
        self._action_counts[ip_address] = [
            t for t in self._action_counts[ip_address] if t > window_start
        ]

        if len(self._action_counts[ip_address]) >= self.max_per_minute:
            logger.warning(f"Rate limit exceeded for {ip_address}")
            return False

        return True

    def record_action(self, ip_address: str, action: str) -> None:
        """Record action execution."""
        now = time.time()
        if ip_address not in self._action_counts:
            self._action_counts[ip_address] = []
        self._action_counts[ip_address].append(now)

        # Set cooldown
        self._ip_cooldowns[ip_address] = now + self.cooldown


class ReflexController:
    """
    Main Guardian Reflex Controller.

    Orchestrates security event processing and reflex action execution.
    Provides real-time metrics for dashboard integration.
    """

    def __init__(
        self,
        firewall_backend: str = "iptables",
        max_actions_per_minute: int = 10,
        simulation_mode: bool = False,
    ):
        """
        Initialize Reflex Controller.

        Args:
            firewall_backend: 'iptables' or 'nftables'
            max_actions_per_minute: Rate limit for actions
            simulation_mode: If True, don't actually block (dev environment)
        """
        self.simulation_mode = simulation_mode
        self.firewall = FirewallManager(firewall_backend)
        self.rate_limiter = ActionRateLimiter(
            max_actions_per_minute=max_actions_per_minute
        )
        self.metrics = ReflexMetrics()
        self._running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._lock = threading.Lock()

    async def start(self) -> None:
        """Start the reflex controller."""
        self._running = True
        logger.info("Reflex Controller started")

        # Start event processor
        asyncio.create_task(self._process_events())

        # Start cleanup task for expired blocks
        asyncio.create_task(self._cleanup_expired_blocks())

    async def stop(self) -> None:
        """Stop the reflex controller."""
        self._running = False
        logger.info("Reflex Controller stopped")

    async def submit_event(self, event: ReflexEvent) -> bool:
        """
        Submit a security event for reflex processing.

        Args:
            event: Security event to process

        Returns:
            True if event was accepted
        """
        try:
            await self._event_queue.put(event)
            with self._lock:
                self.metrics.total_events += 1
                self.metrics.last_event_timestamp = event.timestamp
            return True
        except Exception as e:
            logger.error(f"Failed to submit event: {e}")
            return False

    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0,
                )

                await self._execute_reflex_actions(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")

    async def _execute_reflex_actions(self, event: ReflexEvent) -> None:
        """
        Execute reflex actions for an event.

        Args:
            event: Event to process
        """
        logger.info(f"Processing event: {event.event_type} from {event.source_ip}")

        for action in event.actions:
            if action == ReflexAction.BLOCK_IP:
                await self._execute_block(event)
            elif action == ReflexAction.UNBLOCK_IP:
                await self._execute_unblock(event)
            elif action == ReflexAction.RATE_LIMIT:
                await self._execute_rate_limit(event)
            elif action == ReflexAction.NOTIFY_ADMIN:
                await self._execute_notify_admin(event)
            elif action == ReflexAction.LOG_EVENT:
                self._execute_log(event)
            elif action == ReflexAction.GENERATE_REPORT:
                await self._execute_generate_report(event)

    async def _execute_block(self, event: ReflexEvent) -> None:
        """Execute BLOCK_IP action."""
        if not self.rate_limiter.can_execute(event.source_ip, "BLOCK_IP"):
            with self._lock:
                self.metrics.failed_actions += 1
            return

        reason = event.block_reason or BlockReason.SUSPICIOUS

        if self.simulation_mode:
            logger.info(f"[SIMULATION] Would block: {event.source_ip} ({reason.value})")
            with self._lock:
                self.metrics.blocked_ips += 1
                if event.source_ip not in self.metrics.blocked_ips_list:
                    self.metrics.blocked_ips_list.append(event.source_ip)
            self.rate_limiter.record_action(event.source_ip, "BLOCK_IP")
            return

        success = self.firewall.block_ip(
            ip_address=event.source_ip,
            reason=reason,
            event_id=event.event_id,
        )

        if success:
            with self._lock:
                self.metrics.blocked_ips += 1
                if event.source_ip not in self.metrics.blocked_ips_list:
                    self.metrics.blocked_ips_list.append(event.source_ip)
        else:
            with self._lock:
                self.metrics.failed_actions += 1

        self.rate_limiter.record_action(event.source_ip, "BLOCK_IP")

    async def _execute_unblock(self, event: ReflexEvent) -> None:
        """Execute UNBLOCK_IP action."""
        success = self.firewall.unblock_ip(
            ip_address=event.source_ip,
            reason=event.metadata.get("unblock_reason", "manual"),
        )

        if success:
            with self._lock:
                self.metrics.unblocked_ips += 1
                if event.source_ip in self.metrics.blocked_ips_list:
                    self.metrics.blocked_ips_list.remove(event.source_ip)

    async def _execute_rate_limit(self, event: ReflexEvent) -> None:
        """Execute RATE_LIMIT action."""
        logger.info(f"Rate limiting: {event.source_ip}")
        with self._lock:
            self.metrics.rate_limits += 1

    async def _execute_notify_admin(self, event: ReflexEvent) -> None:
        """Execute NOTIFY_ADMIN action."""
        logger.critical(f"ADMIN ALERT: {event.event_type} from {event.source_ip}")

        # In production, integrate with:
        # - PagerDuty API
        # - Slack webhooks
        # - Email (SMTP)
        # - SMS (Twilio)

        with self._lock:
            self.metrics.admin_notifications += 1

    def _execute_log(self, event: ReflexEvent) -> None:
        """Execute LOG_EVENT action."""
        logger.warning(
            f"SECURITY EVENT: {event.event_type} | "
            f"IP: {event.source_ip} | "
            f"ID: {event.event_id}"
        )

    async def _execute_generate_report(self, event: ReflexEvent) -> None:
        """Execute GENERATE_REPORT action."""
        logger.info(f"Generating report for event: {event.event_id}")
        # In production, generate PDF report and store in evidence vault

    async def _cleanup_expired_blocks(self) -> None:
        """Clean up expired block rules."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.utcnow()
                expired_ips = []

                for rule in self.firewall.get_active_blocks():
                    if rule.expires_at:
                        expires = datetime.fromisoformat(
                            rule.expires_at.replace("Z", "+00:00")
                        )
                        if now >= expires:
                            expired_ips.append(rule.ip_address)

                for ip in expired_ips:
                    self.firewall.unblock_ip(ip, reason="expired")

                if expired_ips:
                    logger.info(f"Cleaned up {len(expired_ips)} expired blocks")

            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for dashboard."""
        with self._lock:
            return {
                "total_events": self.metrics.total_events,
                "blocked_ips_count": self.metrics.blocked_ips,
                "unblocked_ips_count": self.metrics.unblocked_ips,
                "rate_limits": self.metrics.rate_limits,
                "admin_notifications": self.metrics.admin_notifications,
                "failed_actions": self.metrics.failed_actions,
                "last_event": self.metrics.last_event_timestamp,
                "active_blocked_ips": self.metrics.blocked_ips_list,
                "queue_size": self._event_queue.qsize(),
                "simulation_mode": self.simulation_mode,
            }

    def get_status(self) -> Dict[str, Any]:
        """Get controller status."""
        return {
            "running": self._running,
            "firewall_backend": self.firewall.backend,
            "simulation_mode": self.simulation_mode,
            "active_blocks": len(self.firewall.get_active_blocks()),
            "metrics": self.get_metrics(),
        }


async def demo():
    """Demonstrate reflex controller functionality."""
    print("\n" + "=" * 60)
    print("Guardian Reflex Controller Demo")
    print("=" * 60 + "\n")

    # Create controller in simulation mode
    controller = ReflexController(simulation_mode=True)
    await controller.start()

    # Submit demo events
    demo_events = [
        ReflexEvent(
            event_id="evt-001",
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type="auth_failure",
            source_ip="185.220.101.45",
            actions=[
                ReflexAction.BLOCK_IP,
                ReflexAction.LOG_EVENT,
                ReflexAction.NOTIFY_ADMIN,
            ],
            priority=1,
            block_reason=BlockReason.BRUTE_FORCE,
        ),
    ]

    for event in demo_events:
        print(f"\nSubmitting: {event.event_type} from {event.source_ip}")
        await controller.submit_event(event)
        await asyncio.sleep(0.5)  # Allow processing

    # Show metrics
    print("\n" + "-" * 40)
    print("Dashboard Metrics:")
    print("-" * 40)
    metrics = controller.get_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    await controller.stop()
    print("\n" + "=" * 60)
    print("Demo complete")
    print("=" * 60 + "\n")


def get_reflex_controller(
    firewall_backend: str = "iptables",
    simulation_mode: bool = False,
) -> ReflexController:
    """
    Get a ReflexController instance.

    Args:
        firewall_backend: 'iptables' or 'nftables'
        simulation_mode: Run without actual firewall commands

    Returns:
        Configured ReflexController instance
    """
    return ReflexController(
        firewall_backend=firewall_backend,
        simulation_mode=simulation_mode,
    )


if __name__ == "__main__":
    asyncio.run(demo())
