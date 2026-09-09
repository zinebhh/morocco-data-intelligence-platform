"""
Transformation Spark des données OpenAlex
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, schema_of_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
import logging

logger = logging.getLogger(__name__)

def create_spark_session(app_name="OpenAlexTransformer"):
    """Créer une session Spark"""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def transform_openalex_data(spark, input_path, output_path):
    """
    Transformer les données OpenAlex pour l'analytique
    """
    logger.info(f"Lecture des données depuis: {input_path}")
    
    # Lire les données JSON
    df = spark.read.json(input_path)
    
    # Afficher le schéma
    logger.info("Schéma des données:")
    df.printSchema()
    
    # Sélectionner les colonnes importantes
    transformed_df = df.select(
        col("source_id").alias("id"),
        col("title"),
        col("publication_year"),
        col("publication_date"),
        col("doi"),
        col("journal"),
        col("research_field"),
        col("citation_count"),
        col("source"),
        col("authors"),
        col("institutions"),
        col("keywords")
    )
    
    # Filtrer les doublons
    transformed_df = transformed_df.dropDuplicates(["id"])
    
    # Compter
    count = transformed_df.count()
    logger.info(f"✅ {count} publications transformées")
    
    # Sauvegarder
    transformed_df.write \
        .mode("overwrite") \
        .parquet(output_path)
    
    logger.info(f"✅ Données sauvegardées dans: {output_path}")
    
    return transformed_df

if __name__ == "__main__":
    spark = create_spark_session()
    
    # Chemins
    input_path = "data_engineering/ingestion/raw/*.json"
    output_path = "data_engineering/transformations/openalex_transformed"
    
    transform_openalex_data(spark, input_path, output_path)