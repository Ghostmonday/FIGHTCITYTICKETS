"""
Guardian Hunter OSINT Service
==============================

Active threat intelligence and attribution engine.
Performs high-speed OSINT queries to identify and track attackers.
Creates forensic pursuit packages for law enforcement referral.

Key Features:
- IP geolocation and ASN mapping
- Threat intelligence API integration (VirusTotal, AbuseIPDB, Shodan)
- Infrastructure fingerprinting (VPN, Tor, proxy detection)
- Automatic forensic report generation
- Integration with Evidence Hashing for legal admissibility

Author: Neural Draft LLC
Version: 1.0.0
Compliance: Civil Shield v1, CFAA Attribution Standards
"""

import asyncio
import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - GUARDIAN-HUNTER - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Classification of threat severity."""

    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InfrastructureType(Enum):
    """Type of network infrastructure detected."""

    RESIDENTIAL = "residential"
    BUSINESS = "business"
    DATA_CENTER = "data_center"
    VPN = "vpn"
    TOR_EXIT = "tor_exit"
    PROXY = "proxy"
    CLOUD = "cloud"
    UNKNOWN = "unknown"


@dataclass
class GeolocationData:
    """IP geolocation information."""

    ip_address: str
    country_code: str
    country_name: str
    region: str
    city: str
    latitude: float
    longitude: float
    isp: str
    asn: str
    asn_name: str
    is_vpn: bool = False
    is_tor: bool = False
    is_proxy: bool = False
    is_datacenter: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ThreatIntelResult:
    """Complete threat intelligence result."""

    evidence_id: str
    target_ip: str
    query_timestamp: str
    threat_score: float
    threat_level: ThreatLevel
    is_malicious: bool

    # Geolocation
    geolocation: Optional[GeolocationData] = None

    # ASN Info
    asn_info: Dict[str, str] = field(default_factory=dict)

    # Threat scores
    abuse_ipdb_score: Optional[int] = None
    virustotal_positives: Optional[int] = None
    shodan_hostnames: List[str] = field(default_factory=list)

    # Infrastructure analysis
    infrastructure_type: InfrastructureType = InfrastructureType.UNKNOWN
    is_cloud_provider: bool = False
    is_vpn_service: bool = False
    is_tor_exit: bool = False

    # Fingerprinting
    ssl_fingerprint: Optional[str] = None
    user_agent: Optional[str] = None
    http_headers: Dict[str, str] = field(default_factory=dict)

    # Raw API responses (for evidence)
    raw_responses: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ForensicPursuitPackage:
    """Complete forensic package for law enforcement."""

    package_id: str
    case_number: str
    generated_at: str
    target_ip: str

    # Evidence summary
    evidence_ids: List[str]
    total_evidence_count: int

    # Threat summary
    threat_score: float
    threat_level: ThreatLevel
    is_malicious: bool

    # Attribution
    likely_identity: str
    location: str
    isp: str

    # Technical details
    attack_vector: str
    infrastructure_type: str
    indicators_of_compromise: List[str]

    # Recommendations
    law_enforcement_referral: bool = False
    recommended_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HunterConfig:
    """Configuration for Hunter OSINT service."""

    # API Keys (set via environment variables)
    virustotal_api_key: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    abuseipdb_api_key: str = os.getenv("ABUSEIPDB_API_KEY", "")
    shodan_api_key: str = os.getenv("SHODAN_API_KEY", "")
    ipinfo_token: str = os.getenv("IPINFO_TOKEN", "")

    # Rate limiting
    virustotal_rate_limit: int = 4  # requests per minute (free tier)
    abuseipdb_rate_limit: int = 100  # requests per day (free tier)
    shodan_rate_limit: int = 1  # requests per second

    # Thresholds
    malicious_threshold: int = 50  # AbuseIPDB score threshold
    virus_total_threshold: int = 3  # Positive detections threshold

    # Timeout
    request_timeout: float = 30.0


class IPIntelligenceClient:
    """Base client for IP intelligence services."""

    def __init__(self, config: HunterConfig):
        self.config = config
        self.http_client = httpx.AsyncClient(
            timeout=config.request_timeout, follow_redirects=True
        )

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class AbuseIPDBClient(IPIntelligenceClient):
    """Client for AbuseIPDB threat intelligence."""

    BASE_URL = "https://api.abuseipdb.com/api/v2"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    async def check_ip(
        self, ip_address: str, max_days_age: int = 30
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Query AbuseIPDB for IP reputation.

        Args:
            ip_address: IP address to check
            max_days_age: Consider reports from last N days

        Returns:
            Tuple of (abuse_score, raw_response)
        """
        if not self.config.abuseipdb_api_key:
            logger.warning("AbuseIPDB API key not configured")
            return 0, {}

        try:
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": max_days_age,
                "verbose": True,
            }
            headers = {
                "Key": self.config.abuseipdb_api_key,
                "Accept": "application/json",
            }

            response = await self.http_client.get(
                f"{self.BASE_URL}/check", params=params, headers=headers
            )
            response.raise_for_status()
            data = response.json()

            score = data.get("data", {}).get("abuseConfidenceScore", 0)
            return score, data

        except Exception as e:
            logger.error(f"AbuseIPDB query failed for {ip_address}: {e}")
            return 0, {}


