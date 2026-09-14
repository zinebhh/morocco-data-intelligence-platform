"""
Spark job - Export vers PostgreSQL
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import logging
import psycopg2
from psycopg2.extras import execute_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_postgres_connection():
    """Connexion PostgreSQL"""
    return psycopg2.connect(
        host="postgres",
        port=5432,
        user="airflow",
        password="airflow",
        database="analytics"
    )


def export_parquet_to_postgres(parquet_path: str):
    """Exporter les données Parquet vers PostgreSQL"""
    logger.info("🚀 Export vers PostgreSQL")
    
    spark = SparkSession.builder \
        .appName("ExportToPostgres") \
        .getOrCreate()
    
    # Lire les données
    df = spark.read.parquet(parquet_path)
    count = df.count()
    logger.info(f"📊 {count} lignes à exporter")
    
    if count == 0:
        return
    
    # Collecter les données
    rows = df.collect()
    
    # Connexion PostgreSQL
    conn = get_postgres_connection()
    cur = conn.cursor()
    
    # Insérer les données
    insert_query = """
        INSERT INTO publications (
            id, openalex_id, title, publication_year, publication_date,
            doi, citation_count, publication_type, language, journal,
            source_type, is_open_access, oa_status, title_length, processed_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            citation_count = EXCLUDED.citation_count,
            updated_at = CURRENT_TIMESTAMP
    """
    
    data = [
        (
            row['id'], row['openalex_id'], row['title'],
            row['publication_year'], row['publication_date'],
            row['doi'], row['citation_count'], row['publication_type'],
            row['language'], row['journal'], row['source_type'],
            row['is_open_access'], row['oa_status'],
            row['title_length'], row['processed_at']
        )
        for row in rows
    ]
    
    execute_batch(cur, insert_query, data, page_size=100)
    conn.commit()
    
    logger.info(f"✅ {len(data)} lignes exportées")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    parquet_path = "/opt/spark/data_engineering/transformations/output/openalex_parquet"
    export_parquet_to_postgres(parquet_path)