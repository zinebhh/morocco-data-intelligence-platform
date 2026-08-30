"""
Ingestion des données dans MinIO
"""
from minio import Minio
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinIOIngestor:
    """Ingestion des données dans MinIO"""
    
    def __init__(self):
        self.client = Minio(
            'localhost:9000',
            access_key='minioadmin',
            secret_key='minioadmin',
            secure=False
        )
        self.bucket = 'raw-data'
        
        # Créer le bucket s'il n'existe pas
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            logger.info(f"Bucket {self.bucket} créé")
    
    def ingest_json(self, data, filename):
        """Ingérer des données JSON dans MinIO"""
        try:
            # Ajouter la date pour versionner
            date_str = datetime.now().strftime("%Y%m%d")
            object_name = f"universities/{date_str}/{filename}"
            
            # Convertir en JSON
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            # Upload
            self.client.put_object(
                self.bucket,
                object_name,
                data=json_data.encode('utf-8'),
                length=len(json_data),
                content_type='application/json'
            )
            logger.info(f"Données ingérées: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Erreur d'ingestion: {e}")
            return False

if __name__ == "__main__":
    ingestor = MinIOIngestor()
    test_data = {"test": "data"}
    ingestor.ingest_json(test_data, "test.json")