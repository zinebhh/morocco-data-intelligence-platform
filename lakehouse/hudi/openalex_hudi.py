"""
Création des tables Hudi pour OpenAlex
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import logging

logger = logging.getLogger(__name__)

def create_hudi_table(spark, input_path, table_name, base_path):
    """
    Créer une table Hudi
    """
    from pyspark.sql.functions import lit
    from pyspark.sql.types import StringType
    
    # Lire les données transformées
    df = spark.read.parquet(input_path)
    
    # Ajouter des métadonnées
    df = df.withColumn("updated_at", current_timestamp())
    df = df.withColumn("_hoodie_record_key", col("id"))
    df = df.withColumn("_hoodie_partition_path", 
                       col("publication_year").cast(StringType()))
    
    # Configuration Hudi
    hudi_options = {
        'hoodie.table.name': table_name,
        'hoodie.datasource.write.recordkey.field': 'id',
        'hoodie.datasource.write.partitionpath.field': 'publication_year',
        'hoodie.datasource.write.table.type': 'COPY_ON_WRITE',
        'hoodie.datasource.write.operation': 'upsert',
        'hoodie.cleaner.policy': 'KEEP_LATEST_FILE_VERSIONS',
        'hoodie.cleaner.fileversions.retained': 5,
        'hoodie.parquet.compression.codec': 'snappy',
        'hoodie.datasource.hive_sync.enable': 'true',
        'hoodie.datasource.hive_sync.database': 'edudata',
        'hoodie.datasource.hive_sync.table': table_name,
        'hoodie.datasource.hive_sync.partition_fields': 'publication_year',
        'hoodie.datasource.hive_sync.partition_extractor_class': 'org.apache.hudi.hive.MultiPartKeysValueExtractor'
    }
    
    # Écrire la table Hudi
    df.write.format("hudi") \
        .options(**hudi_options) \
        .mode("overwrite") \
        .save(base_path)
    
    logger.info(f"✅ Table Hudi créée: {table_name} dans {base_path}")
    
    return df

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("CreateHudiTables") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
        .getOrCreate()
    
    # Chemins
    input_path = "data_engineering/transformations/openalex_transformed"
    base_path = "lakehouse/hudi/openalex"
    
    create_hudi_table(
        spark,
        input_path,
        "openalex_publications",
        base_path
    )