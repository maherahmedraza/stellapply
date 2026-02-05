import logging
from io import BytesIO
from typing import Optional
from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import MaxRetryError

from src.core.config import settings

logger = logging.getLogger(__name__)


class StorageProvider:
    """
    Provider for object storage (MinIO/S3).
    Implements lazy initialization and robust error recovery.
    """

    def __init__(self) -> None:
        self._client: Optional[Minio] = None
        self._buckets_ensured = False

    @property
    def client(self) -> Minio:
        """Lazy initialization of the MinIO client."""
        if self._client is None:
            self._client = Minio(
                settings.storage.ENDPOINT,
                access_key=settings.storage.ACCESS_KEY,
                secret_key=settings.storage.SECRET_KEY,
                secure=settings.storage.SECURE,
            )
        return self._client

    def _ensure_buckets(self) -> None:
        """Ensure required buckets exist. Only runs once."""
        if self._buckets_ensured:
            return

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

        self._buckets_ensured = True

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """Upload a file with retry logic."""
        self._ensure_buckets()

        retries = 3
        for attempt in range(retries):
            try:
                self.client.put_object(
                    bucket_name,
                    object_name,
                    BytesIO(data),
                    length=len(data),
                    content_type=content_type,
                )
                return True
            except (MaxRetryError, S3Error) as e:
                if attempt == retries - 1:
                    logger.error(f"Upload failed after {retries} attempts: {str(e)}")
                    return False
                logger.warning(f"Upload attempt {attempt + 1} failed, retrying...")
            except Exception as e:
                logger.error(f"Unexpected upload error: {str(e)}")
                return False
        return False

    def download_file(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """Download a file with retry logic."""
        retries = 3
        for attempt in range(retries):
            try:
                response = self.client.get_object(bucket_name, object_name)
                try:
                    return response.read()
                finally:
                    response.close()
                    response.release_conn()
            except (MaxRetryError, S3Error) as e:
                if attempt == retries - 1:
                    logger.error(f"Download failed after {retries} attempts: {str(e)}")
                    return None
                logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
            except Exception as e:
                logger.error(f"Unexpected download error: {str(e)}")
                return None
        return None

    def health_check(self) -> bool:
        """Check connection to storage provider."""
        try:
            self.client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False


storage_provider = StorageProvider()
