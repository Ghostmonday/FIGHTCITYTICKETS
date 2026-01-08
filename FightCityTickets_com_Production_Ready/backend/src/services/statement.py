"""
Statement Refinement Service for FightCityTickets.com

Uses DeepSeek AI to convert user appeal statements into professional,
UPL-compliant appeal letters for San Francisco parking tickets.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import httpx

from ..config import settings
from .citation import CitationValidator

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
        # Don't create client here - create fresh client for each request
        # to avoid "client has been closed" errors

        # Check if API key is configured
        self.is_available = bool(self.api_key and self.api_key != "change-me")

    async def close(self):
        """Close HTTP client - no-op since we create fresh clients."""
        pass

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

            # Create fresh HTTP client for each request to avoid lifecycle issues
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Make API call to DeepSeek
                response = await client.post(
                    "{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer {self.api_key}",
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
                "DeepSeek refined statement: {len(request.original_statement)} -> {len(refined_statement)} chars"
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
                "DeepSeek API error: {e.response.status_code} - {e.response.text}"
            )
            return self._local_fallback_refinement(request)

        except Exception as e:
            logger.error("DeepSeek service error: {str(e)}")
            return self._local_fallback_refinement(request)

    def _get_system_prompt(self) -> str:
        """Get the UPL-compliant system prompt for DeepSeek focused on articulation and polish."""
        return """You are a Professional Language Articulation and Document Refinement Specialist for FightCityTickets.com.

CORE MISSION:
Your role is to elevate, polish, and articulate the user's own words into exceptionally well-written, professional language. You are a master of articulation and refinement - transforming informal, everyday language into eloquent, respectful, and articulate written communication. You are NOT a legal advisor, attorney, or legal consultant. You are a language articulation and refinement specialist.

CRITICAL UPL COMPLIANCE (MANDATORY - NEVER VIOLATE):
1. NEVER provide legal advice, legal strategy, legal recommendations, or legal opinions
2. NEVER suggest what evidence to include, what arguments to make, or what legal points to raise
3. NEVER use legal terminology beyond basic formal language (e.g., "respectfully request" is fine, "pursuant to statute" is NOT)
4. NEVER predict outcomes, suggest legal strategies, or imply what will or won't work legally
5. NEVER add legal analysis, legal interpretation, legal conclusions, or legal reasoning
6. NEVER tell the user what they "should" do legally, what they "must" include, or what legal approach to take
7. ONLY articulate and refine the language the user provides - preserve their facts, their story, their position
8. NEVER add legal content, legal citations, legal references, or legal frameworks

ARTICULATION AND ELEVATION REQUIREMENTS (PRIMARY FOCUS):
1. Transform informal speech into eloquent, articulate written language
2. Elevate vocabulary significantly while preserving exact meaning and intent
3. Enhance clarity, precision, and impact of expression
4. Improve grammar, syntax, and sentence structure for maximum professionalism
5. Use sophisticated, respectful, and courteous language throughout
6. Structure sentences for elegance, clarity, and persuasive impact
7. Maintain the user's factual content, their story, and their position completely intact
8. Polish language to be legally respectable (professional, formal, articulate) but NOT legally expressed (no legal advice)

PROFANITY AND LANGUAGE FILTERING (MANDATORY):
1. Remove ALL profanity, vulgarity, obscenity, and offensive language completely
2. Replace inappropriate language with sophisticated, professional alternatives
3. Remove ALL swear words, curse words, slang, and casual expressions
4. Filter out any offensive, inflammatory, or unprofessional content
5. Maintain exceptionally professional tone at all times - no exceptions

WHAT YOU EXCEL AT:
- Elevating vocabulary from everyday to sophisticated and articulate
- Polishing language to be exceptionally well-written and professional
- Refining grammar and syntax for maximum clarity and impact
- Structuring sentences for elegance and persuasive power
- Transforming informal speech into articulate, formal written communication
- Making the user's story sound professional, respectful, and compelling
- Ensuring language is legally respectable (formal, articulate, professional)

WHAT YOU NEVER DO:
- Provide legal advice, legal recommendations, or legal opinions
- Suggest evidence, arguments, or legal strategies
- Add legal analysis, interpretation, or legal reasoning
- Predict outcomes or suggest what will work legally
- Use legal terminology or legal frameworks
- Tell users what they should do legally

INPUT: User's informal statement about their parking ticket situation (may contain casual language, profanity, or informal speech)
OUTPUT: An exceptionally well-articulated, professionally polished appeal letter with:
- All profanity and inappropriate language removed
- Vocabulary significantly elevated while preserving exact meaning
- Language polished to be sophisticated, articulate, and professional
- Grammar and syntax refined for maximum clarity and impact
- Proper formal letter structure
- User's factual content, story, and position completely preserved
- Legally respectable tone (professional, formal, articulate)
- NO legal advice, legal recommendations, or legal expression

