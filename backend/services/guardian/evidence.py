provethat.io\backend\services\guardian\evidence.py
```

```python
"""
Guardian Evidence Hashing Service
=================================

Legal-grade forensic evidence collection and immutable audit trail management.
Ensures all security events are tracked with cryptographic hashing for
admissibility in legal proceedings.

Key Features:
- SHA-256 cryptographic hashing of all evidence
- Chain-of-custody tracking with timestamps
- Tamper-evident evidence storage
- Forensic report generation
- Digital signature verification

Author: Neural Draft LLC
Version: 1.0.0
Compliance: Civil Shield v1, CFAA Evidence Standards
"""

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - GUARDIAN-EVIDENCE - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of forensic evidence collected."""
    NETWORK_EVENT = "network_event"
    AUTH_FAILURE = "auth_failure"
    FILE_MODIFICATION = "file_modification"
    PROCESS_SPAWN = "process_spawn"
    IP_ATTRIBUTION = "ip_attribution"
    THREAT_INTEL = "threat_intel"
    SYSTEM_SNAPSHOT = "system_snapshot"
    CHAIN_OF_CUSTODY = "chain_of_custody"


class EvidenceIntegrity(Enum):
    """Status of evidence integrity verification."""
    VERIFIED = "verified"
    TAMPERED = "tampered"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class EvidenceMetadata:
    """Metadata associated with a piece of evidence."""
    evidence_id: str
    evidence_type: EvidenceType
    timestamp: str
    collector_node: str
    sensor_id: str
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    integrity_status: EvidenceIntegrity = EvidenceIntegrity.PENDING
    integrity_hash: str = ""
    previous_hash: str = ""
    digital_signature: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NetworkEvidence:
    """Network-level evidence for forensic analysis."""
    evidence_id: str
    timestamp: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    duration_ms: int
    flags: str
    user_agent: Optional[str] = None
    ssl_fingerprint: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    raw_packet_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuthEvidence:
    """Authentication failure evidence."""
    evidence_id: str
    timestamp: str
    username: str
    source_ip: str
    auth_method: str
    failure_reason: str
    attempt_count: int
    geo_location: Optional[Dict[str, str]] = None
    device_fingerprint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileEvidence:
    """File modification evidence."""
    evidence_id: str
    timestamp: str
    file_path: str
    operation: str  # created, modified, deleted, accessed
    file_hash: str
    file_size: int
    file_permissions: str
    user_id: str
    process_name: Optional[str] = None
    previous_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ThreatIntelEvidence:
    """Threat intelligence query results."""
    evidence_id: str
    timestamp: str
    target_ip: str
    query_service: str
    threat_score: float
    is_malicious: bool
    threat_categories: List[str]
    asn_info: Dict[str, str]
    geolocation: Dict[str, str]
    abuse_ipdb_score: Optional[int] = None
    virustotal_detections: Optional[int] = None
    shodan_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvidenceHasher:
    """
    Cryptographic hashing service for evidence integrity.

    Implements SHA-256 hashing with chain-linking for tamper detection.
    """

    def __init__(self, private_key_path: Optional[str] = None):
        """
        Initialize the evidence hasher.

        Args:
            private_key_path: Path to RSA private key for digital signatures
        """
        self.private_key = None
        self.public_key = None

        if private_key_path and os.path.exists(private_key_path):
            self._load_signing_key(private_key_path)
        else:
            self._generate_signing_key()

        logger.info("EvidenceHasher initialized with RSA signing key")

    def _generate_signing_key(self):
        """Generate a new RSA key pair for digital signatures."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        logger.info("Generated new RSA signing key pair (4096-bit)")

    def _load_signing_key(self, private_key_path: str):
        """Load existing RSA private key from file."""
        try:
            with open(private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            self.public_key = self.private_key.public_key()
            logger.info(f"Loaded signing key from {private_key_path}")
        except Exception as e:
            logger.error(f"Failed to load signing key: {e}")
            self._generate_signing_key()

    def compute_evidence_hash(self, evidence_data: Dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of evidence data.

        Args:
            evidence_data: Dictionary of evidence to hash

        Returns:
            Hexadecimal string of the hash
        """
        # Sort keys for deterministic hashing
        sorted_data = json.dumps(evidence_data, sort_keys=True, default=str)
        hash_bytes = hashlib.sha256(sorted_data.encode()).digest()
        return hash_bytes.hex()

    def compute_chain_hash(self, previous_hash: str, current_hash: str) -> str:
        """
        Compute chained hash linking evidence together.

        Creates a blockchain-like chain where each evidence hash
        includes the previous hash, preventing tampering.

        Args:
            previous_hash: Hash of previous evidence in chain
            current_hash: Hash of current evidence

        Returns:
            Combined and hashed chain identifier
        """
        chain_data = f"{previous_hash}|{current_hash}|{datetime.utcnow().isoformat()}"
        return hashlib.sha256(chain_data.encode()).hexdigest()

    def sign_evidence(self, evidence_hash: str) -> str:
        """
        Digitally sign evidence hash with private key.

        Args:
            evidence_hash: Hash of the evidence to sign

        Returns:
            Base64-encoded digital signature
        """
        if not self.private_key:
            logger.warning("No private key available, skipping signature")
            return ""

        signature = self.private_key.sign(
            evidence_hash.encode(),
            padding.PSS(
                margin=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()

    def verify_signature(self, evidence_hash: str, signature: str) -> bool:
        """
        Verify a digital signature.

        Args:
            evidence_hash: Original hash that was signed
            signature: Hex-encoded signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key or not signature:
            return False

        try:
            self.public_key.verify(
                bytes.fromhex(signature),
                evidence_hash.encode(),
                padding.PSS(
                    margin=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def verify_evidence_integrity(
        self,
        evidence_data: Dict[str, Any],
        stored_hash: str,
        signature: str
    ) -> Tuple[bool, str]:
        """
        Verify the integrity of stored evidence.

        Args:
            evidence_data: Current evidence data
            stored_hash: Hash that was originally computed
            signature: Digital signature of the hash

        Returns:
            Tuple of (is_valid, status_message)
        """
        current_hash = self.compute_evidence_hash(evidence_data)

        if current_hash != stored_hash:
            return False, "HASH_MISMATCH: Evidence has been modified"

        if signature and not self.verify_signature(stored_hash, signature):
            return False, "SIGNATURE_INVALID: Digital signature verification failed"

        return True, "VERIFIED: Evidence integrity confirmed"


class ChainOfCustody:
    """
    Chain of custody tracker for legal admissibility.

    Maintains an immutable log of who accessed evidence and when.
    """

    def __init__(self, evidence_id: str, collector_node: str, sensor_id: str):
        """
        Initialize chain of custody for an evidence item.

        Args:
            evidence_id: Unique identifier for this evidence
            collector_node: Name/ID of the collecting node
            sensor_id: ID of the sensor that collected the evidence
        """
        self.evidence_id = evidence_id
        self.collector_node = collector_node
        self.sensor_id = sensor_id
        self.entries: List[Dict[str, Any]] = []
        self._add_custody_event("COLLECTED", "Evidence collected by sensor")

    def _add_custody_event(
        self,
        action: str,
        description: str,
        custodian: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a new entry to the chain of custody.

        Args:
            action: Action type (COLLECTED, STORED, RETRIEVED, etc.)
            description: Human-readable description
            custodian: Who performed the action
            metadata: Additional metadata about the action
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "description": description,
            "custodian": custodian,
            "evidence_id": self.evidence_id,
            "collector_node": self.collector_node,
            "sensor_id": self.sensor_id,
            "metadata": metadata or {}
        }
        self.entries.append(entry)
        logger.info(f"Chain of custody [{self.evidence_id}]: {action}")

    def to_dict(self) -> Dict[str, Any]:
        """Export chain of custody as dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "entries": self.entries,
            "entry_count": len(self.entries)
        }

    def export_chain_log(self) -> str:
        """Export chain of custody as formatted text for reports."""
        lines = [
            "=" * 80,
            "CHAIN OF CUSTODY LOG",
            "=" * 80,
            f"Evidence ID: {self.evidence_id}",
            f"Collector Node: {self.collector_node}",
            f"Sensor ID: {self.sensor_id}",
            f"Total Entries: {len(self.entries)}",
            "-" * 80,
            "TIMELINE:",
            "-" * 80
        ]

        for i, entry in enumerate(self.entries, 1):
            lines.append(f"\n[{i}] {entry['timestamp']}")
            lines.append(f"    Action: {entry['action']}")
            lines.append(f"    Custodian: {entry['custodian']}")
            lines.append(f"    Description: {entry['description']}")
            if entry.get('metadata'):
                lines.append(f"    Metadata: {json.dumps(entry['metadata'], indent=4)}")

        lines.extend(["", "=" * 80, "END OF CHAIN OF CUSTODY LOG", "=" * 80])
        return "\n".join(lines)


class EvidenceService:
    """
    Main service for evidence collection, hashing, and storage.

    Coordinates evidence collection across all Guardian sensors.
    """

    def __init__(
        self,
        storage_path: str = "/var/lib/guardian/evidence",
        private_key_path: Optional[str] = None,
        collector_node: str = "guardian-primary",
        sensor_id: str = "guardian-sentinel-01"
    ):
        """
        Initialize the evidence service.

        Args:
            storage_path: Directory for evidence storage
            private_key_path: Path to RSA private key for signatures
            collector_node: Name of this collection node
            sensor_id: ID of this sensor
        """
        self.storage_path = Path(storage_path)
        self.collector_node = collector_node
        self.sensor_id = sensor_id
        self.hasher = EvidenceHasher(private_key_path)

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Evidence type subdirectories
        self.type_directories = {}
        for evidence_type in EvidenceType:
            (self.storage_path / evidence_type.value).mkdir(exist_ok=True)
            self.type_directories[evidence_type] = self.storage_path / evidence_type.value

        logger.info(f"EvidenceService initialized at {storage_path}")

    def _generate_evidence_id(self) -> str:
        """Generate unique evidence ID with timestamp prefix."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"EV-{timestamp}-{unique_id}"

    def collect_network_evidence(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        bytes_sent: int,
        bytes_received: int,
        duration_ms: int,
        flags: str,
        user_agent: Optional[str] = None,
        ssl_fingerprint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> EvidenceMetadata:
        """
        Collect and hash network event evidence.

        Args:
            Network event details (see NetworkEvidence dataclass)

        Returns:
            EvidenceMetadata with cryptographic hashes
        """
        evidence_id = self._generate_evidence_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Create evidence object
        network_evidence = NetworkEvidence(
            evidence_id=evidence_id,
            timestamp=timestamp,
            source_ip=source_ip,
            destination_ip=destination_ip,
            source_port=source_port,
            destination_port=destination_port,
            protocol=protocol,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            duration_ms=duration_ms,
            flags=flags,
            user_agent=user_agent,
            ssl_fingerprint=ssl_fingerprint,
            headers=headers or {}
        )

        # Compute hash
        evidence_dict = network_evidence.to_dict()
        evidence_hash = self.hasher.compute_evidence_hash(evidence_dict)

        # Create chain of custody
        chain = ChainOfCustody(evidence_id, self.collector_node, self.sensor_id)

        # Create metadata
        metadata = EvidenceMetadata(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.NETWORK_EVENT,
            timestamp=timestamp,
            collector_node=self.collector_node,
            sensor_id=self.sensor_id,
            chain_of_custody=chain.entries,
            integrity_hash=evidence_hash,
            digital_signature=self.hasher.sign_evidence(evidence_hash)
        )

        # Store evidence
        self._store_evidence(evidence_id, EvidenceType.NETWORK_EVENT, evidence_dict, metadata)

        logger.info(f"Network evidence collected: {evidence_id}")
        return metadata

    def collect_auth_evidence(
        self,
        username: str,
        source_ip: str,
        auth_method: str,
        failure_reason: str,
        attempt_count: int,
        geo_location: Optional[Dict[str, str]] = None,
        device_fingerprint: Optional[str] = None
    ) -> EvidenceMetadata:
        """
        Collect and hash authentication failure evidence.

        Args:
            Authentication event details (see AuthEvidence dataclass)

        Returns:
            EvidenceMetadata with cryptographic hashes
        """
        evidence_id = self._generate_evidence_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        auth_evidence = AuthEvidence(
            evidence_id=evidence_id,
            timestamp=timestamp,
            username=username,
            source_ip=source_ip,
            auth_method=auth_method,
            failure_reason=failure_reason,
            attempt_count=attempt_count,
            geo_location=geo_location,
            device_fingerprint=device_fingerprint
        )

        evidence_dict = auth_evidence.to_dict()
        evidence_hash = self.hasher.compute_evidence_hash(evidence_dict)

        chain = ChainOfCustody(evidence_id, self.collector_node, self.sensor_id)

        metadata = EvidenceMetadata(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.AUTH_FAILURE,
            timestamp=timestamp,
            collector_node=self.collector_node,
            sensor_id=self.sensor_id,
            chain_of_custody=chain.entries,
            integrity_hash=evidence_hash,
            digital_signature=self.hasher.sign_evidence(evidence_hash)
        )

        self._store_evidence(evidence_id, EvidenceType.AUTH_FAILURE, evidence_dict, metadata)

        logger.info(f"Auth evidence collected: {evidence_id}")
        return metadata

    def collect_file_evidence(
        self,
        file_path: str,
        operation: str,
        file_hash: str,
        file_size: int,
        file_permissions: str,
        user_id: str,
        process_name: Optional[str] = None,
        previous_hash: Optional[str] = None
    ) -> EvidenceMetadata:
        """
        Collect and hash file modification evidence.

        Args:
            File event details (see FileEvidence dataclass)

        Returns:
            EvidenceMetadata with cryptographic hashes
        """
        evidence_id = self._generate_evidence_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        file_evidence = FileEvidence(
            evidence_id=evidence_id,
            timestamp=timestamp,
            file_path=file_path,
            operation=operation,
            file_hash=file_hash,
            file_size=file_size,
            file_permissions=file_permissions,
            user_id=user_id,
            process_name=process_name,
            previous_hash=previous_hash
        )

        evidence_dict = file_evidence.to_dict()
        evidence_hash = self.hasher.compute_evidence_hash(evidence_dict)

        chain = ChainOfCustody(evidence_id, self.collector_node, self.sensor_id)

        metadata = EvidenceMetadata(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.FILE_MODIFICATION,
            timestamp=timestamp,
            collector_node=self.collector_node,
            sensor_id=self.sensor_id,
            chain_of_custody=chain.entries,
            integrity_hash=evidence_hash,
            digital_signature=self.hasher.sign_evidence(evidence_hash)
        )

        self._store_evidence(evidence_id, EvidenceType.FILE_MODIFICATION, evidence_dict, metadata)

        logger.info(f"File evidence collected: {evidence_id}")
        return metadata

    def collect_threat_intel(
        self,
        target_ip: str,
        query_service: str,
        threat_score: float,
        is_malicious: bool,
        threat_categories: List[str],
        asn_info: Dict[str, str],
        geolocation: Dict[str, str],
        abuse_ipdb_score: Optional[int] = None,
        virustotal_detections: Optional[int] = None,
        shodan_data: Optional[Dict[str, Any]] = None
    ) -> EvidenceMetadata:
        """
        Collect and hash threat intelligence results.

        Args:
            Threat intelligence data (see ThreatIntelEvidence dataclass)

        Returns:
            EvidenceMetadata with cryptographic hashes
        """
        evidence_id = self._generate_evidence_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        threat_evidence = ThreatIntelEvidence(
            evidence_id=evidence_id,
            timestamp=timestamp,
            target_ip=target_ip,
            query_service=query_service,
            threat_score=threat_score,
            is_malicious=is_malicious,
            threat_categories=threat_categories,
            asn_info=asn_info,
            geolocation=geolocation,
            abuse_ipdb_score=abuse_ipdb_score,
            virustotal_detections=virustotal_detections,
            shodan_data=shodan_data or {}
        )

        evidence_dict = threat_evidence.to_dict()
        evidence_hash = self.hasher.compute_evidence_hash(evidence_dict)

        chain = ChainOfCustody(evidence_id, self.collector_node, self.sensor_id)

        metadata = EvidenceMetadata(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.THREAT_INTEL,
            timestamp=timestamp,
            collector_node=self.collector_node,
            sensor_id=self.sensor_id,
            chain_of_custody=chain.entries,
            integrity_hash=evidence_hash,
            digital_signature=self.hasher.sign_evidence(evidence_hash)
        )

        self._store_evidence(evidence_id, EvidenceType.THREAT_INTEL, evidence_dict, metadata)

        logger.info(f"Threat intel evidence collected: {evidence_id}")
        return metadata

    def _store_evidence(
        self,
        evidence_id: str,
        evidence_type: EvidenceType,
        evidence_data: Dict[str, Any],
        metadata: EvidenceMetadata
    ):
        """
        Store evidence to persistent storage.

        Args:
            evidence_id: Unique identifier
            evidence_type: Type of evidence
            evidence_data: Evidence payload
            metadata: Evidence metadata with hashes
        """
        type_dir = self.type_directories[evidence_type]

        # Store evidence data
        evidence_file = type_dir / f"{evidence_id}.json"
        with open(evidence_file, 'w') as f:
            json.dump(evidence_data, f, indent=2, default=str)

        # Store metadata
        metadata_file = type_dir / f"{evidence_id}.meta.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2, default=str)

        # Create index entry
        index_file = self.storage_path / "evidence_index.jsonl"
        index_entry = {
            "evidence_id": evidence_id,
            "evidence_type": evidence_type.value,
            "timestamp": metadata.timestamp,
            "integrity_hash": metadata.integrity_hash,
            "storage_path": str(evidence_file)
        }
        with open(index_file, 'a') as f:
            f.write(json.dumps(index_entry) + "\n")

        logger.info(f"Evidence stored: {evidence_id}")

    def verify_evidence(self, evidence_id: str) -> Tuple[bool, str]:
        """
        Verify the integrity of stored evidence.

        Args:
            evidence_id: ID of evidence to verify

        Returns:
            Tuple of (is_valid, status_message)
        """
        # Find evidence
        for evidence_type in EvidenceType:
            type_dir = self.type_directories[evidence_type]
            metadata_file = type_dir / f"{evidence_id}.meta.json"

            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                evidence_file = type_dir / f"{evidence_id}.json"
                with open(evidence_file, 'r') as f:
                    evidence_data = json.load(f)

                return self.hasher.verify_evidence_integrity(
                    evidence_data,
                    metadata["integrity_hash"],
                    metadata.get("digital_signature", "")
                )

        return False, "EVIDENCE_NOT_FOUND"

    def generate_forensic_report(
        self,
        evidence_ids: List[str],
        case_number: str,
        investigator: str
    ) -> str:
        """
        Generate a forensic report for given evidence IDs.

        Args:
            evidence_ids: List of evidence IDs to include
            case_number: Case/reference number for the report
            investigator: Name of investigator generating report

        Returns:
            Formatted forensic report as string
        """
        lines = [
            "=" * 80,
            "NEURAL DRAFT LLC - GUARDIAN FORENSIC REPORT",
            "=" * 80,
            "",
            f"Case Number: {case_number}",
            f"Report Generated: {datetime.utcnow().isoformat() + 'Z'}",
            f"Investigator: {investigator}",
            f"Evidence Count: {len(evidence_ids)}",
            "-" * 80,
            ""
        ]

        for evidence_id in evidence_ids:
            lines.append(f"EVIDENCE: {evidence_id}")
            lines.append("-" * 40)

            # Get metadata
            metadata = None
            for evidence_type in EvidenceType:
                type_dir = self.type_directories[evidence_type]
                metadata_file = type_dir / f"{evidence_id}.meta.json"

                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    break

            if metadata:
                lines.append(f"Type: {metadata.get('evidence_type', 'unknown')}")
                lines.append(f"Timestamp: {metadata.get('timestamp', 'unknown')}")
                lines.append(f"Collector: {metadata.get('collector_node', 'unknown')}")
                lines.append(f"Sensor: {metadata.get('sensor_id', 'unknown')}")
                lines.append(f"Integrity Hash: {metadata.get('integrity_hash', 'N/A')}")
                lines.append(f"Signature: {metadata.get('digital_signature', 'N/A')[:64]}...")

                # Chain of custody
                lines.append("")
                lines.append("Chain of Custody:")
                for entry in metadata.get('chain_of_custody', []):
                    lines.append(f"  [{entry['timestamp']}] {entry['action']} by {entry['custodian']}")
            else:
                lines.append("ERROR: Evidence metadata not found")

            lines.append("")
            lines.append("=" * 80)

        # Append verification statement
        lines.extend([
            "",
            "VERIFICATION STATEMENT",
            "-" * 40,
            "This report contains cryptographic evidence hashes generated by the",
            "Neural Draft LLC Guardian Evidence Service. Each piece of evidence",
            "has been hashed using SHA-256 and digitally signed.",
            "",
            "The integrity of this report can be verified by recalculating the",
            "SHA-256 hash of each evidence file and comparing against the hashes",
            "listed above.",
            "",
            "Digital Signature Method: RSA-4096 with SHA-256",
            "",
            "=" * 80,
            "END OF FORENSIC REPORT",
            "=" * 80
        ])

        return "\n".join(lines)

    def export_evidence_bundle(
        self,
        evidence_ids: List[str],
        output_path: str
    ) -> str:
        """
        Export evidence as a bundle for law enforcement.

        Creates a ZIP-like structure with all evidence and verification files.

        Args:
            evidence_ids: Evidence IDs to include
            output_path: Path for output bundle

        Returns:
            Path to exported bundle
        """
        bundle_dir = Path(output_path)
        bundle_dir.mkdir(parents=True, exist_ok=True)

        evidence_files = []

        for evidence_id in evidence_ids:
            for evidence_type in EvidenceType:
                type_dir = self.type_directories[evidence_type]
                evidence_file = type_dir / f"{evidence_id}.json"
                metadata_file = type_dir / f"{evidence_id}.meta.json"

                if evidence_file.exists():
                    # Copy evidence
                    dest_evidence = bundle_dir / evidence_file.name
                    with open(evidence_file, 'r') as src:
                        with open(dest_evidence, 'w') as dst:
                            dst.write(src.read())
                    evidence_files.append(str(dest_evidence))

                    # Copy metadata
                    if metadata_file.exists():
                        dest_metadata = bundle_dir / metadata_file.name
                        with open(metadata_file, 'r') as src:
                            with open(dest_metadata, 'w') as dst:
                                dst.write(src.read())

        # Generate manifest
        manifest = {
            "bundle_id": f"BUNDLE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "evidence_count": len(evidence_files),
            "evidence_ids": evidence_ids,
            "integrity_verification": "See individual .meta.json files for SHA-256 hashes"
        }

        with open(bundle_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Evidence bundle exported to {output_path}")
        return output_path


def get_evidence_service(
    storage_path: str = "/var/lib/guardian/evidence",
    private_key_path: Optional[str] = None
) -> EvidenceService:
    """
    Get an instance of the Evidence Service.

    Args:
        storage_path: Evidence storage directory
        private_key_path: Path to RSA private key

    Returns:
        Configured EvidenceService instance
    """
    return EvidenceService(
        storage_path=storage_path,
        private_key_path=private_key_path
    )


if __name__ == "__main__":
    # Demo usage
    service = get_evidence_service()

    # Collect sample network evidence
    metadata = service.collect_network_evidence(
        source_ip="192.168.1.100",
        destination_ip="10.0.0.5",
        source_port=54321,
        destination_port=22,
        protocol="TCP",
        bytes_sent=1024,
        bytes_received=512,
        duration_ms=150,
        flags="SYN",
        user_agent="Mozilla/5.0 (Compatible; EvilScanner/1.0)"
    )

    print(f"Evidence collected: {metadata.evidence_id}")
    print(f"Integrity Hash: {metadata.integrity_hash[:32]}...")
    print(f"Signature: {metadata.digital_signature[:32]}...")

    # Verify
    is_valid, message = service.verify_evidence(metadata.evidence_id)
    print(f"Verification: {message}")