class VirusTotalClient(IPIntelligenceClient):
    """Client for VirusTotal threat intelligence."""

    BASE_URL = "https://www.virustotal.com/api/v3"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2))
    async def check_ip(self, ip_address: str) -> Tuple[int, Dict[str, Any]]:
        """
        Query VirusTotal for IP reputation.

        Args:
            ip_address: IP address to check

        Returns:
            Tuple of (positive_count, raw_response)
        """
        if not self.config.virustotal_api_key:
            logger.warning("VirusTotal API key not configured")
            return 0, {}

        try:
            headers = {"x-apikey": self.config.virustotal_api_key}

            response = await self.http_client.get(
                f"{self.BASE_URL}/ip_addresses/{ip_address}", headers=headers
            )
            response.raise_for_status()
            data = response.json()

            attributes = data.get("data", {}).get("attributes", {})
            last_analysis_stats = attributes.get("last_analysis_stats", {})
            positives = last_analysis_stats.get("malicious", 0)

            return positives, data

        except Exception as e:
            logger.error(f"VirusTotal query failed for {ip_address}: {e}")
            return 0, {}


class ShodanClient(IPIntelligenceClient):
    """Client for Shodan threat intelligence."""

    BASE_URL = "https://api.shodan.io"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    async def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Query Shodan for IP information.

        Args:
            ip_address: IP address to check

        Returns:
            Shodan response data
        """
        if not self.config.shodan_api_key:
            logger.warning("Shodan API key not configured")
            return {}

        try:
            params = {"key": self.config.shodan_api_key}

            response = await self.http_client.get(
                f"{self.BASE_URL}/shodan/host/{ip_address}", params=params
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"No Shodan data for {ip_address}")
                return {}
            raise
        except Exception as e:
            logger.error(f"Shodan query failed for {ip_address}: {e}")
            return {}


class IPInfoClient(IPIntelligenceClient):
    """Client for IP geolocation."""

    BASE_URL = "https://ipinfo.io"

    async def geolocate(self, ip_address: str) -> Dict[str, Any]:
        """
        Get geolocation data for IP address.

        Args:
            ip_address: IP address to geolocate

        Returns:
            Geolocation data dictionary
        """
        try:
            headers = {}
            if self.config.ipinfo_token:
                headers["Authorization"] = f"Bearer {self.config.ipinfo_token}"

            response = await self.http_client.get(
                f"{self.BASE_URL}/{ip_address}/json", headers=headers
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"IPInfo query failed for {ip_address}: {e}")
            return {}


class HunterService:
    """
    Main Hunter OSINT service.

    Coordinates threat intelligence queries across multiple APIs
    to build a complete picture of suspicious activity.
    """

    def __init__(self, config: Optional[HunterConfig] = None):
        """
        Initialize Hunter service.

        Args:
            config: Hunter configuration (uses defaults if not provided)
        """
        self.config = config or HunterConfig()

        # Initialize API clients
        self.abuse_client = AbuseIPDBClient(self.config)
        self.virustotal_client = VirusTotalClient(self.config)
        self.shodan_client = ShodanClient(self.config)
        self.ipinfo_client = IPInfoClient(self.config)

        logger.info("HunterService initialized")

    async def close(self):
        """Close all HTTP clients."""
        await asyncio.gather(
            self.abuse_client.close(),
            self.virustotal_client.close(),
            self.shodan_client.close(),
            self.ipinfo_client.close(),
            return_exceptions=True,
        )

    async def investigate_ip(
        self,
        ip_address: str,
        user_agent: Optional[str] = None,
        ssl_fingerprint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        evidence_id: Optional[str] = None,
    ) -> ThreatIntelResult:
        """
        Perform comprehensive investigation of an IP address.

        Args:
            ip_address: Target IP to investigate
            user_agent: Optional User-Agent from request
            ssl_fingerprint: Optional SSL/TLS fingerprint
            headers: Optional HTTP headers from request
            evidence_id: Optional evidence ID for correlation

        Returns:
            Complete threat intelligence result
        """
        evidence_id = evidence_id or f"HUNT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        query_timestamp = datetime.utcnow().isoformat() + "Z"

        logger.info(f"Starting investigation of {ip_address} (evidence: {evidence_id})")

        # Run API queries concurrently
        tasks = [
            self.abuse_client.check_ip(ip_address),
            self.virustotal_client.check_ip(ip_address),
            self.shodan_client.check_ip(ip_address),
            self.ipinfo_client.geolocate(ip_address),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse results
        abuse_score, abuse_data = (
            results[0] if isinstance(results[0], tuple) else (0, {})
        )
        vt_positives, vt_data = results[1] if isinstance(results[1], tuple) else (0, {})
        shodan_data = results[2] if isinstance(results[2], dict) else {}
        geo_data = results[3] if isinstance(results[3], dict) else {}

        # Calculate threat score (0-100)
        threat_score = self._calculate_threat_score(
            abuse_score, vt_positives, shodan_data
        )

        # Determine threat level
        threat_level = self._determine_threat_level(threat_score)
        is_malicious = threat_score >= self.config.malicious_threshold

        # Analyze infrastructure
        infrastructure_type = self._analyze_infrastructure(
            geo_data, shodan_data, abuse_data
        )

        # Parse geolocation
        geolocation = self._parse_geolocation(geo_data, ip_address)

        # Extract ASN info
        asn_info = self._extract_asn_info(geo_data, shodan_data)

        # Parse Shodan data
        shodan_hostnames = shodan_data.get("hostnames", [])

        # Build result
        result = ThreatIntelResult(
            evidence_id=evidence_id,
            target_ip=ip_address,
            query_timestamp=query_timestamp,
            threat_score=threat_score,
            threat_level=threat_level,
            is_malicious=is_malicious,
            geolocation=geolocation,
            asn_info=asn_info,
            abuse_ipdb_score=abuse_score if abuse_score > 0 else None,
            virustotal_positives=vt_positives if vt_positives > 0 else None,
            shodan_hostnames=shodan_hostnames,
            infrastructure_type=infrastructure_type,
            is_cloud_provider=infrastructure_type == InfrastructureType.CLOUD,
            is_vpn_service=infrastructure_type == InfrastructureType.VPN,
            is_tor_exit=infrastructure_type == InfrastructureType.TOR_EXIT,
            ssl_fingerprint=ssl_fingerprint,
            user_agent=user_agent,
            http_headers=headers or {},
            raw_responses={
                "abuseipdb": abuse_data,
                "virustotal": vt_data,
                "shodan": shodan_data,
                "ipinfo": geo_data,
            },
        )

        logger.info(
            f"Investigation complete: {ip_address} | "
            f"Score: {threat_score} | Level: {threat_level.value}"
        )

        return result

    def _calculate_threat_score(
        self, abuse_score: int, vt_positives: int, shodan_data: Dict[str, Any]
    ) -> float:
        """Calculate composite threat score (0-100)."""
        score = 0.0

        # AbuseIPDB score (max 30 points)
        score += min(abuse_score * 0.3, 30)

        # VirusTotal positives (max 30 points)
        score += min(vt_positives * 10, 30)

        # Shodan flags (max 20 points)
        if shodan_data:
            # Check for suspicious ports
            ports = shodan_data.get("ports", [])
            suspicious_ports = [22, 23, 445, 3389, 5900, 8080, 8443]
            if any(p in ports for p in suspicious_ports):
                score += 10

            # Check for vulns
            vulns = shodan_data.get("vulns", {})
            if vulns:
                score += min(len(vulns) * 2, 10)

        # Additional indicators (max 20 points)
        # These would be enhanced with more logic

        return min(score, 100)

    def _determine_threat_level(self, score: float) -> ThreatLevel:
        """Determine threat level from score."""
        if score == 0:
            return ThreatLevel.BENIGN
        elif score < 20:
            return ThreatLevel.SUSPICIOUS
        elif score < 40:
            return ThreatLevel.LOW
        elif score < 60:
            return ThreatLevel.MEDIUM
        elif score < 80:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL

    def _analyze_infrastructure(
        self,
        geo_data: Dict[str, Any],
        shodan_data: Dict[str, Any],
        abuse_data: Dict[str, Any],
    ) -> InfrastructureType:
        """Analyze detected infrastructure type."""
        # Check Shodan first (most reliable for infrastructure)
        if shodan_data:
            # Check for cloud providers
            isp = geo_data.get("org", "").lower()
            cloud_providers = [
                "amazon",
                "google",
                "microsoft",
                "azure",
                "digitalocean",
                "linode",
            ]
            if any(cp in isp for cp in cloud_providers):
                return InfrastructureType.CLOUD

            # Check for VPN services
            vpn_providers = [
                "nordvpn",
                "expressvpn",
                "surfshark",
                "mullvad",
                "ipvanish",
            ]
            if any(vp in isp for vp in vpn_providers):
                return InfrastructureType.VPN

            # Check for hosting/data center
            hosting_indicators = ["hosting", "dedicated", "server", "colocation"]
            if any(ind in isp for ind in hosting_indicators):
                return InfrastructureType.DATA_CENTER

        # Check AbuseIPDB for VPN/Tor indicators
        if abuse_data:
            data = abuse_data.get("data", {})
            if data.get("isTor"):
                return InfrastructureType.TOR_EXIT
            if data.get("isVPN"):
                return InfrastructureType.VPN
            if data.get("isProxy"):
                return InfrastructureType.PROXY

        # Check IP ranges
        ip = geo_data.get("ip", "")
        if (
            ip.startswith("10.")
            or ip.startswith("192.168.")
            or ip.startswith("172.16.")
        ):
            return InfrastructureType.RESIDENTIAL

        return InfrastructureType.BUSINESS

    def _parse_geolocation(
        self, geo_data: Dict[str, Any], ip_address: str
    ) -> Optional[GeolocationData]:
        """Parse geolocation data from IPInfo response."""
        if not geo_data:
            return None

        # Parse location
        loc = geo_data.get("loc", "0,0").split(",")
        lat = float(loc[0]) if len(loc) > 0 else 0.0
        lon = float(loc[1]) if len(loc) > 1 else 0.0

        # Parse org/ISP
        org = geo_data.get("org", "")
        asn = ""
        if "AS" in org:
            asn_match = re.search(r"AS(\d+)", org)
            if asn_match:
                asn = f"AS{asn_match.group(1)}"

        return GeolocationData(
            ip_address=ip_address,
            country_code=geo_data.get("country", ""),
            country_name=geo_data.get("country_name", ""),
            region=geo_data.get("region", ""),
            city=geo_data.get("city", ""),
            latitude=lat,
            longitude=lon,
            isp=org,
            asn=asn,
            asn_name=org,
            is_vpn=geo_data.get("vpn", False),
            is_tor=geo_data.get("tor", False),
            is_proxy=geo_data.get("proxy", False),
            is_datacenter=geo_data.get("hosting", False),
        )

    def _extract_asn_info(
        self, geo_data: Dict[str, Any], shodan_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Extract ASN information from responses."""
        info = {}

        # From IPInfo
        if geo_data:
            if "org" in geo_data:
                info["isp"] = geo_data["org"]
            if "asn" in geo_data:
                info["asn"] = geo_data["asn"]

        # From Shodan (more detailed)
        if shodan_data:
            if "asn" in shodan_data:
                info["asn"] = shodan_data["asn"]
            if "isp" in shodan_data:
                info["isp"] = shodan_data["isp"]

        return info

    def generate_iocs(self, result: ThreatIntelResult) -> List[str]:
        """
        Generate Indicators of Compromise from investigation result.

        Args:
            result: Threat intelligence result

        Returns:
            List of IOCs
        """
        iocs = []

        # IP address
        iocs.append(f"IP: {result.target_ip}")

        # Geolocation
        if result.geolocation:
            geo = result.geolocation
            iocs.append(f"Location: {geo.city}, {geo.country_name}")
            iocs.append(f"ISP: {geo.isp}")
            iocs.append(f"ASN: {geo.asn}")

        # Threat scores
        if result.abuse_ipdb_score is not None:
            iocs.append(f"AbuseIPDB Score: {result.abuse_ipdb_score}/100")

        if result.virustotal_positives is not None:
            iocs.append(f"VirusTotal Detections: {result.virustotal_positives}")

        # Infrastructure
        iocs.append(f"Infrastructure: {result.infrastructure_type.value}")

        # SSL fingerprint
        if result.ssl_fingerprint:
            iocs.append(f"SSL Fingerprint: {result.ssl_fingerprint[:32]}...")

        # User agent
        if result.user_agent:
            iocs.append(f"User-Agent: {result.user_agent}")

        return iocs

    async def generate_forensic_package(
        self,
        investigation_result: ThreatIntelResult,
        case_number: str,
        investigator: str = "Guardian Hunter",
        related_evidence_ids: Optional[List[str]] = None,
    ) -> ForensicPursuitPackage:
        """
        Generate complete forensic pursuit package for law enforcement.

        Args:
            investigation_result: Result from investigate_ip()
            case_number: Case/reference number
            investigator: Name of investigator
            related_evidence_ids: Related evidence IDs

        Returns:
            Complete forensic pursuit package
        """
        package_id = f"PKG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{investigation_result.target_ip.replace('.', '-')}"

        # Generate IOCs
        iocs = self.generate_iocs(investigation_result)

        # Determine likely identity
        likely_identity = "Unknown"
        if investigation_result.geolocation:
            geo = investigation_result.geolocation
            likely_identity = f"{geo.city}, {geo.country_name} ({geo.isp})"

        # Determine location
        location = "Unknown"
        if investigation_result.geolocation:
            geo = investigation_result.geolocation
            location = f"{geo.city}, {geo.region}, {geo.country_name}"

        # Determine ISP
        isp = (
            investigation_result.geolocation.isp
            if investigation_result.geolocation
            else "Unknown"
        )

        # Attack vector inference
        attack_vector = self._infer_attack_vector(investigation_result)

        # Recommendations
        recommendations = self._generate_recommendations(investigation_result)

        # Law enforcement referral decision
        law_enforcement = (
            investigation_result.threat_level
            in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            and investigation_result.is_malicious
        )

        package = ForensicPursuitPackage(
            package_id=package_id,
            case_number=case_number,
            generated_at=datetime.utcnow().isoformat() + "Z",
            target_ip=investigation_result.target_ip,
            evidence_ids=related_evidence_ids or [investigation_result.evidence_id],
            total_evidence_count=len(related_evidence_ids) + 1
            if related_evidence_ids
            else 1,
            threat_score=investigation_result.threat_score,
            threat_level=investigation_result.threat_level,
            is_malicious=investigation_result.is_malicious,
            likely_identity=likely_identity,
            location=location,
            isp=isp,
            attack_vector=attack_vector,
            infrastructure_type=investigation_result.infrastructure_type.value,
            indicators_of_compromise=iocs,
            law_enforcement_referral=law_enforcement,
            recommended_actions=recommendations,
        )

        logger.info(f"Forensic package generated: {package_id}")

        return package

    def _infer_attack_vector(self, result: ThreatIntelResult) -> str:
        """Infer likely attack vector from investigation results."""
        # Check for common attack patterns
        if result.infrastructure_type == InfrastructureType.TOR_EXIT:
            return "Anonymized (Tor) - Possible reconnaissance or evasion"

        if result.infrastructure_type == InfrastructureType.VPN:
            return "Anonymized (VPN) - Possible evasion tactic"

        if result.abuse_ipdb_score and result.abuse_ipdb_score > 50:
            return "Brute force / Credential stuffing (high abuse confidence)"

        if result.virustotal_positives and result.virustotal_positives > 0:
            return "Malicious infrastructure - Possible C2 or malware"

        if result.shodan_hostnames:
            return "Infrastructure mapping - Possible port scanning"

        return "Unknown - Requires additional forensic analysis"

    def _generate_recommendations(self, result: ThreatIntelResult) -> List[str]:
        """Generate recommended actions based on investigation."""
        recommendations = []

        if result.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            recommendations.append("IMMEDIATE: Block IP at firewall/edge")
            recommendations.append("IMMEDIATE: Preserve all logs and evidence")

        if result.infrastructure_type == InfrastructureType.TOR_EXIT:
            recommendations.append("Monitor for Tor bridge attacks")
            recommendations.append("Consider implementing Tor exit node blocking")

        if result.abuse_ipdb_score and result.abuse_ipdb_score > 30:
            recommendations.append("Report IP to AbuseIPDB if not already listed")

        if result.virustotal_positives and result.virustotal_positives > 0:
            recommendations.append(
                "Submit samples to antivirus vendors if malware detected"
            )

        if result.is_malicious:
            recommendations.append("FILE REPORT: FBI IC3 (www.ic3.gov)")
            recommendations.append("FILE REPORT: Local law enforcement cyber unit")
            recommendations.append("PRESERVE EVIDENCE: Do not modify logs or systems")

        recommendations.append("CONTINUE MONITORING: Watch for related activity")

        return recommendations


