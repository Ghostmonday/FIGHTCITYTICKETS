"""
Guardian Security Services
===========================

Neural Draft LLC's autonomous infrastructure defense system.

This package integrates:
- Evidence: Legal-grade forensic evidence collection and immutable audit trails
- Hunter: Active threat intelligence and OSINT attribution engine

The Guardian system provides:
- Real-time security monitoring
- Cryptographic evidence hashing for legal admissibility
- Threat intelligence integration (VirusTotal, AbuseIPDB, Shodan)
- Forensic report generation for law enforcement referral
- Chain-of-custody tracking

Usage:
    from guardian import GuardianService, HunterService, EvidenceService

Author: Neural Draft LLC
Version: 1.0.0
Compliance: Civil Shield v1
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .evidence import (
    ChainOfCustody,
    EvidenceHasher,
    EvidenceService,
    EvidenceType,
    get_evidence_service,
)
from .hunter import (
    ForensicPursuitPackage,
    HunterService,
    ThreatIntelResult,
    get_hunter_service,
)

# Configure module logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - GUARDIAN - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__compliance_version__ = "civil_shield_v1"

__all__ = [
    # Evidence Services
    "EvidenceService",
    "EvidenceHasher",
    "EvidenceType",
    "ChainOfCustody",
    "get_evidence_service",
    # Hunter Services
    "HunterService",
    "ThreatIntelResult",
    "ForensicPursuitPackage",
    "get_hunter_service",
    # Main Service
    "GuardianService",
    # Utilities
    "log_security_event",
    "create_attack_report",
]


class GuardianService:
    """
    Main Guardian service coordinating defense and attribution.

    Integrates evidence collection, threat intelligence, and
    forensic reporting into a unified security service.
    """

    def __init__(
        self,
        sensor_id: str = "guardian-primary",
        collector_node: str = "guardian-node-01",
        evidence_storage: str = "/var/lib/guardian/evidence",
    ):
        """
        Initialize Guardian service.

        Args:
            sensor_id: Unique identifier for this sensor
            collector_node: Name of the collection node
            evidence_storage: Path for evidence storage
        """
        self.sensor_id = sensor_id
        self.collector_node = collector_node

        # Initialize sub-services
        self.evidence_service = get_evidence_service(
            storage_path=evidence_storage,
            collector_node=collector_node,
            sensor_id=sensor_id,
        )
        self.hunter_service = get_hunter_service()

        logger.info(f"GuardianService initialized: {sensor_id}")

    async def close(self):
        """Close all sub-service connections."""
        await self.hunter_service.close()
        logger.info("GuardianService connections closed")

    async def handle_security_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        attribution_enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        Handle a security event with evidence collection and optional attribution.

        Args:
            event_type: Type of security event (auth_failure, port_scan, etc.)
            event_data: Event details
            attribution_enabled: Whether to run Hunter attribution

        Returns:
            Dictionary with evidence_id, threat_info, and actions
        """
        result = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "evidence_id": None,
            "threat_info": None,
            "actions": [],
        }

        # Collect evidence
        evidence_metadata = None

        if event_type == "auth_failure":
            evidence_metadata = self.evidence_service.collect_auth_evidence(
                username=event_data.get("username", "unknown"),
                source_ip=event_data.get("source_ip", "0.0.0.0"),
                auth_method=event_data.get("auth_method", "password"),
                failure_reason=event_data.get("failure_reason", "unknown"),
                attempt_count=event_data.get("attempt_count", 1),
            )
            result["evidence_id"] = evidence_metadata.evidence_id

        elif event_type == "network_scan":
            evidence_metadata = self.evidence_service.collect_network_evidence(
                source_ip=event_data.get("source_ip", "0.0.0.0"),
                destination_ip=event_data.get("destination_ip", "0.0.0.0"),
                source_port=event_data.get("source_port", 0),
                destination_port=event_data.get("destination_port", 0),
                protocol=event_data.get("protocol", "TCP"),
                bytes_sent=event_data.get("bytes_sent", 0),
                bytes_received=event_data.get("bytes_received", 0),
                duration_ms=event_data.get("duration_ms", 0),
                flags=event_data.get("flags", ""),
                user_agent=event_data.get("user_agent"),
                ssl_fingerprint=event_data.get("ssl_fingerprint"),
                headers=event_data.get("headers", {}),
            )
            result["evidence_id"] = evidence_metadata.evidence_id

        elif event_type == "file_modification":
            evidence_metadata = self.evidence_service.collect_file_evidence(
                file_path=event_data.get("file_path", "/unknown"),
                operation=event_data.get("operation", "unknown"),
                file_hash=event_data.get("file_hash", ""),
                file_size=event_data.get("file_size", 0),
                file_permissions=event_data.get("file_permissions", "000"),
                user_id=event_data.get("user_id", "unknown"),
                process_name=event_data.get("process_name"),
            )
            result["evidence_id"] = evidence_metadata.evidence_id

        # Run attribution if enabled
        if attribution_enabled and event_data.get("source_ip"):
            try:
                threat_result = await self.hunter_service.investigate_ip(
                    ip_address=event_data["source_ip"],
                    user_agent=event_data.get("user_agent"),
                    ssl_fingerprint=event_data.get("ssl_fingerprint"),
                    headers=event_data.get("headers", {}),
                    evidence_id=evidence_metadata.evidence_id
                    if evidence_metadata
                    else None,
                )

                # Collect threat intel as evidence
                self.evidence_service.collect_threat_intel(
                    target_ip=event_data["source_ip"],
                    query_service="hunter_attribution",
                    threat_score=threat_result.threat_score,
                    is_malicious=threat_result.is_malicious,
                    threat_categories=[threat_result.threat_level.value],
                    asn_info=threat_result.asn_info,
                    geolocation=threat_result.geolocation.to_dict()
                    if threat_result.geolocation
                    else {},
                    abuse_ipdb_score=threat_result.abuse_ipdb_score,
                    virustotal_detections=threat_result.virustotal_positives,
                    shodan_data=threat_result.raw_responses.get("shodan", {}),
                )

                result["threat_info"] = {
                    "threat_score": threat_result.threat_score,
                    "threat_level": threat_result.threat_level.value,
                    "is_malicious": threat_result.is_malicious,
                    "location": (
                        f"{threat_result.geolocation.city}, {threat_result.geolocation.country_name}"
                        if threat_result.geolocation
                        else "Unknown"
                    ),
                    "infrastructure": threat_result.infrastructure_type.value,
                }

                # Generate recommended actions
                if threat_result.is_micious:
                    result["actions"].append("BLOCK_IP")
                    result["actions"].append("GENERATE_REPORT")

            except Exception as e:
                logger.error(f"Attribution failed: {e}")

        # Default actions based on event type
        if event_type == "auth_failure":
            attempts = event_data.get("attempt_count", 1)
            if attempts >= 5:
                result["actions"].append("BLOCK_IP")
            result["actions"].append("LOG_EVENT")
            result["actions"].append("NOTIFY_ADMIN")

        elif event_type == "network_scan":
            result["actions"].append("BLOCK_IP")
            result["actions"].append("LOG_EVENT")

        return result

    async def generate_case_report(
        self,
        evidence_ids: List[str],
        case_number: str,
        investigator: str = "Guardian System",
    ) -> str:
        """
        Generate a complete forensic case report.

        Args:
            evidence_ids: List of evidence IDs to include
            case_number: Case/reference number
            investigator: Name of investigator

        Returns:
            Formatted forensic report
        """
        report = self.evidence_service.generate_forensic_report(
            evidence_ids=evidence_ids,
            case_number=case_number,
            investigator=investigator,
        )

        logger.info(f"Case report generated: {case_number}")
        return report

    async def generate_pursuit_package(
        self,
        target_ip: str,
        case_number: str,
        investigator: str = "Guardian Hunter",
    ) -> ForensicPursuitPackage:
        """
        Generate a law enforcement referral package.

        Args:
            target_ip: IP address to investigate
            case_number: Case/reference number
            investigator: Name of investigator

        Returns:
            Complete forensic pursuit package
        """
        # Run investigation
        threat_result = await self.hunter_service.investigate_ip(
            ip_address=target_ip,
        )

        # Generate package
        package = await self.hunter_service.generate_forensic_package(
            investigation_result=threat_result,
            case_number=case_number,
            investigator=investigator,
        )

        return package


