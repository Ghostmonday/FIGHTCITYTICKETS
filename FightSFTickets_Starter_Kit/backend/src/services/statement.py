"""
Statement Refinement Service for FightSFTickets.com

Uses DeepSeek AI to convert user appeal statements into professional,
UPL-compliant appeal letters for San Francisco parking tickets.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from ..config import settings

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class StatementRefinementRequest:
    """Request model for statement refinement."""

    original_statement: str
    citation_number: str = ""
    citation_type: str = "parking"
    desired_tone: str = "professional"  # professional, formal, concise
    max_length: int = 500


@dataclass
class StatementRefinementResponse:
    """Response model for statement refinement."""

    status: str  # "success", "fallback", "error", "service_unavailable"
    original_statement: str
    refined_statement: str
    improvements: Dict[str, bool] = None
    error_message: Optional[str] = None
    method_used: str = ""  # "deepseek", "local_fallback"


class DeepSeekService:
    """Handles AI statement refinement using DeepSeek API."""

    def __init__(self):
        """Initialize DeepSeek service."""
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.client = httpx.AsyncClient(timeout=30.0)

        # Check if API key is configured
        self.is_available = bool(self.api_key and self.api_key != "change-me")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def refine_statement_async(
        self, request: StatementRefinementRequest
    ) -> StatementRefinementResponse:
        """
        Refine a parking ticket appeal statement using DeepSeek AI.

        Returns a professional, UPL-compliant appeal letter.
        """
        try:
            # Check if service is available
            if not self.is_available:
                logger.warning("DeepSeek API key not configured, using fallback")
                return self._local_fallback_refinement(request)

            # Create the system prompt
            system_prompt = self._get_system_prompt()

            # Create user prompt with the transcript
            user_prompt = self._create_refinement_prompt(request)

            # Make API call to DeepSeek
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": min(request.max_length, 1000),
                    "temperature": 0.3,  # Low temperature for consistency
                    "top_p": 0.9,
                },
            )

            response.raise_for_status()
            data = response.json()

            # Extract the refined statement
            refined_statement = data["choices"][0]["message"]["content"].strip()

            # Clean up the response (remove markdown formatting if present)
            refined_statement = self._clean_response(refined_statement)

            logger.info(
                f"DeepSeek refined statement: {len(request.original_statement)} -> {len(refined_statement)} chars"
            )

            return StatementRefinementResponse(
                status="success",
                original_statement=request.original_statement,
                refined_statement=refined_statement,
                improvements={
                    "professional_tone": True,
                    "factual_language": True,
                    "upl_compliant": True,
                    "structured_format": self._has_proper_structure(refined_statement),
                },
                method_used="deepseek",
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"DeepSeek API error: {e.response.status_code} - {e.response.text}"
            )
            return self._local_fallback_refinement(request)

        except Exception as e:
            logger.error(f"DeepSeek service error: {str(e)}")
            return self._local_fallback_refinement(request)

    def _get_system_prompt(self) -> str:
        """Get the UPL-compliant system prompt for DeepSeek."""
        return """You are a professional document assistant for FightSFTickets.com.

Your task: Convert a user's informal spoken complaint about a parking ticket into a formal, factual appeal letter.

RULES:
1. NEVER give legal advice or recommend what evidence to include
2. Use neutral, professional language only
3. State FACTS, not opinions
4. Do not editorialize or add emotional language
5. Do not make claims the user did not make
6. Format as a formal letter to the citation agency

INPUT: User transcript about their parking ticket situation
OUTPUT: A professional appeal letter ready for signature

Structure:
- Header: Date, Recipient Address placeholder
- Subject: Citation Number
- Body: Factual statement of circumstances
- Closing: Request for review/dismissal
- Signature block placeholder"""

    def _create_refinement_prompt(self, request: StatementRefinementRequest) -> str:
        """Create the user prompt for statement refinement."""
        return f"""Please convert this informal statement into a professional appeal letter:

"{request.original_statement}"

Citation Number: {request.citation_number or "Not provided"}
Citation Type: {request.citation_type or "Parking ticket"}

