"""
Spark job - Transformation des données universitaires
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, lit, md5, current_timestamp, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from pyspark.sql.functions import regexp_replace, trim, lower
import logging
from bs4 import BeautifulSoup
import re
from pathlib import Path

logger = logging.getLogger(__name__)

def create_spark_session(app_name="UniversityTransformer"):
    """Créer une session Spark"""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .getOrCreate()

def clean_html(html_content: str) -> str:
    """
    Nettoyer le HTML et extraire le texte
    """
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer les scripts et styles
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extraire le texte
        text = soup.get_text(separator=' ', strip=True)
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Nettoyer les caractères spéciaux
        text = re.sub(r'[^\w\s\.\,\;\-\?\!]', '', text)
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Erreur nettoyage HTML: {e}")
        return ""

def extract_title(html_content: str) -> str:
    """Extraire le titre de la page"""
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else ""
        return title.strip() if title else ""
    except:
        return ""

def transform_university_data(spark, input_path: str, output_path: str):
    """
    Transformer les données HTML en données structurées
    
    Args:
        spark: Session Spark
        input_path: Chemin d'entrée (RAW)
        output_path: Chemin de sortie (Parquet)
    """
    logger.info(f"🚀 Lecture des données depuis: {input_path}")
    
    # Schéma pour les données
    schema = StructType([
        StructField("university", StringType(), True),
        StructField("url", StringType(), True),
        StructField("html_content", StringType(), True),
        StructField("title", StringType(), True),
        StructField("clean_text", StringType(), True),
        StructField("page_number", IntegerType(), True),
        StructField("ingestion_date", StringType(), True)
    ])
    
    # Lire les fichiers HTML
    # (Ici on simule la lecture - à adapter selon votre structure)
    
    # Exemple: Créer des données de test
    from pyspark.sql import Row
    test_data = [
        Row(university="Université Hassan II", 
            url="https://www.univh2c.ma/page1.html",
            html_content="<h1>Bienvenue</h1><p>Texte de test</p>",
            page_number=1,
            ingestion_date="2026-09-07")
    ]
    df = spark.createDataFrame(test_data)
    
    logger.info(f"📊 {df.count()} lignes chargées")
    
    # Appliquer les transformations
    logger.info("🔄 Transformation des données...")
    
    # UDFs pour le nettoyage
    clean_html_udf = udf(clean_html, StringType())
    extract_title_udf = udf(extract_title, StringType())
    
    # Transformer
    transformed_df = df \
        .withColumn("clean_text", clean_html_udf(col("html_content"))) \
        .withColumn("title", extract_title_udf(col("html_content"))) \
        .withColumn("content_hash", md5(col("clean_text"))) \
        .withColumn("processed_at", current_timestamp()) \
        .withColumn("text_length", length(col("clean_text"))) \
        .dropDuplicates(["content_hash"])
    
    # Filtrer les pages vides
    transformed_df = transformed_df.filter(
        col("text_length") > 50  # Minimum 50 caractères
    )
    
    # Ajouter des métadonnées
    transformed_df = transformed_df.withColumn("source", lit("university_website"))
    transformed_df = transformed_df.withColumn("pipeline_version", lit("1.0"))
    
    logger.info(f"📊 {transformed_df.count()} lignes après transformation")
    
    # Sauvegarder en Parquet
    transformed_df.write \
        .mode("overwrite") \
        .partitionBy("university") \
        .parquet(output_path)
    
    logger.info(f"💾 Données sauvegardées dans: {output_path}")
    
    return transformed_df

if __name__ == "__main__":
    # Test
    spark = create_spark_session()
    
    input_path = "data_engineering/ingestion/raw/universities"
    output_path = "data_engineering/transformations/output/universities_parquet"
    
    result = transform_university_data(spark, input_path, output_path)
    result.show(5, truncate=50)