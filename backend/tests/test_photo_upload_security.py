import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile, HTTPException
from src.routes.photos import upload_photo

@pytest.mark.asyncio
async def test_upload_large_file_prevention():
    """
    Test that uploading a large file is rejected WITHOUT reading the content.
    """
    # Mock UploadFile
    mock_file = MagicMock(spec=UploadFile)
    mock_file.file = MagicMock()
    # Mock file size to be larger than MAX_FILE_SIZE (10MB)
    # 100MB
    mock_file.file.tell.return_value = 100 * 1024 * 1024
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "large_image.jpg"

    # Mock read to fail if called
    # This simulates that we don't want to read a large file into memory
    mock_file.read = AsyncMock(side_effect=Exception("VULNERABILITY: Read was called on large file!"))

    # Call the function directly to test logic
    try:
        await upload_photo(file=mock_file)
        pytest.fail("Should have raised HTTPException")
    except HTTPException as e:
        # If the code reads the file first, it will trigger the exception from mock_file.read
        # So reaching here means it might have passed reading (if we didn't mock side_effect)
        # OR it raised HTTPException after reading.
        # But our mock raises Exception on read.
        pass
    except Exception as e:
        if str(e) == "VULNERABILITY: Read was called on large file!":
            # This is expected for the vulnerability reproduction
            # We want to fail the test if this happens, to confirm the vulnerability exists
            pytest.fail("Vulnerability confirmed: upload_photo read the entire file into memory!")
        raise e
