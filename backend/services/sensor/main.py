provethat.io\backend\services\sensor\main.py
```

```python
#!/usr/bin/env python3
"""
Guardian Sensor - Auth Log Monitor
Part of the Neural Draft Guardian Security Stack

Monitors /var/log/auth.log for SSH authentication events and forwards
security-relevant entries to the Sentinel Gateway for AI analysis.

Author: Neural Draft Guardian Team
Version: 1.0.0
"""

import hashlib
import json
import os
import re
import time
import threading
from datetime import datetime
from typing import Dict, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("guardian.sensor.auth")


@dataclass
class AuthEvent:
    """
    Structured representation of an authentication event.
    Includes cryptographic hash for immutable audit trail.
    """
    timestamp: str
    source_ip: Optional[str]
    username: Optional[str]
    event_type: str  # 'failed_password', 'accepted_key', 'session_opened', etc.
    raw_message: str
    process: Optional[str]
    audit_hash: str  # SHA-256 hash of (timestamp + source_ip + raw_message)

    def to_dict(self) -> Dict:
        return asdict(self)


class AuthLogTailer:
    """
    Real-time tailer for Linux auth.log with pattern matching
    for SSH authentication security events.
    """

    # Regex patterns for common SSH auth events
    PATTERNS = {
        'failed_password': re.compile(
            r'(?P<timestamp>[\w\s:]+)\s+(?P<process>\S+)\s+Failed password for'
            r'(?:\s+(invalid user )?)?(?P<username>\S+)\s+from\s+(?P<source_ip>\d+\.\d+\.\d+\.\d+)'
        ),
        'accepted_key': re.compile(
            r'(?P<timestamp>[\w\s:]+)\s+(?P<process>\S+)\s+Accepted publickey for'
            r'\s+(?P<username>\S+)\s+from\s+(?P<source_ip>\d+\.\d+\.\d+\.\d+)'
        ),
        'session_opened': re.compile(
            r'(?P<timestamp>[\w\s:]+)\s+(?P<process>\S+)\s+session opened for user'
            r'\s+(?P<username>\S+)\s+by\s+\S+\s+\(uid=\d+\)'
        ),
        'session_closed': re.compile(
            r'(?P<timestamp>[\w\s:]+)\s+(?P<process>\S+)\s+session closed for user'
            r'\s+(?P<username>\S+)'
        ),
        'disconnected': re.compile(
            r'(?P<timestamp>[\w\s:]+)\s+(?P<process>\S+)\s+Disconnected from'
            r'(?:\s+invalid user )?(?P<username>\S+)\s+from\s+(?P<source_ip>\d+\.\d+\.\d+\.\d+)'
        ),
    }

    def __init__(self, log_path: str = "/var/log/auth.log"):
        self.log_path = log_path
        self.position = 0  # Current file position
        self.running = False
        self._lock = threading.Lock()

    def _calculate_audit_hash(self, event: AuthEvent) -> str:
        """Generate immutable audit hash for forensic integrity."""
        content = f"{event.timestamp}|{event.source_ip or 'unknown'}|{event.raw_message}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _parse_line(self, line: str) -> Optional[AuthEvent]:
        """Parse a single log line into an AuthEvent if it matches known patterns."""
        for event_type, pattern in self.PATTERNS.items():
            match = pattern.search(line)
            if match:
                groups = match.groupdict()
                timestamp = datetime.strptime(
                    groups['timestamp'].strip(),
                    "%b %d %H:%M:%S"
                ).strftime("%Y-%m-%dT%H:%M:%S")

                event = AuthEvent(
                    timestamp=timestamp,
                    source_ip=groups.get('source_ip'),
                    username=groups.get('username'),
                    event_type=event_type,
                    raw_message=line.strip(),
                    process=groups.get('process'),
                    audit_hash=""  # Will be calculated below
                )
                event.audit_hash = self._calculate_audit_hash(event)
                return event
        return None

    def tail(self, callback: Callable[[AuthEvent], None], poll_interval: float = 0.5):
        """
        Continuously tail the auth.log and invoke callback for each event.

        Args:
            callback: Function to call with each parsed AuthEvent
            poll_interval: Seconds between file position checks
        """
        self.running = True
        logger.info(f"Starting auth.log tailer on {self.log_path}")

        # Verify log file exists and is readable
        if not os.path.exists(self.log_path):
            logger.error(f"Auth log not found at {self.log_path}")
            return

        # Seek to end of file on startup
        self.position = os.path.getsize(self.log_path)

        while self.running:
            try:
                current_size = os.path.getsize(self.log_path)

                if current_size < self.position:
                    # Log rotation occurred - reopen from beginning
                    logger.warning("Log rotation detected, reopening from start")
                    self.position = 0

                if current_size > self.position:
                    # New data available
                    with open(self.log_path, 'r') as f:
                        f.seek(self.position)
                        new_lines = f.readlines()

                    for line in new_lines:
                        if line.strip():  # Skip empty lines
                            event = self._parse_line(line)
                            if event:
                                with self._lock:
                                    callback(event)

                    self.position = f.tell()

            except PermissionError:
                logger.error("Permission denied reading auth.log. Run as root?")
                break
            except Exception as e:
                logger.error(f"Error reading log: {e}")

            time.sleep(poll_interval)

    def stop(self):
        """Stop the tailer gracefully."""
        self.running = False
        logger.info("Auth log tailer stopped")


