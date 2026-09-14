"""
Spark job - Écriture dans Hudi (Lakehouse)
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, md5, current_timestamp, lit
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session():
    """Créer une session Spark avec Hudi"""
    return SparkSession.builder \
        .appName("HudiETL") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()


def write_to_hudi(spark, parquet_path: str, hudi_path: str, table_name: str):
    """
    Écrire les données Parquet dans Hudi
    """
    logger.info(f"📖 Lecture des données Parquet: {parquet_path}")
    
    df = spark.read.parquet(parquet_path)
    count = df.count()
    logger.info(f"📊 {count} lignes chargées")
    
    if count == 0:
        logger.warning("⚠️ Aucune donnée")
        return
    
    # Préparer le DataFrame
    df = df.withColumn("updated_at", current_timestamp())
    
    # Configuration Hudi
    hudi_options = {
        'hoodie.table.name': table_name,
        'hoodie.datasource.write.recordkey.field': 'id',
        'hoodie.datasource.write.partitionpath.field': 'publication_year',
        'hoodie.datasource.write.table.name': table_name,
        'hoodie.datasource.write.operation': 'upsert',
        'hoodie.datasource.write.precombine.field': 'updated_at',
        'hoodie.datasource.write.table.type': 'COPY_ON_WRITE',
        'hoodie.cleaner.policy': 'KEEP_LATEST_FILE_VERSIONS',
        'hoodie.cleaner.fileversions.retained': 3,
        'hoodie.parquet.compression.codec': 'snappy',
        'hoodie.datasource.hive_sync.enable': 'false',
    }
    
    # Écrire
    df.write.format("hudi") \
        .options(**hudi_options) \
        .mode("overwrite") \
        .save(hudi_path)
    
    logger.info(f"✅ Données écrites dans Hudi: {hudi_path}")
    
    # Vérifier
    result = spark.read.format("hudi").load(hudi_path)
    logger.info(f"📊 Table Hudi: {result.count()} lignes")
    
    return result


if __name__ == "__main__":
    spark = create_spark_session()
    
    parquet_path = "/opt/spark/data_engineering/transformations/output/openalex_parquet"
    hudi_path = "/opt/spark/lakehouse/hudi/openalex_publications"
    
    write_to_hudi(spark, parquet_path, hudi_path, "openalex_publications")
    logger.info("✅ Pipeline Hudi terminé")