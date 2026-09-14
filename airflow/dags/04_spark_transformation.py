"""
DAG 4: Transformation des données (Pandas - version finale)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import os
import glob
import json
import pandas as pd
import hashlib

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def check_data_task(**context):
    """Vérifier que les données existent"""
    raw_dir = "/opt/airflow/data_engineering/ingestion/raw"
    files = glob.glob(f"{raw_dir}/openalex_*.json")
    logger.info(f"📁 {len(files)} fichiers trouvés")
    
    if not files:
        raise ValueError("❌ Aucun fichier OpenAlex")
    
    context['ti'].xcom_push(key='files_count', value=len(files))
    return len(files)


def transform_task(**context):
    """Transformer avec Pandas (robuste)"""
    logger.info("🚀 Transformation avec Pandas")
    
    raw_dir = "/opt/airflow/data_engineering/ingestion/raw"
    output_dir = "/opt/airflow/data_engineering/transformations/output"
    
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(f"{raw_dir}/openalex_*.json")
    logger.info(f"📁 {len(files)} fichiers à traiter")
    
    all_rows = []
    for f in files[:2]:  # Limiter à 2 fichiers pour test
        logger.info(f"📖 Lecture: {os.path.basename(f)}")
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                continue
            
            for item in data:
                doc_id = item.get("id")
                if not doc_id:
                    continue
                
                # Titre
                title = item.get("display_name") or "Sans titre"
                title = str(title).strip()
                
                # Journal
                journal = None
                primary_loc = item.get("primary_location") or {}
                if isinstance(primary_loc, dict):
                    source = primary_loc.get("source") or {}
                    if isinstance(source, dict):
                        journal = source.get("display_name")
                
                # Open access
                oa = item.get("open_access") or {}
                if not isinstance(oa, dict):
                    oa = {}
                
                all_rows.append({
                    "openalex_id": doc_id,
                    "title": title,
                    "publication_year": item.get("publication_year"),
                    "doi": item.get("doi"),
                    "citation_count": item.get("cited_by_count", 0),
                    "publication_type": item.get("type"),
                    "language": item.get("language"),
                    "journal": journal,
                    "is_open_access": oa.get("is_oa", False),
                    "oa_status": oa.get("oa_status")
                })
        except Exception as e:
            logger.error(f"❌ Erreur {f}: {e}")
    
    logger.info(f"📊 {len(all_rows)} lignes chargées")
    
    if not all_rows:
        raise ValueError("❌ Aucune donnée")
    
    # DataFrame
    df = pd.DataFrame(all_rows)
    df["title_length"] = df["title"].str.len()
    df["id"] = df["openalex_id"].apply(lambda x: hashlib.md5(str(x).encode()).hexdigest())
    
    # Filtrer
    df = df[df["title_length"] > 5]
    df = df[df["publication_year"].notna()]
    df = df.drop_duplicates(subset=["openalex_id"])
    
    logger.info(f"✅ {len(df)} lignes après transformation")
    
    # Sauvegarder en CSV (plus simple que Parquet)
    output_file = f"{output_dir}/openalex_transformed.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"💾 Sauvegardé: {output_file}")
    
    # Essayer Parquet aussi
    try:
        output_parquet = f"{output_dir}/openalex_transformed.parquet"
        df.to_parquet(output_parquet, index=False)
        logger.info(f"💾 Sauvegardé Parquet: {output_parquet}")
    except Exception as e:
        logger.warning(f"⚠️ Parquet non disponible: {e}")
    
    context['ti'].xcom_push(key='transformed_count', value=len(df))
    return len(df)


def validate_task(**context):
    count = context['ti'].xcom_pull(key='transformed_count', task_ids='transform_task')
    logger.info(f"🔍 Validation: {count} lignes")
    if count == 0:
        raise ValueError("❌ Aucune donnée")
    return True


with DAG(
    '04_spark_transformation',
    default_args=default_args,
    description='Transformation des données',
    schedule_interval='@daily',
    catchup=False,
    tags=['transformation']
) as dag:
    
    start = DummyOperator(task_id='start')
    check_data = PythonOperator(task_id='check_data', python_callable=check_data_task)
    transform = PythonOperator(task_id='transform_task', python_callable=transform_task)
    validate = PythonOperator(task_id='validate_task', python_callable=validate_task)
    end = DummyOperator(task_id='end')
    
    start >> check_data >> transform >> validate >> end