LETTER STRUCTURE:
- Header: Date, Recipient Address (use agency-specific address placeholder)
- Salutation: Use appropriate agency name (SFMTA, SFPD, SFSU, SFMUD, or city-specific agency)
- Subject: Citation Number
- Body: Factual statement of circumstances (exceptionally well-articulated and polished)
- Closing: Respectful, articulate request for review
- Signature block placeholder

REMEMBER: You are a language articulation specialist. Your job is to take what the user tells you and make it sound exceptionally professional, articulate, and well-written. Elevate their vocabulary, polish their language, refine their expression - but preserve their facts, their story, and their position. Make it legally respectable through professional articulation, NOT through legal expression or legal advice."""

    def _create_refinement_prompt(self, request: StatementRefinementRequest) -> str:
        """Create the user prompt for statement refinement."""
        # Detect agency from citation number
        agency = "SFMTA"  # Default
        if request.citation_number:
            try:
                agency_enum = CitationValidator.identify_agency(request.citation_number)
                agency = agency_enum.value
            except Exception:
                pass  # Keep default if detection fails

        return """Please elevate, polish, and articulate this user statement into an exceptionally well-written, professional appeal letter.

USER'S ORIGINAL STATEMENT (may contain informal language, casual speech, or profanity):
"{request.original_statement}"

Citation Number: {request.citation_number or "Not provided"}
Citation Agency: {agency}
Citation Type: {request.citation_type or "Parking ticket"}

YOUR TASK - ARTICULATION AND POLISH:
1. Remove ALL profanity, swear words, vulgarity, slang, and inappropriate language completely
2. Elevate vocabulary significantly - transform everyday words into sophisticated, articulate language
3. Polish language to be exceptionally well-written, professional, and eloquent
4. Refine grammar, syntax, and sentence structure for maximum clarity and impact
5. Enhance articulation - make the user's story sound professional, compelling, and respectful
6. Preserve the user's exact factual content, their story, and their position completely intact
7. Format as a proper formal appeal letter structure
8. Ensure language is legally respectable (professional, formal, articulate) but NOT legally expressed

CRITICAL RESTRICTIONS:
- DO NOT add legal advice, legal recommendations, legal strategies, or legal opinions
- DO NOT suggest evidence, arguments, or what to include
- DO NOT add legal analysis, legal interpretation, or legal reasoning
- DO NOT use legal terminology beyond basic formal language
- DO NOT predict outcomes or suggest what will work legally
- ONLY articulate and polish the language - preserve user's facts, story, and position

OUTPUT REQUIREMENTS:
Provide an exceptionally well-articulated, professionally polished appeal letter that:
- Removes all profanity and inappropriate language
- Significantly elevates vocabulary while preserving exact meaning
- Polishes language to be sophisticated, articulate, and professional
- Refines grammar and syntax for maximum clarity and impact
- Maintains the user's factual content, story, and position completely
- Sounds legally respectable through professional articulation, NOT legal expression
- Is exceptionally well-written and compelling
- Includes a clear statement before the closing requesting that responses be sent to the return address (use placeholder [RETURN_ADDRESS] which will be replaced with actual address)

IMPORTANT: Before the closing (e.g., "Sincerely,"), include a statement like:
"Please send your response regarding this appeal to the following address: [RETURN_ADDRESS]"

