"""
DAG pour l'ingestion des données des universités marocaines
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

def scrape_universities():
    """Scraper les données des universités marocaines"""
    # TODO: Implémenter le scraping
    print("Scraping des universités marocaines...")
    pass

def ingest_to_minio():
    """Ingérer les données dans MinIO"""
    # TODO: Implémenter l'ingestion
    print("Ingestion vers MinIO...")
    pass

with DAG(
    'ingest_universities',
    default_args=default_args,
    description='Ingestion des universités marocaines',
    schedule_interval='@daily',
    catchup=False,
    tags=['ingestion', 'universities']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    scrape = PythonOperator(
        task_id='scrape_universities',
        python_callable=scrape_universities
    )
    
    ingest = PythonOperator(
        task_id='ingest_to_minio',
        python_callable=ingest_to_minio
    )
    
    end = DummyOperator(task_id='end')
    
    start >> scrape >> ingest >> end