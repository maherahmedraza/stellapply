import logging
from io import BytesIO

from minio import Minio

from src.core.config import settings

logger = logging.getLogger(__name__)


class StorageProvider:
    """Provider for object storage (MinIO/S3)."""

    def __init__(self) -> None:
        self.client = Minio(
            settings.storage.ENDPOINT,
            access_key=settings.storage.ACCESS_KEY,
            secret_key=settings.storage.SECRET_KEY,
            secure=settings.storage.SECURE,
        )
        self._ensure_buckets()

    def _ensure_buckets(self) -> None:
        """Ensure required buckets exist."""
        buckets = [
            settings.storage.BUCKET_RESUMES,
            settings.storage.BUCKET_ASSETS,
            "audit-archive",
        ]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created storage bucket: {bucket}")
            except Exception as e:
                logger.error(f"Failed to ensure bucket {bucket}: {str(e)}")

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """Upload a file to the specified bucket."""
        try:
            self.client.put_object(
                bucket_name,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            return True
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False


storage_provider = StorageProvider()