async def demo():
    """Demo usage of Hunter service."""
    service = HunterService()

    try:
        # Investigate a suspicious IP (replace with actual suspicious IP)
        result = await service.investigate_ip(
            ip_address="1.2.3.4",
            user_agent="Mozilla/5.0 (compatible; EvilScanner/1.0)",
            ssl_fingerprint="sha256:abc123...",
            headers={"X-Forwarded-For": "1.2.3.4"},
        )

        print(f"Investigation Result for {result.target_ip}")
        print(f"Threat Score: {result.threat_score}/100")
        print(f"Threat Level: {result.threat_level.value}")
        print(f"Malicious: {result.is_malicious}")

        if result.geolocation:
            print(
                f"Location: {result.geolocation.city}, {result.geolocation.country_name}"
            )
            print(f"ISP: {result.geolocation.isp}")

        print(f"Infrastructure: {result.infrastructure_type.value}")

        # Generate forensic package
        package = await service.generate_forensic_package(
            investigation_result=result,
            case_number="CASE-2024-001",
            investigator="Guardian Hunter",
        )

        print(f"\nForensic Package: {package.package_id}")
        print(f"Law Enforcement Referral: {package.law_enforcement_referral}")

    finally:
        await service.close()


def get_hunter_service() -> HunterService:
    """Get an instance of the Hunter service."""
    return HunterService()


if __name__ == "__main__":
    asyncio.run(demo())
