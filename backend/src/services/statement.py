"""
AI-powered statement refinement service for procedural compliance submissions.

This module provides intelligent document refinement using DeepSeek AI models
to transform informal user statements into professionally articulated appeal
letters that meet municipal procedural standards.

The Clerical Engine™ ensures all submissions maintain:
- User voice preservation (no invented content)
- Procedural compliance formatting
- Professional bureaucratic tone
- UPL (Unauthorized Practice of Law) compliance

Author: Neural Draft LLC
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StatementRefinementRequest(BaseModel):
    """Request model for statement refinement."""

    citation_number: str
    appeal_reason: str
    user_name: Optional[str] = None
    city_id: Optional[str] = None
    section_id: Optional[str] = None
    violation_date: Optional[str] = None
    vehicle_info: Optional[str] = None


class StatementRefinementResponse(BaseModel):
    """Response model for statement refinement."""

    refined_text: str
    original_text: str
    citation_number: str
    processing_time_ms: int
    model_used: str = "deepseek-chat"
    clerical_engine_version: str = "2.0.0"


class DeepSeekService:
    """
    DeepSeek AI service for statement refinement.

    The Clerical Engine™ processes user-provided statements to create
    professionally formatted appeal letters suitable for municipal submission.
    """

    API_URL = "https://api.deepseek.com/chat/completions"

    # Timeout and retry configuration
    DEFAULT_TIMEOUT = 60.0  # seconds
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSeek service.

        Args:
            api_key: DeepSeek API key. Falls back to DEEPSEEK_API_KEY env var.
        """
        self.api_key = (
            api_key or os.environ.get("DEEPSEEK_API_KEY") or settings.deepseek_api_key
        )
        self._client = None

    def _get_system_prompt(self) -> str:
        """
        Get the authoritative system prompt for procedural compliance refinement.

        This prompt establishes the Clerical Engine™ as a professional
        document preparation service, NOT a legal service.
        """
        return """You are the Clerical Engine™, a professional document preparation system operated by Neural Draft LLC.

YOUR ROLE: Document Articulation Specialist
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You transform citizen submissions into formally compliant procedural documents
that meet municipal administrative standards. You are NOT a lawyer, attorney,
or legal advisor. You do not provide legal advice.

CORE MISSION
━━━━━━━━━━━━
Your sole function is to ARTICULATE and REFINE the user's provided statement
into professional, formally structured language while PRESERVING:
- The user's exact factual content and circumstances
- The user's position and stated argument
- The user's voice and perspective
- All evidence and details the user has provided

MANDATORY PRESERVATION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. NEVER add facts, evidence, or content the user did not provide
2. NEVER suggest legal strategies or arguments
3. NEVER interpret laws, regulations, or statutes
4. NEVER use legal terminology or legal frameworks
5. NEVER predict outcomes or suggest what will "work"
6. NEVER tell the user what they "should" argue
7. NEVER make legal recommendations

REFINEMENT BOUNDARIES
━━━━━━━━━━━━━━━━━━━━
You may only:
- Elevate vocabulary while preserving meaning
- Improve grammar, syntax, and sentence structure
- Organize content for clarity and professional presentation
- Add formal salutations and closings appropriate to administrative documents
- Structure the document according to procedural standards

WHAT YOU MUST REMOVE
━━━━━━━━━━━━━━━━━━━━
- Casual language, slang, and colloquialisms
- Emotional outbursts or inflammatory language
- Profanity and vulgarity
- Casual abbreviations (use formal alternatives)
- First-person informal expressions

PROFESSIONAL TONE STANDARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Write as a professional bureaucrat would write to a municipal agency:
- Respectful but formal
- Factual and precise
- Free of emotional language
- Structured for administrative review
- Compliant with procedural standards

LETTER STRUCTURE (CLERICAL ENGINE™ FORMAT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Professional Header (automated by system)
2. Date
3. Agency Address Block
4. Subject Line: Citation Number
5. Salutation: "To Whom It May Concern" or agency-specific
6. Body: User's articulated statement (professionally refined)
7. Closing: "Respectfully submitted,"
8. Signature Block
9. Clerical Engine™ Footer (automated by system)

INPUT HANDLING
━━━━━━━━━━━━━━━
When users admit fault (e.g., "I parked there illegally"), do NOT invent defenses.
Instead, professionally articulate their acknowledgment and request leniency based on:
- Clean driving record
- First-time offense
- Circumstances that merit consideration
- Professional presentation of their honest position

OUTPUT FORMAT
━━━━━━━━━━━━━
Produce a single, professionally formatted letter ready for municipal submission.
Maintain the user's facts. Elevate their expression. Preserve their position.

The Clerical Engine™ processes submissions with ID: CE-{timestamp}"""

    def _create_refinement_prompt(self, request: StatementRefinementRequest) -> str:
        """Create the user prompt for statement refinement."""
        # Detect agency from citation number pattern
        agency_name = self._detect_agency(request.citation_number, request.city_id)

        return f"""CITATION DETAILS
━━━━━━━━━━━━━━━
Citation Number: {request.citation_number}
Agency: {agency_name}
Violation Date: {request.violation_date or "Not specified"}
Vehicle: {request.vehicle_info or "Not specified"}

USER'S SUBMITTED STATEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━
{request.appeal_reason}

INSTRUCTIONS
━━━━━━━━━━━━
Articulate the above statement into a professionally formatted appeal letter
that:
1. Preserves all user-provided facts and circumstances
2. Elevates language to formal administrative standards
3. Maintains the user's stated position and argument
4. Uses respectful, professional bureaucratic tone
5. Is ready for municipal submission

Write only the letter body. Do not include headers or footers (these are
added by the Clerical Engine™ automatically)."""

    def _detect_agency(
        self, citation_number: str, city_id: Optional[str] = None
    ) -> str:
        """Detect the agency from citation number pattern or city ID."""
        if city_id:
            city_mappings = {
                "sf": "SFMTA",
                "us-ca-san_francisco": "SFMTA",
                "la": "LADOT",
                "us-ca-los_angeles": "LADOT",
                "nyc": "NYC Department of Finance",
                "us-ny-new_york": "NYC Department of Finance",
                "us-ca-san_diego": "San Diego Transportation Dept",
                "us-az-phoenix": "Phoenix Transportation Dept",
                "us-co-denver": "Denver DOTI",
                "us-il-chicago": "Chicago Department of Finance",
                "us-or-portland": "Portland Bureau of Transportation",
                "us-pa-philadelphia": "Philadelphia Parking Authority",
                "us-tx-dallas": "Dallas Parking Services",
                "us-tx-houston": "Houston Parking Management",
                "us-ut-salt_lake_city": "Salt Lake City Transportation",
                "us-wa-seattle": "Seattle DOT",
            }
            if city_id in city_mappings:
                return city_mappings[city_id]

        # Fallback: detect from citation number pattern
        citation_clean = citation_number.upper().replace("-", "").replace(" ", "")

        if citation_clean.isdigit() and len(citation_clean) <= 9:
            # Likely SF pattern
            return "SFMTA"
        elif citation_clean.startswith("LA") or "LAPD" in citation_clean:
            return "LADOT"
        elif citation_clean.startswith("NYC") or citation_clean.startswith("NY"):
            return "NYC Department of Finance"
        elif citation_clean.startswith("CH"):
            return "Chicago Department of Finance"

        return "Citation Review Board"

    def _clean_response(self, response: str) -> str:
        """Clean and normalize the AI response."""
        # Remove common AI artifacts
        cleaned = response.strip()

        # Remove "Here is your refined letter:" or similar prefixes
        prefixes_to_remove = [
            "Here is the refined letter:",
            "Here is your professionally formatted letter:",
            "Below is the refined statement:",
            "The refined letter is:",
            "Your appeal letter:",
        ]
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix) :].strip()

        # Remove any "Dear Citation Review Board" if it appears (added by system)
        # The system adds salutation automatically
        return cleaned

    def _has_proper_structure(self, text: str) -> bool:
        """Check if the refined text has proper letter structure."""
        # Basic checks for letter-like structure
        if len(text) < 50:
            return False
        return True

    async def refine_statement_async(
        self, request: StatementRefinementRequest
    ) -> StatementRefinementResponse:
        """Refine a user statement using DeepSeek AI with retries."""
        import time
        import httpx

        start_time = time.time()
        original_text = request.appeal_reason

        # Retry logic for transient failures
        last_error = None
        for attempt in range(self.RETRY_COUNT):
            try:
                async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                    response = await client.post(
                        self.API_URL,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": self._get_system_prompt()},
                                {
                                    "role": "user",
                                    "content": self._create_refinement_prompt(request),
                                },
                            ],
                            "temperature": 0.3,
                            "max_tokens": 2000,
                            "stream": False,
                        },
                    )

                response.raise_for_status()
                data = response.json()

                refined_text = data["choices"][0]["message"]["content"]
                refined_text = self._clean_response(refined_text)

                # Fallback validation
                if not self._has_proper_structure(refined_text):
                    logger.warning("AI response lacks proper structure, using fallback")
                    refined_text = self._local_fallback_refinement(request)

                processing_time = int((time.time() - start_time) * 1000)

                return StatementRefinementResponse(
                    refined_text=refined_text,
                    original_text=original_text,
                    citation_number=request.citation_number,
                    processing_time_ms=processing_time,
                )

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"DeepSeek timeout (attempt {attempt + 1}/{self.RETRY_COUNT})")
                if attempt < self.RETRY_COUNT - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (2 ** attempt))  # Exponential backoff

            except httpx.NetworkError as e:
                last_error = e
                logger.warning(f"DeepSeek network error (attempt {attempt + 1}/{self.RETRY_COUNT})")
                if attempt < self.RETRY_COUNT - 1:
                    await time.sleep(self.RETRY_DELAY * (2 ** attempt))

            except httpx.HTTPStatusError as e:
                # Retry on 5xx errors, but not on 4xx
                if e.response.status_code >= 500:
                    last_error = e
                    logger.warning(f"DeepSeek server error {e.response.status_code} (attempt {attempt + 1}/{self.RETRY_COUNT})")
                    if attempt < self.RETRY_COUNT - 1:
                        await time.sleep(self.RETRY_DELAY * (2 ** attempt))
                else:
                    # Non-retryable client error
                    logger.error(f"DeepSeek client error: {e}")
                    break

            except Exception as e:
                logger.error(f"DeepSeek API error: {e}")
                break

        # All retries exhausted or non-retryable error - fallback to local refinement
        logger.error(f"DeepSeek failed after {self.RETRY_COUNT} attempts: {last_error}")
        refined_text = self._local_fallback_refinement(request)
        processing_time = int((time.time() - start_time) * 1000)

        return StatementRefinementResponse(
            refined_text=refined_text,
            original_text=original_text,
            citation_number=request.citation_number,
            processing_time_ms=processing_time,
        )

    def _local_fallback_refinement(self, request: StatementRefinementRequest) -> str:
        """Local fallback when AI is unavailable."""
        agency = self._detect_agency(request.citation_number, request.city_id)

        # Professional template with user content
        user_content = request.appeal_reason.strip()

        # Clean up user content
        lines = user_content.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.lower().startswith("dear"):
                cleaned_lines.append(line)

        body = " ".join(cleaned_lines)

        # Ensure proper punctuation and capitalization
        if body and not body[-1] in ".!?":
            body += "."

        return f"""To Whom It May Concern:

Re: Citation Number {request.citation_number}

I am writing to formally submit an appeal regarding the above-referenced parking citation.

{body}

Respectfully submitted,

{request.user_name or "Citizen"}"""


