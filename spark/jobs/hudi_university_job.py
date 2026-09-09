"""
Job Spark pour transformer et écrire dans Hudi
"""
import sys
from pathlib import Path
from datetime import datetime
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, md5, concat, current_timestamp, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# Ajouter le projet au PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from data_engineering.lakehouse.hudi.hudi_writer import HudiWriter, create_hudi_table_from_parquet
from data_engineering.lakehouse.hudi.hudi_config import HudiConfig
from data_engineering.transformations.spark.transform_university_html import clean_html, extract_title

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Créer une session Spark avec Hudi"""
    return SparkSession.builder \
        .appName("HudiUniversityJob") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
        .getOrCreate()

def transform_data_for_hudi(spark, raw_path: str):
    """
    Transformer les données brutes pour Hudi
    
    Args:
        spark: Session Spark
        raw_path: Chemin des données brutes
        
    Returns:
        DataFrame: Données transformées
    """
    logger.info(f"📖 Lecture des données brutes: {raw_path}")
    
    # Lire les données
    df = spark.read.text(raw_path).withColumnRenamed("value", "html_content")
    
    # Ajouter des colonnes
    df = df.withColumn("university", lit("Université Hassan II"))
    df = df.withColumn("url", lit("https://www.univh2c.ma/"))
    
    # Nettoyer
    from pyspark.sql.functions import udf
    clean_html_udf = udf(clean_html, StringType())
    extract_title_udf = udf(extract_title, StringType())
    
    transformed_df = df \
        .withColumn("clean_text", clean_html_udf(col("html_content"))) \
        .withColumn("title", extract_title_udf(col("html_content"))) \
        .withColumn("id", md5(col("url"))) \
        .withColumn("content_hash", md5(col("clean_text"))) \
        .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d"))) \
        .withColumn("processed_at", current_timestamp()) \
        .withColumn("text_length", length(col("clean_text"))) \
        .filter(col("text_length") > 50) \
        .dropDuplicates(["content_hash"])
    
    logger.info(f"✅ {transformed_df.count()} lignes transformées")
    
    return transformed_df

def run_hudi_pipeline():
    """
    Exécuter le pipeline complet avec Hudi
    """
    logger.info("=" * 60)
    logger.info("🚀 PIPELINE HUDI - UNIVERSITÉS")
    logger.info("=" * 60)
    
    # 1. Créer la session Spark
    spark = create_spark_session()
    logger.info("✅ Session Spark créée")
    
    # 2. Transformer les données
    raw_path = "data_engineering/ingestion/raw/universities/*/*/page_*.html"
    transformed_df = transform_data_for_hudi(spark, raw_path)
    
    if transformed_df.count() == 0:
        logger.warning("⚠️ Aucune donnée à traiter")
        return
    
    # 3. Écrire dans Hudi
    writer = HudiWriter(spark)
    config = HudiConfig(table_name="universities")
    
    result = writer.write_university_data(
        transformed_df,
        config=config,
        mode="upsert"
    )
    
    # 4. Vérifier
    logger.info("📊 Vérification de la table Hudi")
    table_df = writer.read_table("universities")
    logger.info(f"📊 Table Hudi: {table_df.count()} lignes")
    
    # 5. Afficher un échantillon
    logger.info("📝 Échantillon des données:")
    table_df.select("id", "university", "title", "text_length").show(5, truncate=50)
    
    logger.info("=" * 60)
    logger.info("✅ PIPELINE HUDI TERMINÉ")
    logger.info("=" * 60)
    
    return result

if __name__ == "__main__":
    run_hudi_pipeline()