This ensures the city knows where to send their response even if the envelope is separated from the letter."""

    def _clean_response(self, response: str) -> str:
        """Clean up the AI response to ensure it's appropriate and profanity-free."""
        # Remove any markdown formatting
        response = response.replace("**", "").replace("*", "")

        # Remove excessive line breaks
        while "\n\n\n" in response:
            response = response.replace("\n\n\n", "\n\n")

        # Profanity filter - common profanity words (case-insensitive)
        profanity_patterns = [
            r'\b(fuck|fucking|fucked)\b',
            r'\b(shit|shitting|shitted)\b',
            r'\b(damn|damned|damnit)\b',
            r'\b(hell|hellish)\b',
            r'\b(ass|asses|asshole)\b',
            r'\b(bitch|bitches|bitching)\b',
            r'\b(crap|crappy)\b',
            r'\b(piss|pissing|pissed)\b',
            r'\b(bullshit|bullcrap)\b',
            r'\b(goddamn|goddamnit)\b',
        ]

        for pattern in profanity_patterns:
            response = re.sub(pattern, '', response, flags=re.IGNORECASE)

        # Clean up multiple spaces
        response = re.sub(r'\s+', ' ', response)

        # Clean up multiple periods or punctuation
        response = re.sub(r'\.{3,}', '...', response)

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

        # Detect agency from citation number
        agency = "SFMTA"  # Default
        if request.citation_number:
            try:
                agency_enum = CitationValidator.identify_agency(request.citation_number)
                agency = agency_enum.value
            except Exception:
                pass  # Keep default if detection fails

        # Agency-specific salutations
        agency_salutations = {
            "SFMTA": "SFMTA Citation Review",
            "SFPD": "San Francisco Police Department - Traffic Division",
            "SFSU": "San Francisco State University - Parking & Transportation",
            "SFMUD": "San Francisco Municipal Utility District",
            "UNKNOWN": "Citation Review Department",
        }
        salutation = agency_salutations.get(agency, "Citation Review Department")

        # Simple improvements for fallback
        refined = original

        # Profanity filter for fallback - remove all profanity
        profanity_words = [
            'fuck', 'fucking', 'fucked', 'fucker',
            'shit', 'shitting', 'shitted', 'shits',
            'damn', 'damned', 'damnit', 'dammit',
            'hell', 'hellish',
            'ass', 'asses', 'asshole', 'assholes',
            'bitch', 'bitches', 'bitching', 'bitched',
            'crap', 'crappy',
            'piss', 'pissing', 'pissed', 'pisses',
            'bullshit', 'bullcrap',
            'goddamn', 'goddamnit', 'goddamned',
        ]

        for word in profanity_words:
            refined = re.sub(r'\b' + re.escape(word) + r'\b', '', refined, flags=re.IGNORECASE)

        # Enhanced language elevation and articulation
        replacements = {
            # Basic capitalization
            "i was": "I was",
            "i am": "I am",
            "i had": "I had",
            "i did": "I did",
            "i tried": "I attempted",
            "i think": "I believe",  # Elevate uncertainty
            "i feel": "I believe",
            # Elevate vocabulary - transform everyday to articulate
            "the meter": "The parking meter",
            "it didn't work": "The parking meter was not functioning properly",
            "it was broken": "The parking meter was malfunctioning",
            "it was messed up": "The parking meter was not functioning correctly",
            "i only parked": "I parked only",
            "for like": "for approximately",
            "for about": "for approximately",
            "around": "approximately",
            "really": "quite",  # Elevate language
            "very": "particularly",  # Elevate language
            "bad": "problematic",  # Elevate language
            "good": "appropriate",  # Elevate language
            "stuf": "items",  # Elevate language
            "thing": "matter",  # Elevate language
            "guy": "individual",  # Elevate language
            "people": "individuals",  # Elevate language
            "got": "received",  # Elevate language
            "ticket": "citation",  # More formal
            "unfair": "unjust",  # More articulate
            "wrong": "incorrect",  # More formal
            "right": "correct",  # More formal
            "sure": "certain",  # More articulate
            "maybe": "perhaps",  # More articulate
            "probably": "likely",  # More articulate
            "a lot": "considerably",  # More articulate
            "kinda": "somewhat",  # More articulate
            "sorta": "somewhat",  # More articulate
        }

        for informal, formal in replacements.items():
            refined = refined.replace(informal, formal)

        # Clean up multiple spaces left by profanity removal
        refined = re.sub(r'\s+', ' ', refined)
        refined = refined.strip()

        # Capitalize first letter
        if refined and not refined[0].isupper():
            refined = refined[0].upper() + refined[1:]

        # Add period if missing
        if refined and not refined.endswith((".", "!", "?")):
            refined += "."

        # Wrap in proper letter format
        citation_part = (
            "Citation #{request.citation_number}"
            if request.citation_number
            else "Citation"
        )
        date_str = datetime.now().strftime("%B %d, %Y")

        formatted_letter = """{date_str}

{salutation}

Subject: Appeal of {citation_part}

Dear Sir or Madam,

I am writing to respectfully appeal the parking citation referenced above.

{refined}

I respectfully request that you review this matter and consider dismissing the citation. Thank you for your time and consideration.

Please send your response regarding this appeal to the following address:

[RETURN_ADDRESS]

Sincerely,

[Your Name]"""

        logger.info(
            "Using local fallback refinement with agency detection ({agency}): {len(original)} -> {len(formatted_letter)} chars"
        )

        return StatementRefinementResponse(
            status="fallback",
            original_statement=original,
            refined_statement=formatted_letter,
            improvements={
                "basic_cleanup": True,
                "capitalization": True,
                "punctuation": True,
                "agency_detected": agency != "SFMTA",
                "letter_format": True,
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
    return await service.refine_statement_async(request)


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
        print("Original: {test_statement.strip()}")

        result = await refine_statement(
            original_statement=test_statement,
            citation_number="912345678",
        )

        print("Status: {result.status}")
        print("Method: {result.method_used}")
        print("Refined: {result.refined_statement}")

        if result.improvements:
            print("Improvements: {result.improvements}")

        print("\n✅ Statement refinement test completed")

    except Exception as e:
        print("❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_refinement())
