"""
Client MinIO pour le Data Lake
"""
from minio import Minio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class MinIOClient:
    """Client MinIO simple"""
    
    def __init__(self):
        self.client = Minio(
            'minio:9000',
            access_key='minioadmin',
            secret_key='minioadmin',
            secure=False
        )
        self._ensure_buckets()
    
    def _ensure_buckets(self):
        """Créer les buckets"""
        buckets = ["raw-data", "processed-data", "lakehouse"]
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"✅ Bucket créé: {bucket}")