def log_security_event(
    sensor_id: str,
    event_type: str,
    description: str,
    severity: str = "INFO",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Log a security event to the system log.

    Args:
        sensor_id: ID of the sensor detecting the event
        event_type: Type of event
        description: Human-readable description
        severity: Event severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        metadata: Additional event metadata

    Returns:
        Log entry dictionary
    """
    import uuid

    log_entry = {
        "log_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sensor_id": sensor_id,
        "event_type": event_type,
        "description": description,
        "severity": severity,
        "metadata": metadata or {},
    }

    log_func = getattr(logger, severity.lower(), logger.info)
    log_func(f"[{event_type}] {description}")

    return log_entry


def create_attack_report(
    target_ip: str,
    attack_type: str,
    timeline: List[Dict[str, Any]],
    iocs: List[str],
    case_number: str,
) -> Dict[str, Any]:
    """
    Create a structured attack report.

    Args:
        target_ip: Targeted IP address
        attack_type: Type of attack
        timeline: Chronological list of events
        iocs: List of indicators of compromise
        case_number: Case/reference number

    Returns:
        Structured attack report
    """
    report = {
        "report_id": f"ATTACK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "case_number": case_number,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "target": {
            "ip": target_ip,
        },
        "attack_type": attack_type,
        "timeline": timeline,
        "indicators_of_compromise": iocs,
        "summary": {
            "total_events": len(timeline),
            "ioc_count": len(iocs),
            "severity": "HIGH" if len(timeline) > 10 else "MEDIUM",
        },
    }

    logger.info(f"Attack report created: {report['report_id']}")
    return report


def get_guardian_service(
    sensor_id: str = "guardian-primary",
    collector_node: str = "guardian-node-01",
    evidence_storage: str = "/var/lib/guardian/evidence",
) -> GuardianService:
    """
    Get an instance of the Guardian service.

    Args:
        sensor_id: Unique sensor identifier
        collector_node: Collection node name
        evidence_storage: Evidence storage path

    Returns:
        Configured GuardianService instance
    """
    return GuardianService(
        sensor_id=sensor_id,
        collector_node=collector_node,
        evidence_storage=evidence_storage,
    )
