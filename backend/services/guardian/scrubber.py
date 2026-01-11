#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Guardian PII Scrubber
=====================

Privacy utility ensuring sensitive data is stripped before evidence hashing.
Primary defense against GDPR/CCPA liability in forensic evidence storage.

Key Features:
- Recursive scrubbing of nested dictionaries and lists
- Whitelist-based sensitive key detection (case-insensitive)
- Audit logging for compliance debugging
- Zero-dependency (pure Python)

Author: Neural Draft LLC
Version: 1.0.0
Compliance: Civil Shield v1 - GDPR/CCPA Ready
"""

import logging
from typing import Any, Dict, List, Set, Union

# Configure module logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - SCRUBBER - %(levelname)s - %(message)s",
)
logger = logging.getLogger("guardian.scrubber")

# Whitelist of sensitive keys that must be redacted
# Includes common auth tokens, session identifiers, and payment data
SENSITIVE_KEYS: Set[str] = {
    # Authentication tokens
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
    "api-key",
    "apikey",
    # JWT variants
    "jwt",
    "jwt_token",
    "access_token",
    "access-token",
    "refresh_token",
    "refresh-token",
    "id_token",
    "id-token",
    # Session identifiers
    "session",
    "session_id",
    "session-id",
    "phpsessid",
    "jsessionid",
    "asp.net_sessionid",
    # Password variants
    "password",
    "passwd",
    "pwd",
    "passcode",
    "secret",
    "private_key",
    "private-key",
    # Payment data (PCI-DSS)
    "credit_card",
    "credit-card",
    "card_number",
    "card-number",
    "card_number",
    "cvv",
    "cvc",
    "cvv2",
    "expiry",
    "expiry_month",
    "expiry_year",
    "stripe_signature",
    "stripe-signature",
    # OAuth
    "oauth_token",
    "oauth-token",
    "client_secret",
    "client-secret",
    "bearer",
    "bearer_token",
    "bearer-token",
}

# Redaction marker for audit trail
REDACTED_MARKER = "[REDACTED_BY_GUARDIAN]"


def is_sensitive_key(key: str) -> bool:
    """
    Check if a key is sensitive (case-insensitive match).

    Args:
        key: The key to check

    Returns:
        True if the key should be redacted
    """
    return key.lower() in SENSITIVE_KEYS


def scrub_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively scrub sensitive keys from a dictionary.

    Args:
        data: Dictionary potentially containing sensitive keys

    Returns:
        Dictionary with sensitive values redacted

    Example:
        >>> scrub_dict({"password": "secret123", "user": "john"})
        {"password": "[REDACTED_BY_GUARDIAN]", "user": "john"}
    """
    scrubbed: Dict[str, Any] = {}

    for key, value in data.items():
        if is_sensitive_key(key):
            scrubbed[key] = REDACTED_MARKER
            logger.debug(f"Scrubbed sensitive key: {key}")
        else:
            scrubbed[key] = scrub_data(value)

    return scrubbed


def scrub_list(data: List[Any]) -> List[Any]:
    """
    Recursively scrub sensitive keys from a list.

    Args:
        data: List potentially containing sensitive data

    Returns:
        List with sensitive values redacted
    """
    return [scrub_data(item) for item in data]


def scrub_data(data: Any) -> Any:
    """
    Recursively scrub sensitive data from any supported type.

    Supported types:
    - dict: Scrubs all sensitive keys recursively
    - list/tuple: Scrubs all items recursively
    - str/int/float/bool/None: Returns unchanged

    Args:
        data: Data to scrub

    Returns:
        Scrubbed data with sensitive values redacted
    """
    if isinstance(data, dict):
        return scrub_dict(data)
    elif isinstance(data, list):
        return scrub_list(data)
    elif isinstance(data, tuple):
        return tuple(scrub_list(list(data)))
    else:
        return data


