import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.app import app
from src.services.storage import StorageService

client = TestClient(app)

@pytest.fixture
def mock_storage_service():
    with patch("src.routes.photos.get_storage_service") as mock:
        service = MagicMock(spec=StorageService)
        mock.return_value = service
        yield service

def test_presigned_url_success(mock_storage_service):
    mock_storage_service.is_configured = True
    mock_storage_service.generate_presigned_url.return_value = {
        "upload_url": "https://s3.example.com/upload",
        "key": "uploads/test.jpg",
        "public_url": "https://public.example.com/test.jpg"
    }

    response = client.post("/api/photos/presigned-url", json={
        "filename": "test.jpg",
        "content_type": "image/jpeg"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["upload_url"] == "https://s3.example.com/upload"
    assert data["key"] == "uploads/test.jpg"
    assert "photo_id" in data

def test_presigned_url_not_configured(mock_storage_service):
    mock_storage_service.is_configured = False

    response = client.post("/api/photos/presigned-url", json={
        "filename": "test.jpg",
        "content_type": "image/jpeg"
    })

    assert response.status_code == 501
    assert response.json()["detail"] == "S3 storage is not configured"

def test_presigned_url_invalid_type(mock_storage_service):
    mock_storage_service.is_configured = True

    response = client.post("/api/photos/presigned-url", json={
        "filename": "test.txt",
        "content_type": "text/plain"
    })

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
