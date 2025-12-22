"""
OpenAI Whisper Transcription Service for FightSFTickets.com

Handles voice recording transcription for appeal statements.
Uses OpenAI Whisper API to convert speech to text.
"""

import io
import logging
from typing import Optional, Tuple

import httpx
from pydub import AudioSegment

from ..config import settings

# Set up logger
logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {"webm", "mp3", "wav", "m4a", "ogg", "flac"}
MAX_DURATION_SECONDS = 120  # 2 minutes


class TranscriptionError(Exception):
    """Custom exception for transcription errors."""

    pass


class WhisperTranscriptionService:
    """Handles audio transcription using OpenAI Whisper API."""

    def __init__(self):
        """Initialize Whisper service."""
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"
        self.model = "whisper-1"  # Latest Whisper model

        # Check if API key is configured
        self.is_available = bool(self.api_key and self.api_key != "change-me")

        if not self.is_available:
            logger.warning("OpenAI API key not configured for transcription")

    def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio data using OpenAI Whisper.

        Args:
            audio_data: Raw audio file bytes
            filename: Original filename with extension
            content_type: MIME type (optional, inferred from filename)

        Returns:
            Transcribed text

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            # Validate and preprocess audio
            validated_data, format_type = self._validate_and_preprocess_audio(
                audio_data, filename, content_type
            )

            # Check if service is available
            if not self.is_available:
                logger.warning("Whisper API unavailable, using fallback transcription")
                return self._fallback_transcription(validated_data, format_type)

            # Call OpenAI Whisper API
            transcription = self._call_whisper_api(validated_data, filename)

            logger.info(
                f"Successfully transcribed {len(audio_data)} bytes -> {len(transcription)} chars"
            )

            return transcription.strip()

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            # Try fallback transcription
            try:
                validated_data, format_type = self._validate_and_preprocess_audio(
                    audio_data, filename, content_type
                )
                return self._fallback_transcription(validated_data, format_type)
            except Exception as fallback_error:
                logger.error(
                    f"Fallback transcription also failed: {str(fallback_error)}"
                )
                raise TranscriptionError(
                    f"Audio transcription failed: {str(e)}. Please try again or provide text manually."
                ) from e

    def _validate_and_preprocess_audio(
        self,
        audio_data: bytes,
        filename: str,
        content_type: Optional[str] = None,
    ) -> Tuple[bytes, str]:
        """
        Validate and preprocess audio data.

        Returns:
            Tuple of (processed_audio_bytes, format_type)
        """
        try:
            # Determine file format
            format_type = self._determine_format(filename, content_type)

            # Load audio with pydub to validate and check duration
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format_type)

            # Check duration
            duration_seconds = len(audio) / 1000.0  # pydub uses milliseconds
            if duration_seconds > MAX_DURATION_SECONDS:
                raise TranscriptionError(
                    f"Audio too long: {duration_seconds:.1f}s (max {MAX_DURATION_SECONDS}s). "
                    "Please keep recordings under 2 minutes."
                )

            if duration_seconds < 0.5:
                raise TranscriptionError(
                    f"Audio too short: {duration_seconds:.1f}s. Please speak longer."
                )

            # Normalize audio (optional but recommended)
            audio = audio.normalize()

            # Export back to bytes in the same format
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format=format_type)
            processed_data = output_buffer.getvalue()

            logger.info(
                f"Validated audio: {format_type.upper()}, {duration_seconds:.1f}s"
            )

            return processed_data, format_type

        except Exception as e:
            if isinstance(e, TranscriptionError):
                raise
            raise TranscriptionError(f"Audio validation failed: {str(e)}") from e

    def _determine_format(
        self, filename: str, content_type: Optional[str] = None
    ) -> str:
        """Determine audio format from filename and content type."""
        # Try to get format from filename extension
        if filename:
            # Split by dots and get last part
            parts = filename.split(".")
            if len(parts) > 1:
                ext = parts[-1].lower()
                # Map common extensions to formats
                format_map = {
                    "webm": "webm",
                    "mp3": "mp3",
                    "wav": "wav",
                    "m4a": "mp4",  # pydub treats m4a as mp4
                    "aac": "aac",
                    "ogg": "ogg",
                    "oga": "ogg",
                    "flac": "flac",
                }
                if ext in format_map:
                    return format_map[ext]

        # Try to get format from content type
        if content_type:
            # Extract format from MIME type
            if content_type.startswith("audio/"):
                format_part = content_type.split("/")[-1].split(";")[0]
                if format_part in SUPPORTED_FORMATS:
                    # Handle m4a -> mp4 mapping for pydub
                    return "mp4" if format_part == "m4a" else format_part

        # Default to webm (common for browser recordings)
        return "webm"

    def _call_whisper_api(self, audio_data: bytes, filename: str) -> str:
        """Call OpenAI Whisper API for transcription."""
        try:
            # Prepare the multipart form data
            files = {
                "file": (filename, io.BytesIO(audio_data), "audio/webm"),
            }
            data = {
                "model": self.model,
                "language": "en",  # English (default for SF appeals)
                "response_format": "text",  # Return plain text
            }

            # Make API request
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    files=files,
                    data=data,
                )

                response.raise_for_status()
                return response.text

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise TranscriptionError("Invalid OpenAI API key") from e
            elif e.response.status_code == 429:
                raise TranscriptionError(
                    "OpenAI API rate limit exceeded. Please try again later."
                ) from e
            else:
                raise TranscriptionError(
                    f"Whisper API error: {e.response.status_code}"
                ) from e
        except httpx.RequestError as e:
            raise TranscriptionError(
                f"Network error calling Whisper API: {str(e)}"
            ) from e

    def _fallback_transcription(self, audio_data: bytes, format_type: str) -> str:
        """Basic fallback transcription when Whisper is unavailable."""
        # This is a very basic fallback that can't actually transcribe speech
        # In a real implementation, you might use a local Whisper model or simpler service

        logger.info("Using transcription fallback (no actual speech recognition)")

        return (
            "[Audio recording received. Due to technical issues, "
            "the transcription service is temporarily unavailable. "
            "Please describe your appeal in text below.]"
        )


# Global service instance
_transcription_service = None


def get_transcription_service() -> WhisperTranscriptionService:
    """Get the global transcription service instance."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = WhisperTranscriptionService()
    return _transcription_service


def transcribe_audio_file(
    audio_data: bytes,
    filename: str,
    content_type: Optional[str] = None,
) -> str:
    """
    High-level function to transcribe audio.

    This is the main entry point for the service.
    """
    service = get_transcription_service()
    return service.transcribe_audio(audio_data, filename, content_type)


# Test function (requires pydub and audio file)
def test_transcription():
    """Test the transcription service."""
    print("🧪 Testing Transcription Service")
    print("=" * 50)

    # Note: This requires actual audio files and OpenAI API key
    print("⚠️  Note: Full testing requires:")
    print("   1. OpenAI API key in environment")
    print("   2. pydub: pip install pydub")
    print("   3. ffmpeg for audio processing")
    print("   4. Test audio file")
    print("\n   Service initialized and ready for testing with real audio.")

    service = get_transcription_service()
    print(f"✅ Service initialized: available={service.is_available}")
    print("✅ Configuration loaded successfully")


if __name__ == "__main__":
    test_transcription()