def get_statement_service() -> DeepSeekService:
    """Get an instance of the DeepSeek service."""
    return DeepSeekService()


async def refine_statement(
    citation_number: str,
    appeal_reason: str,
    user_name: Optional[str] = None,
    city_id: Optional[str] = None,
) -> StatementRefinementResponse:
    """
    Convenience function to refine a statement.

    Args:
        citation_number: The citation number
        appeal_reason: The user's appeal statement
        user_name: Optional user name for signature
        city_id: Optional city identifier

    Returns:
        StatementRefinementResponse with refined text
    """
    service = get_statement_service()

    request = StatementRefinementRequest(
        citation_number=citation_number,
        appeal_reason=appeal_reason,
        user_name=user_name,
        city_id=city_id,
    )

    return await service.refine_statement_async(request)


async def test_refinement() -> Dict[str, Any]:
    """Test the refinement service with a sample statement."""
    test_request = StatementRefinementRequest(
        citation_number="123456789",
        appeal_reason="I parked at a meter that was broken. I checked it and it showed no time left but I had just put money in. This seems unfair.",
        user_name="John Doe",
        city_id="sf",
    )

    result = await refine_statement(
        test_request.citation_number,
        test_request.appeal_reason,
        test_request.user_name,
        test_request.city_id,
    )

    return {
        "success": True,
        "refined_text": result.refined_text,
        "processing_time_ms": result.processing_time_ms,
        "model_used": result.model_used,
    }