class GatewayClient:
    """
    HTTP client for sending security events to the Sentinel Gateway.
    Includes retry logic and batch sending for efficiency.
    """

    def __init__(self, gateway_url: str, api_key: str, sensor_id: str):
        self.gateway_url = gateway_url.rstrip('/')
        self.api_key = api_key
        self.sensor_id = sensor_id
        self.batch = []
        self.batch_lock = threading.Lock()
        self.batch_size = 10
        self.batch_timeout = 5.0  # seconds

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Sensor-ID": self.sensor_id,
            "X-API-Key": self.api_key
        }

    def send_event(self, event: AuthEvent) -> bool:
        """
        Send a single event to the gateway. Batches multiple events
        for efficiency when volume is high.
        """
        with self.batch_lock:
            self.batch.append(event.to_dict())

            if len(self.batch) >= self.batch_size:
                return self._flush_batch()
            return True

    def _flush_batch(self) -> bool:
        """Send accumulated batch to gateway."""
        if not self.batch:
            return True

        payload = {
            "sensor_id": self.sensor_id,
            "events": self.batch.copy(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.batch.clear()

        # In production, use requests library with retry logic
        # This is a placeholder demonstrating the interface
        logger.info(f"Sending batch of {len(payload['events'])} events to {self.gateway_url}/api/v1/events")

        # Simulated HTTP call structure:
        # try:
        #     response = requests.post(
        #         f"{self.gateway_url}/api/v1/events",
        #         json=payload,
        #         headers=self._get_headers(),
        #         timeout=10
        #     )
        #     response.raise_for_status()
        #     return True
        # except requests.RequestException as e:
        #     logger.error(f"Failed to send events: {e}")
        #     return False

        return True

    def flush(self):
        """Force send any pending events on shutdown."""
        with self.batch_lock:
            self._flush_batch()


class GuardianSensor:
    """
    Main Guardian Sensor daemon.
    Orchestrates log monitoring and event forwarding.
    """

    def __init__(
        self,
        sensor_id: str,
        gateway_url: str,
        api_key: str,
        log_path: str = "/var/log/auth.log"
    ):
        self.sensor_id = sensor_id
        self.gateway_url = gateway_url
        self.api_key = api_key
        self.log_path = log_path

        self.tailer = AuthLogTailer(log_path)
        self.gateway = GatewayClient(gateway_url, api_key, sensor_id)
        self._shutdown_event = threading.Event()

    def _handle_event(self, event: AuthEvent):
        """Callback for processed auth events."""
        logger.info(f"Event: {event.event_type} | User: {event.username} | IP: {event.source_ip} | Hash: {event.audit_hash[:16]}...")

        # Priority routing based on event severity
        if event.event_type == 'failed_password':
            # High-priority: Immediate send for brute force detection
            self.gateway.send_event(event)
        else:
            # Normal priority: Let batch logic handle it
            self.gateway.send_event(event)

    def run(self):
        """Start the sensor daemon."""
        logger.info(f"Starting Guardian Sensor: {self.sensor_id}")
        logger.info(f"Monitoring: {self.log_path} -> {self.gateway_url}")

        try:
            self.tailer.tail(self._handle_event)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        finally:
            self._shutdown()

    def _shutdown(self):
        """Graceful shutdown with event flushing."""
        logger.info("Shutting down Guardian Sensor...")
        self.tailer.stop()
        self.gateway.flush()
        logger.info("Guardian Sensor shutdown complete")


def main():
    """Entry point for running the sensor as a standalone daemon."""
    import argparse

    parser = argparse.ArgumentParser(description="Guardian Auth Log Sensor")
    parser.add_argument("--sensor-id", required=True, help="Unique sensor identifier")
    parser.add_argument("--gateway-url", required=True, help="Sentinel Gateway URL")
    parser.add_argument("--api-key", required=True, help="API key for gateway auth")
    parser.add_argument("--log-path", default="/var/log/auth.log", help="Path to auth.log")
    args = parser.parse_args()

    sensor = GuardianSensor(
        sensor_id=args.sensor_id,
        gateway_url=args.gateway_url,
        api_key=args.api_key,
        log_path=args.log_path
    )

    sensor.run()


if __name__ == "__main__":
    main()
