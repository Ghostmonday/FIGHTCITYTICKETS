"""
Transcription Routes for FightSFTickets.com

Handles voice recording upload and transcription using OpenAI Whisper.
"""

from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status

try:
    from services.transcription import transcribe_audio_file
except ImportError:
    from ..services.transcription import transcribe_audio_file

router = APIRouter()


@router.post("/")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    max_duration: Optional[int] = 120,
) -> dict:
    """
    Transcribe an audio recording to text.

    Accepts audio files and returns the transcribed text.
    Supports common audio formats: webm, mp3, wav, m4a, etc.

    Args:
        audio_file: Audio file upload
        max_duration: Maximum duration in seconds (default: 120)

    Returns:
        Dict with transcription and metadata
    """
    try:
        # Validate file type
        if not audio_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file filename is required",
            )

        # Read file content
        audio_data = await audio_file.read()

        # Check file size (max 25MB for OpenAI API)
        max_size = 25 * 1024 * 1024  # 25MB
        if len(audio_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file too large (max 25MB)",
            )

        # Check if file is empty
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Audio file is empty"
            )

        # Transcribe the audio
        transcription = transcribe_audio_file(
            audio_data=audio_data,
            filename=audio_file.filename,
            content_type=audio_file.content_type,
        )

        return {
            "success": True,
            "transcription": transcription,
            "file_info": {
                "filename": audio_file.filename,
                "content_type": audio_file.content_type,
                "size_bytes": len(audio_data),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        # Handle transcription errors
        error_message = f"Transcription failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )


@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_audio_file(
    audio_file: UploadFile = File(...),
) -> dict:
    """
    Validate an audio file without transcribing it.

    Useful for frontend validation before upload.
    """
    try:
        # Basic validation
        if not audio_file.filename:
            return {"valid": False, "error": "Filename required"}

        # Read just enough to check format
        first_chunk = await audio_file.read(1024)  # Read first 1KB
        await audio_file.seek(0)  # Reset file pointer

        if len(first_chunk) == 0:
            return {"valid": False, "error": "File is empty"}

        # Check file extension
        filename_lower = audio_file.filename.lower()
        supported_extensions = [".webm", ".mp3", ".wav", ".m4a", ".ogg", ".flac"]

        if not any(filename_lower.endswith(ext) for ext in supported_extensions):
            return {
                "valid": False,
                "error": f"Unsupported format. Supported: {', '.join(supported_extensions)}",
            }

        return {
            "valid": True,
            "filename": audio_file.filename,
            "content_type": audio_file.content_type,
            "message": "Audio file format is supported",
        }

    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}
