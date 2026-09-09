"""
Configuration pour Apache Hudi
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class HudiConfig:
    """Configuration des tables Hudi"""
    
    # Configuration générale
    base_path: str = "lakehouse/hudi"
    table_name: str = "universities"
    
    # Options Hudi
    options: dict = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {
                'hoodie.table.name': self.table_name,
                'hoodie.datasource.write.recordkey.field': 'id',
                'hoodie.datasource.write.partitionpath.field': 'university',
                'hoodie.datasource.write.table.type': 'COPY_ON_WRITE',
                'hoodie.datasource.write.operation': 'upsert',
                'hoodie.cleaner.policy': 'KEEP_LATEST_FILE_VERSIONS',
                'hoodie.cleaner.fileversions.retained': 5,
                'hoodie.parquet.compression.codec': 'snappy',
                'hoodie.datasource.hive_sync.enable': 'false',
                'hoodie.datasource.hive_sync.database': 'edudata',
                'hoodie.datasource.hive_sync.table': self.table_name,
                'hoodie.datasource.hive_sync.partition_fields': 'university',
                'hoodie.datasource.hive_sync.partition_extractor_class': 'org.apache.hudi.hive.MultiPartKeysValueExtractor'
            }

# Configuration pour chaque table
UNIVERSITY_HUDI_CONFIG = HudiConfig(table_name="universities")
PUBLICATION_HUDI_CONFIG = HudiConfig(table_name="publications")
PROGRAM_HUDI_CONFIG = HudiConfig(table_name="programs")