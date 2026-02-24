"""
Storage Service for handling S3 uploads and file management.
"""
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.aws_region

        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=self.region
            )
            self.is_configured = True
        else:
            self.s3_client = None
            self.is_configured = False
            logger.warning("AWS S3 credentials not configured. S3 storage disabled.")

    def generate_presigned_url(
        self,
        object_name: str,
        file_type: str,
        expiration: int = 3600
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a presigned URL to upload an S3 object.

        :param object_name: string
        :param file_type: string (MIME type)
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Dictionary with upload_url and key, or None if error
        """
        if not self.is_configured or not self.bucket_name:
            logger.error("S3 not configured, cannot generate presigned URL")
            return None

        try:
            # Generate a presigned URL for the S3 object
            # For PUT uploads (simpler for single file upload from frontend)
            response = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name,
                    'ContentType': file_type
                },
                ExpiresIn=expiration
            )

            # For PUT, the response is just the string URL
            return {
                "upload_url": response,
                "key": object_name,
                # Note: public_url assumes public access or that we will generate a GET URL later
                "public_url": f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_name}"
            }
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

# Global service instance
_storage_service = None

def get_storage_service() -> StorageService:
    """Get the global Storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
