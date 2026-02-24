"""Photo upload routes for handling ticket image uploads."""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

router = APIRouter(tags=["photos"])

# Configure upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/fightcity-uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed image types
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class UploadResponse(BaseModel):
    """Response model for photo upload."""
    photo_id: str
    filename: str
    size: int
    uploaded_at: str


@router.post("/photos/upload", response_model=UploadResponse)
async def upload_photo(
    citation_number: Optional[str] = None,
    city_id: Optional[str] = None,
    file: UploadFile = File(...),
):
    """
    Upload a photo of a parking ticket.
    
    Stores the file temporarily and returns a photo_id that can be
    used to associate the photo with an appeal.
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_TYPES)}",
        )

    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024)}MB",
        )

    # Generate unique ID
    photo_id = str(uuid.uuid4())
    
    # Determine extension
    ext = ".jpg"
    if file.content_type == "image/png":
        ext = ".png"
    elif file.content_type == "image/webp":
        ext = ".webp"
    elif file.content_type == "image/gif":
        ext = ".gif"

    # Create filename with metadata
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{photo_id}_{timestamp}{ext}"
    
    # Create subdirectory based on citation or default
    subdir = "temp"
    if citation_number:
        # Sanitize citation number for directory name
        safe_citation = "".join(c for c in citation_number if c.isalnum())[:20]
        subdir = safe_citation
    
    target_dir = UPLOAD_DIR / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = target_dir / safe_filename

    # Write file
    with open(file_path, "wb") as f:
        f.write(content)

    return UploadResponse(
        photo_id=photo_id,
        filename=file.name,
        size=len(content),
        uploaded_at=datetime.now(timezone.utc).isoformat(),
    )


@router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: str):
    """
    Delete an uploaded photo.
    """
    # Search for the file
    for subdir in UPLOAD_DIR.iterdir():
        if subdir.is_dir():
            for file in subdir.glob(f"{photo_id}_*"):
                file.unlink()
                return {"message": "Photo deleted", "photo_id": photo_id}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Photo not found",
    )
