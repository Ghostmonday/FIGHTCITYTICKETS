"""
Storage Service for S3 interactions.

Handles generating presigned URLs for file uploads and retrievals.
"""

import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

from ..config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing S3 storage."""

    def __init__(self):
        """Initialize Storage service with AWS credentials."""
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.aws_region

        # Check if S3 is configured
        self.is_configured = bool(
            settings.aws_access_key_id
            and settings.aws_secret_access_key
            and settings.s3_bucket_name
            and settings.s3_bucket_name != "change-me"
        )

        if self.is_configured:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region,
                )
            except Exception:
                logger.exception("Failed to initialize S3 client")
                self.is_configured = False
        else:
            logger.warning(
                "AWS S3 credentials not configured. Storage service disabled."
            )

    def generate_presigned_url(
        self, object_name: str, file_type: str, expiration: int = 3600
    ) -> dict[str, Any] | None:
        """
        Generate a presigned URL to share an S3 object.

        Args:
            object_name: The name of the key to use in S3
            file_type: The content type of the file (e.g., 'image/jpeg')
            expiration: Time in seconds for the presigned URL to remain valid

        Returns:
            Dictionary with upload URL and fields, or None if error/not configured.
            Using generate_presigned_url for PUT requests.
        """
        if not self.is_configured:
            logger.warning(
                "Storage service not configured, cannot generate presigned URL"
            )
            return None

        try:
            # Generate a presigned URL for the S3 client to invoke an action
            # on your behalf.
            url = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                    "ContentType": file_type,
                },
                ExpiresIn=expiration,
            )

            # Return the URL and the key (for reference)
            public_url = (
                f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/"
                f"{object_name}"
            )
            return {
                "upload_url": url,
                "key": object_name,
                "public_url": public_url,
            }
        except ClientError:
            logger.exception("Error generating presigned URL")
            return None
        except Exception:
            logger.exception("Unexpected error in storage service")
            return None


# Global service instance
_storage_service = None


def get_storage_service() -> StorageService:
    """Get the global Storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
