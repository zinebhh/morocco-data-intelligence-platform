import io
import json
import logging
import os
from typing import Any, Optional

from minio import Minio

logger = logging.getLogger(__name__)


class MinIOClient:
    """
    Client centralisé pour le stockage des données dans MinIO.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: bool = False,
    ) -> None:

        self.endpoint = (
            endpoint
            or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        )

        self.access_key = (
            access_key
            or os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        )

        self.secret_key = (
            secret_key
            or os.getenv("MINIO_SECRET_KEY", "minioadmin123")
        )

        self.secure = secure

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        self.raw_bucket = "raw-data"
        self.processed_bucket = "processed-data"
        self.curated_bucket = "curated-data"
        self.errors_bucket = "errors-data"

        self._ensure_buckets()

    def _ensure_buckets(self) -> None:
        buckets = [
            self.raw_bucket,
            self.processed_bucket,
            self.curated_bucket,
            self.errors_bucket,
        ]

        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info("Created MinIO bucket: %s", bucket)

    def upload_json(
        self,
        data: Any,
        object_name: str,
        bucket_type: str = "raw",
        metadata: Optional[dict[str, str]] = None,
    ) -> str:

        bucket_mapping = {
            "raw": self.raw_bucket,
            "processed": self.processed_bucket,
            "curated": self.curated_bucket,
            "errors": self.errors_bucket,
        }

        if bucket_type not in bucket_mapping:
            raise ValueError(
                f"Unknown bucket_type: {bucket_type}"
            )

        bucket_name = bucket_mapping[bucket_type]

        payload = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str,
        ).encode("utf-8")

        self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=io.BytesIO(payload),
            length=len(payload),
            content_type="application/json",
            metadata=metadata,
        )

        uri = f"s3://{bucket_name}/{object_name}"

        logger.info("Uploaded JSON: %s", uri)

        return uri

    def upload_html(
        self,
        html: str,
        object_name: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> str:

        payload = html.encode("utf-8")

        self.client.put_object(
            bucket_name=self.raw_bucket,
            object_name=object_name,
            data=io.BytesIO(payload),
            length=len(payload),
            content_type="text/html",
            metadata=metadata,
        )

        uri = f"s3://{self.raw_bucket}/{object_name}"

        logger.info("Uploaded HTML: %s", uri)

        return uri