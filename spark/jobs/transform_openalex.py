"""
Spark job - Transformation des données OpenAlex
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, md5, current_timestamp, length, 
    regexp_replace, trim, lower, lit
)
import logging
from pathlib import Path
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_spark_session():
    """Créer une session Spark"""
    return SparkSession.builder \
        .appName("OpenAlexTransformer") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()


def transform_openalex_data(spark, input_pattern: str, output_path: str):
    """
    Transformer les données OpenAlex
    """
    logger.info(f"📖 Lecture des données: {input_pattern}")
    
    # Lire les fichiers JSON
    files = glob.glob(input_pattern)
    if not files:
        logger.error("❌ Aucun fichier trouvé")
        return None
    
    logger.info(f"📁 {len(files)} fichiers trouvés")
    
    # Lire tous les fichiers JSON
    df = spark.read.option("multiline", "true").json(files)
    
    total = df.count()
    logger.info(f"📊 {total} lignes chargées")
    
    if total == 0:
        return None
    
    # Transformer
    transformed_df = df.select(
        col("id").alias("openalex_id"),
        col("display_name").alias("title"),
        col("publication_year").cast("int"),
        col("publication_date"),
        col("doi"),
        col("cited_by_count").cast("int").alias("citation_count"),
        col("type").alias("publication_type"),
        col("language"),
        col("primary_location.source.display_name").alias("journal"),
        col("primary_location.source.type").alias("source_type"),
        col("open_access.is_oa").alias("is_open_access"),
        col("open_access.oa_status").alias("oa_status")
    )
    
    # Nettoyer
    transformed_df = transformed_df \
        .withColumn("title", 
            when(col("title").isNull(), "Sans titre")
            .otherwise(trim(regexp_replace(col("title"), r"\s+", " ")))) \
        .withColumn("title_length", length(col("title"))) \
        .withColumn("id", md5(col("openalex_id"))) \
        .withColumn("processed_at", current_timestamp())
    
    # Filtrer
    transformed_df = transformed_df.filter(
        (col("title_length") > 5) &
        (col("publication_year").isNotNull()) &
        (col("publication_year") >= 1900)
    )
    
    # Dédupliquer
    transformed_df = transformed_df.dropDuplicates(["openalex_id"])
    
    final_count = transformed_df.count()
    logger.info(f"✅ {final_count} lignes après transformation")
    
    # Sauvegarder en Parquet
    transformed_df.write \
        .mode("overwrite") \
        .partitionBy("publication_year") \
        .parquet(output_path)
    
    logger.info(f"💾 Données sauvegardées: {output_path}")
    
    return transformed_df


if __name__ == "__main__":
    spark = create_spark_session()
    
    input_pattern = "/opt/spark/data_engineering/ingestion/raw/openalex_*.json"
    output_path = "/opt/spark/data_engineering/transformations/output/openalex_parquet"
    
    result = transform_openalex_data(spark, input_pattern, output_path)
    
    if result:
        result.show(5, truncate=50)
        logger.info("✅ Transformation terminée")
    else:
        logger.error("❌ Aucune donnée à transformer")