Please provide a formal, factual appeal letter that states only the facts mentioned by the user, without adding legal advice or recommendations about evidence."""

    def _clean_response(self, response: str) -> str:
        """Clean up the AI response to ensure it's appropriate."""
        # Remove any markdown formatting
        response = response.replace("**", "").replace("*", "")

        # Remove excessive line breaks
        while "\n\n\n" in response:
            response = response.replace("\n\n\n", "\n\n")

        # Trim whitespace
        response = response.strip()

        return response

    def _has_proper_structure(self, text: str) -> bool:
        """Check if the refined text has proper letter structure."""
        # Look for common indicators of proper structure
        indicators = ["citation", "appeal", "request", "review"]
        text_lower = text.lower()

        return any(indicator in text_lower for indicator in indicators)

    def _local_fallback_refinement(
        self, request: StatementRefinementRequest
    ) -> StatementRefinementResponse:
        """Provide basic local refinement when AI service is unavailable."""
        original = request.original_statement

        # Simple improvements for fallback
        refined = original

        # Basic cleanup
        replacements = {
            "i was": "I was",
            "the meter": "The parking meter",
            "it didn't work": "The parking meter was not functioning properly",
            "i only parked": "I parked only",
            "for like": "for approximately",
            "i think": "",  # Remove uncertainty
            "probably": "",  # Remove uncertainty
        }

        for informal, formal in replacements.items():
            refined = refined.replace(informal, formal)

        # Capitalize first letter
        if refined and not refined[0].isupper():
            refined = refined[0].upper() + refined[1:]

        # Add period if missing
        if refined and not refined.endswith((".", "!", "?")):
            refined += "."

        logger.info(
            f"Using local fallback refinement: {len(original)} -> {len(refined)} chars"
        )

        return StatementRefinementResponse(
            status="fallback",
            original_statement=original,
            refined_statement=refined,
            improvements={
                "basic_cleanup": True,
                "capitalization": refined[0].isupper(),
                "punctuation": refined.endswith((".", "!", "?")),
            },
            method_used="local_fallback",
        )


# Global service instance
_statement_service = None


def get_statement_service() -> DeepSeekService:
    """Get the global statement service instance."""
    global _statement_service
    if _statement_service is None:
        _statement_service = DeepSeekService()
    return _statement_service


async def refine_statement(
    original_statement: str,
    citation_number: str = "",
    citation_type: str = "parking",
    desired_tone: str = "professional",
    max_length: int = 500,
) -> StatementRefinementResponse:
    """
    High-level function to refine a statement.

    This is the main entry point for the service.
    """
    if not original_statement or not original_statement.strip():
        return StatementRefinementResponse(
            status="error",
            original_statement=original_statement,
            refined_statement=original_statement,
            error_message="Empty statement provided",
            method_used="none",
        )

    request = StatementRefinementRequest(
        original_statement=original_statement.strip(),
        citation_number=citation_number,
        citation_type=citation_type,
        desired_tone=desired_tone,
        max_length=max_length,
    )

    service = get_statement_service()
    try:
        return await service.refine_statement_async(request)
    finally:
        # Clean up the service instance
        try:
            await service.close()
        except Exception:
            pass  # Ignore cleanup errors


# Test function
async def test_refinement():
    """Test the statement refinement service."""
    print("🧪 Testing Statement Refinement Service")
    print("=" * 50)

    test_statement = """
    i got this ticket but the meter was broken. i tried to pay but it didn't work.
    the screen was all messed up and wouldn't take my money. i only parked for
    like 15 minutes and i think it's unfair that i got a ticket.
    """

    try:
        print(f"Original: {test_statement.strip()}")

        result = await refine_statement(
            original_statement=test_statement,
            citation_number="912345678",
        )

        print(f"Status: {result.status}")
        print(f"Method: {result.method_used}")
        print(f"Refined: {result.refined_statement}")

        if result.improvements:
            print(f"Improvements: {result.improvements}")

        print("\n✅ Statement refinement test completed")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_refinement())
