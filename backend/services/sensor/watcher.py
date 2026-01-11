#!/usr/bin/env python3
"""
Guardian Sensor - File Integrity Monitor (FIM)
Part of the Neural Draft Guardian Security Stack

Monitors specified directories for file creation, modification, and deletion
using inotify. Sends real-time alerts to the Sentinel Gateway.
"""

import hashlib
import json
import logging
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

try:
    import inotify_simple
except ImportError:
    inotify_simple = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - GUARDIAN-FIM - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/guardian/fim.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """File system event types monitored by FIM"""

    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    MOVED_FROM = "MOVED_FROM"
    MOVED_TO = "MOVED_TO"
    ACCESSED = "ACCESSED"
    ATTRIB_CHANGED = "ATTRIB_CHANGED"


class FileIntegrityMonitor:
    """
    Real-time File Integrity Monitor using inotify.

    Detects unauthorized changes to critical system files and web content.
    Essential for catching web shell uploads and configuration tampering.
    """

    # Flags mapping for inotify
    INOTIFY_FLAGS = {
        EventType.CREATED: inotify_simple.flags.CREATE,
        EventType.MODIFIED: inotify_simple.flags.MODIFY,
        EventType.DELETED: inotify_simple.flags.DELETE,
        EventType.MOVED_FROM: inotify_simple.flags.MOVED_FROM,
        EventType.MOVED_TO: inotify_simple.flags.MOVED_TO,
    }

    def __init__(
        self,
        gateway_url: str = "http://localhost:8080/api/v1/sensor/events",
        monitored_paths: List[str] = None,
        alert_callback: Optional[Callable] = None,
        batch_interval: float = 0.1,
    ):
        """
        Initialize the File Integrity Monitor.

        Args:
            gateway_url: URL to send security events to
            monitored_paths: List of paths to monitor (default: /var/www/)
            alert_callback: Optional callback for immediate alert processing
            batch_interval: Seconds to batch events before sending
        """
        self.gateway_url = gateway_url
        self.monitored_paths = monitored_paths or ["/var/www/"]
        self.alert_callback = alert_callback
        self.batch_interval = batch_interval
        self._running = False
        self._event_buffer: List[dict] = []
        self._buffer_lock = threading.Lock()
        self._inotify = None
        self._watch_descriptors: Dict[int, str] = {}
        self._baseline_hash: Dict[str, str] = {}

        # Ensure log directory exists
        os.makedirs("/var/log/guardian/", exist_ok=True)

    def _calculate_file_hash(self, filepath: str) -> str:
        """
        Calculate SHA-256 hash of a file.

        Args:
            filepath: Path to the file

        Returns:
            Hexadecimal hash string
        """
        try:
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError) as e:
            logger.warning(f"Could not hash file {filepath}: {e}")
            return ""

    def _build_baseline(self) -> Dict[str, str]:
        """
        Build a baseline hash map of all files in monitored paths.

        Returns:
            Dictionary mapping filepath to hash
        """
        baseline = {}
        for monitored_path in self.monitored_paths:
            if os.path.exists(monitored_path):
                for root, dirs, files in os.walk(monitored_path):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        try:
                            baseline[filepath] = self._calculate_file_hash(filepath)
                        except Exception as e:
                            logger.warning(f"Could not hash {filepath}: {e}")
        return baseline

    def _initialize_inotify(self):
        """Initialize inotify watches on monitored paths."""
        if inotify_simple is None:
            logger.error(
                "inotify_simple not installed. Run: pip install inotify_simple"
            )
            sys.exit(1)

        self._inotify = inotify_simple.INOTIFY()

        for path in self.monitored_paths:
            if os.path.exists(path):
                wd = self._inotify.add_watch(
                    path,
                    inotify_simple.flags.CREATE
                    | inotify_simple.flags.MODIFY
                    | inotify_simple.flags.DELETE
                    | inotify_simple.flags.MOVED_FROM
                    | inotify_simple.flags.MOVED_TO
                    | inotify_simple.flags.CLOSE_WRITE
                    | inotify_simple.flags.ATTRIB,
                )
                self._watch_descriptors[wd] = path
                logger.info(f"Watching {path} (wd={wd})")
            else:
                logger.warning(f"Monitored path does not exist: {path}")

    def _map_event_to_type(self, flags: int) -> EventType:
        """
        Map inotify flags to EventType enum.

        Args:
            flags: inotify event flags

        Returns:
            Corresponding EventType
        """
        if flags & inotify_simple.flags.CREATE:
            return EventType.CREATED
        elif flags & inotify_simple.flags.DELETE:
            return EventType.DELETED
        elif flags & inotify_simple.flags.MODIFY:
            return EventType.MODIFIED
        elif flags & inotify_simple.flags.MOVED_FROM:
            return EventType.MOVED_FROM
        elif flags & inotify_simple.flags.MOVED_TO:
            return EventType.MOVED_TO
        elif flags & inotify_simple.flags.ATTRIB:
            return EventType.ATTRIB_CHANGED
        else:
            return EventType.ACCESSED

    def _create_event_payload(self, event) -> dict:
        """
        Create a standardized event payload for the Gateway.

        Args:
            event: inotify event object

        Returns:
            Dictionary payload for API transmission
        """
        watch_path = self._watch_descriptors.get(event.wd, "/")
        filepath = os.path.join(watch_path, event.name) if event.name else watch_path

        # Calculate file hash for modified/created files
        file_hash = ""
        if event.flags & (
            inotify_simple.flags.CREATE
            | inotify_simple.flags.MODIFY
            | inotify_simple.flags.CLOSE_WRITE
        ):
            file_hash = self._calculate_file_hash(filepath)

        # Check if this represents a baseline deviation
        is_new = filepath not in self._baseline_hash
        hash_changed = is_new or (
            file_hash
            and filepath in self._baseline_hash
            and self._baseline_hash[filepath] != file_hash
        )

        payload = {
            "sensor_id": os.getenv("GUARDIAN_SENSOR_ID", "unknown"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "FIM_ALERT",
            "data": {
                "event_type": self._map_event_to_type(event.flags).value,
                "filepath": filepath,
                "watch_path": watch_path,
                "file_hash": file_hash,
                "is_new_file": is_new,
                "hash_changed": hash_changed,
                "size": os.path.getsize(filepath) if os.path.exists(filepath) else 0,
            },
            "threat_score": self._calculate_threat_score(filepath, event),
            "metadata": {
                "watch_descriptor": event.wd,
                "cookie": event.cookie,
                "raw_flags": event.flags,
            },
        }

        return payload

    def _calculate_threat_score(self, filepath: str, event) -> float:
        """
        Calculate threat score based on file characteristics.

        Args:
            filepath: Path to the affected file
            event: inotify event

        Returns:
            Threat score (0-100)
        """
        score = 0.0

        # Critical file modifications
        critical_patterns = [
            ".env",
            "nginx.conf",
            "docker-compose",
            "Dockerfile",
            ".htaccess",
            "wp-config.php",
            "config.php",
        ]

        filepath_lower = filepath.lower()
        for pattern in critical_patterns:
            if pattern in filepath_lower:
                score = max(score, 90.0)

        # Web shell patterns
        web_shell_indicators = [
            "eval(",
            "base64_decode",
            "shell_exec",
            "system(",
            "passthru",
            "$HTTP_",
        ]

        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read(8192)  # Read first 8KB
                for indicator in web_shell_indicators:
                    if indicator in content:
                        score = max(score, 95.0)
                        break
        except (IOError, OSError):
            pass

        # File type risk
        if filepath.endswith((".php", ".js", ".py", ".sh", ".exe", ".elf")):
            score = max(score, 60.0)

        # Deletion events are suspicious
        if event.flags & inotify_simple.flags.DELETE:
            score = max(score, 70.0)

        return min(score, 100.0)

    def _flush_buffer(self):
        """Send buffered events to the Gateway."""
        with self._buffer_lock:
            if not self._event_buffer:
                return

            payload = {
                "sensor_id": os.getenv("GUARDIAN_SENSOR_ID", "unknown"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": "FIM_BATCH",
                "events": self._event_buffer,
            }

            self._event_buffer.clear()

        # In production, use proper HTTP client with retries
        try:
            import requests

            response = requests.post(self.gateway_url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.debug(f"Sent {len(payload['events'])} FIM events to Gateway")
            else:
                logger.warning(f"Gateway returned {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send events to Gateway: {e}")
            # Re-queue events for retry (in production, use proper queue)

    def start(self):
        """Start monitoring the configured paths."""
        logger.info("Starting Guardian File Integrity Monitor...")

        # Build baseline before starting
        self._baseline_hash = self._build_baseline()
        logger.info(f"Baseline established with {len(self._baseline_hash)} files")

        self._initialize_inotify()
        self._running = True

        # Event processing thread
        def process_events():
            while self._running:
                try:
                    events = self._inotify.read(timeout=100)
                    if events:
                        for event in events:
                            payload = self._create_event_payload(event)

                            with self._buffer_lock:
                                self._event_buffer.append(payload)

                            # Immediate callback for high-priority events
                            if self.alert_callback and payload["threat_score"] > 80:
                                self.alert_callback(payload)

                        # Flush buffer after batch
                        self._flush_buffer()

                except Exception as e:
                    logger.error(f"Event processing error: {e}")

        # Start processing thread
        self._process_thread = threading.Thread(target=process_events, daemon=True)
        self._process_thread.start()

        logger.info("Guardian File Integrity Monitor active")

        # Keep main thread alive
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop monitoring and cleanup."""
        logger.info("Stopping Guardian File Integrity Monitor...")
        self._running = False

        if self._inotify:
            for wd in self._watch_descriptors:
                try:
                    self._inotify.remove_watch(wd)
                except Exception:
                    pass

        self._flush_buffer()
        logger.info("Guardian File Integrity Monitor stopped")


def main():
    """Entry point for running FIM as a standalone service."""
    import argparse

    parser = argparse.ArgumentParser(description="Guardian File Integrity Monitor")
    parser.add_argument(
        "--gateway",
        default="http://localhost:8080/api/v1/sensor/events",
        help="Gateway URL for event submission",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["/var/www/", "/etc/", "/home/"],
        help="Paths to monitor",
    )
    parser.add_argument(
        "--sensor-id",
        default=os.getenv("GUARDIAN_SENSOR_ID", "fim-sensor-01"),
        help="Unique sensor identifier",
    )

    args = parser.parse_args()

    # Set environment variable
    os.environ["GUARDIAN_SENSOR_ID"] = args.sensor_id

    # Initialize and start monitor
    monitor = FileIntegrityMonitor(gateway_url=args.gateway, monitored_paths=args.paths)

    monitor.start()


if __name__ == "__main__":
    main()
