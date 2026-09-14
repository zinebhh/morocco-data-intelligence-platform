"""
DAG 5: Copie vers Lakehouse (version Pandas)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import os
import shutil
import glob
from pathlib import Path

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def check_source_task(**context):
    """Vérifier que les données transformées existent"""
    source_dir = "/opt/airflow/data_engineering/transformations/output"
    
    files = glob.glob(f"{source_dir}/openalex_transformed.*")
    logger.info(f"📁 {len(files)} fichiers trouvés dans {source_dir}")
    
    if not files:
        raise ValueError(f"❌ Aucun fichier dans {source_dir}")
    
    for f in files:
        size = os.path.getsize(f)
        logger.info(f"   - {os.path.basename(f)} ({size} bytes)")
    
    context['ti'].xcom_push(key='source_files', value=len(files))
    return len(files)


def copy_to_lakehouse_task(**context):
    """Copier les données vers le lakehouse"""
    logger.info("🚀 Copie vers le Lakehouse")
    
    source_dir = Path("/opt/airflow/data_engineering/transformations/output")
    dest_dir = Path("/opt/airflow/lakehouse/openalex_publications")
    
    # Nettoyer la destination
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier les fichiers
    files_copied = 0
    for pattern in ["openalex_transformed.csv", "openalex_transformed.parquet"]:
        source_file = source_dir / pattern
        if source_file.exists():
            dest_file = dest_dir / pattern
            shutil.copy2(source_file, dest_file)
            files_copied += 1
            size = os.path.getsize(dest_file)
            logger.info(f"✅ Copié: {dest_file} ({size} bytes)")
    
    logger.info(f"📊 {files_copied} fichiers copiés vers {dest_dir}")
    
    context['ti'].xcom_push(key='files_copied', value=files_copied)
    return files_copied


def validate_task(**context):
    """Valider la copie"""
    files_copied = context['ti'].xcom_pull(key='files_copied', task_ids='copy_task')
    
    logger.info(f"🔍 Validation: {files_copied} fichiers")
    
    if files_copied == 0:
        raise ValueError("❌ Aucun fichier copié")
    
    # Vérifier les fichiers
    dest_dir = Path("/opt/airflow/lakehouse/openalex_publications")
    files = list(dest_dir.glob("*"))
    logger.info(f"📁 {len(files)} fichiers dans le lakehouse:")
    for f in files:
        logger.info(f"   - {f.name} ({os.path.getsize(f)} bytes)")
    
    return True


with DAG(
    '05_hudi_lakehouse',
    default_args=default_args,
    description='Copie vers le Lakehouse',
    schedule_interval='@daily',
    catchup=False,
    tags=['lakehouse']
) as dag:
    
    start = DummyOperator(task_id='start')
    check_source = PythonOperator(task_id='check_source', python_callable=check_source_task)
    copy_task = PythonOperator(task_id='copy_task', python_callable=copy_to_lakehouse_task)
    validate = PythonOperator(task_id='validate_task', python_callable=validate_task)
    end = DummyOperator(task_id='end')
    
    start >> check_source >> copy_task >> validate >> end