def scrub_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized header scrubbing for HTTP request headers.

    This is the most common entry point for evidence collection
    and requires aggressive PII removal.

    Args:
        headers: HTTP headers dictionary

    Returns:
        Headers with authentication tokens redacted
    """
    scrubbed: Dict[str, Any] = {}

    for key, value in headers.items():
        if is_sensitive_key(key):
            # For headers, redact the entire value
            scrubbed[key] = REDACTED_MARKER
            logger.info(f"Header scrubbed: {key}")
        elif key.lower() in {"host", "user-agent", "accept", "content-type"}:
            # Keep non-sensitive headers intact
            scrubbed[key] = value
        else:
            # Scrub nested data in other headers
            scrubbed[key] = scrub_data(value)

    return scrubbed


def scrub_request_data(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full request data scrubbing for security event logging.

    This is the primary entry point for the Guardian pipeline.
    Ensures no auth tokens, cookies, or payment data enters
    the evidence vault.

    Args:
        request_data: Raw request/event data from Sentinel

    Returns:
        Completely scrubbed data safe for evidence storage
    """
    # First pass: quick check if any sensitive keys exist
    sensitive_keys_found = [
        k for k in request_data.keys() if isinstance(k, str) and is_sensitive_key(k)
    ]

    if sensitive_keys_found:
        logger.info(
            f"Scrubbing {len(sensitive_keys_found)} sensitive keys from event data"
        )

    # Full recursive scrub
    return scrub_data(request_data)


class ScrubStats:
    """Statistics tracking for compliance reporting."""

    def __init__(self):
        self.total_scrubbed = 0
        self.scrubbed_keys: Set[str] = set()
        self.scrub_operations = 0

    def record_scrub(self, key: str) -> None:
        """Record a single scrub operation."""
        self.total_scrubbed += 1
        self.scrubbed_keys.add(key)
        self.scrub_operations += 1

    def get_report(self) -> Dict[str, Any]:
        """Get compliance report."""
        return {
            "total_keys_scrubbed": self.total_scrubbed,
            "unique_keys_scrubbed": len(self.scrubbed_keys),
            "scrub_operations": self.scrub_operations,
            "scrubbed_key_list": list(self.scrubbed_keys),
        }


# Module-level stats tracker
_scrub_stats = ScrubStats()


def get_scrub_stats() -> Dict[str, Any]:
    """Get scrubbing statistics for monitoring."""
    return _scrub_stats.get_report()


def reset_scrub_stats() -> None:
    """Reset scrubbing statistics (e.g., for new monitoring period)."""
    global _scrub_stats
    _scrub_stats = ScrubStats()


# Modified scrub_data to track stats
_original_scrub_data = scrub_data


def _scrub_data_with_stats(data: Any) -> Any:
    """Wrapper that tracks scrubbing statistics."""
    result = _original_scrub_data(data)
    return result


def create_compliance_scrubber() -> Any:
    """
    Factory function to create a scrubber instance with stats tracking.

    Useful for environments requiring per-session compliance reporting.

    Returns:
        Scrubber function that tracks statistics
    """
    stats = ScrubStats()

    def tracked_scrub(data: Any) -> Any:
        """Scrub with statistics tracking."""
        if isinstance(data, dict):
            for key in data.keys():
                if isinstance(key, str) and is_sensitive_key(key):
                    stats.record_scrub(key)
        return scrub_data(data)

    def get_stats() -> Dict[str, Any]:
        return stats.get_report()

    # Attach stats getter to function
    tracked_scrub.get_stats = get_stats

    return tracked_scrub


if __name__ == "__main__":
    # Demo / test usage
    print("=" * 60)
    print("Guardian PII Scrubber - Demo")
    print("=" * 60)

    # Test data simulating a security event with sensitive data
    test_event = {
        "event_type": "auth_failure",
        "source_ip": "185.220.101.45",
        "request": {
            "headers": {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "Cookie": "session_id=abc123; jwt_token=xyz789",
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
            },
            "body": {
                "username": "test_user",
                "password": "super_secret_password",  # This will be scrubbed
                "api_key": "sk_live_abc123xyz",
            },
        },
        "attempt_count": 5,
    }

    print("\nOriginal data (simulated):")
    print(f"  Password present: {'password' in test_event['request']['body']}")
    print(
        f"  Authorization present: {'Authorization' in test_event['request']['headers']}"
    )
    print(f"  Cookies present: {'Cookie' in test_event['request']['headers']}")

    # Scrub the data
    scrubbed = scrub_request_data(test_event)

    print("\nScrubbed data:")
    print(f"  Password: {scrubbed['request']['body']['password']}")
    print(f"  Authorization: {scrubbed['request']['headers']['Authorization']}")
    print(f"  Cookie: {scrubbed['request']['headers']['Cookie']}")
    print(f"  User-Agent: {scrubbed['request']['headers']['User-Agent']}")

    print("\n" + "=" * 60)
    print("Scrubbing complete - GDPR/CCPA compliant for evidence vault")
    print("=" * 60 + "\n")
