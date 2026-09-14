"""
DAG 6: Export vers PostgreSQL (base analytics)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import os
import pandas as pd
import psycopg2

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def export_task(**context):
    """Export vers PostgreSQL (base analytics)"""
    logger.info("🚀 Export vers PostgreSQL (analytics)")
    
    # 1. Lire le CSV
    csv_path = "/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv"
    
    if not os.path.exists(csv_path):
        raise ValueError(f"❌ Fichier introuvable: {csv_path}")
    
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} lignes à exporter")
    
    if len(df) == 0:
        return 0
    
    # 2. Se connecter à la base ANALYTICS
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user="airflow",
        password="airflow",
        database="analytics"  # ← ICI : analytics (pas airflow)
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # 3. Créer la table (si n'existe pas)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id VARCHAR(64) PRIMARY KEY,
            openalex_id VARCHAR(255),
            title TEXT,
            publication_year INTEGER,
            doi VARCHAR(255),
            citation_count INTEGER DEFAULT 0,
            publication_type VARCHAR(50),
            language VARCHAR(10),
            journal VARCHAR(500),
            is_open_access BOOLEAN DEFAULT FALSE,
            oa_status VARCHAR(50),
            title_length INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.info("✅ Table créée/vérifiée")
    
    # 4. Vider la table
    cur.execute("TRUNCATE TABLE publications")
    
    # 5. Insérer les données
    inserted = 0
    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO publications (
                    id, openalex_id, title, publication_year, doi,
                    citation_count, publication_type, language, journal,
                    is_open_access, oa_status, title_length
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(row['id']),
                str(row['openalex_id']) if pd.notna(row['openalex_id']) else None,
                str(row['title']),
                int(row['publication_year']) if pd.notna(row['publication_year']) else None,
                str(row['doi']) if pd.notna(row['doi']) else None,
                int(row['citation_count']) if pd.notna(row['citation_count']) else 0,
                str(row['publication_type']) if pd.notna(row['publication_type']) else None,
                str(row['language']) if pd.notna(row['language']) else None,
                str(row['journal']) if pd.notna(row['journal']) else None,
                bool(row['is_open_access']) if pd.notna(row['is_open_access']) else False,
                str(row['oa_status']) if pd.notna(row['oa_status']) else None,
                int(row['title_length']) if pd.notna(row['title_length']) else 0
            ))
            inserted += 1
        except Exception as e:
            logger.warning(f"⚠️ Erreur ligne: {e}")
    
    cur.close()
    conn.close()
    
    logger.info(f"✅ {inserted} lignes insérées dans analytics")
    context['ti'].xcom_push(key='inserted_count', value=inserted)
    return inserted


with DAG(
    '06_export_postgres',
    default_args=default_args,
    description='Export vers PostgreSQL (analytics)',
    schedule_interval='@daily',
    catchup=False,
    tags=['postgres']
) as dag:
    
    start = DummyOperator(task_id='start')
    export = PythonOperator(task_id='export_task', python_callable=export_task)
    end = DummyOperator(task_id='end')
    
    start >> export >> end