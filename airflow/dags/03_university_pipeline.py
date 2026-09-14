"""
DAG 3: Pipeline complet
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
import logging
import sys
from pathlib import Path

sys.path.insert(0, "/opt/airflow")

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def scrape_task(**context):
    from data_engineering.ingestion.scrapers.universities_scraper import scrape_university
    
    university_name = Variable.get("scrape_university_name", default_var="Université Hassan II")
    university_url = Variable.get("scrape_university_url", default_var="https://www.univh2c.ma/")
    max_pages = int(Variable.get("scrape_max_pages", default_var=5))
    
    result = scrape_university(university_name, university_url, max_pages)
    context['ti'].xcom_push(key='output_dir', value=result.get('output_dir'))
    context['ti'].xcom_push(key='pages_count', value=result.get('pages_scraped', 0))
    return result

def upload_task(**context):
    from minio import Minio
    
    output_dir = context['ti'].xcom_pull(key='output_dir', task_ids='scrape_task')
    if not output_dir:
        return 0
    
    client = Minio('minio:9000', access_key='minioadmin', secret_key='minioadmin', secure=False)
    bucket = "raw-data"
    
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
    
    university_name = Variable.get("scrape_university_name", default_var="Université Hassan II")
    prefix = f"universities/{university_name.lower().replace(' ', '_')}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    files = 0
    for html_file in Path(output_dir).glob("*.html"):
        object_name = f"{prefix}/{timestamp}/{html_file.name}"
        client.fput_object(bucket, object_name, str(html_file))
        files += 1
    
    logger.info(f"✅ {files} fichiers uploadés")
    return files

with DAG(
    '03_university_pipeline',
    default_args=default_args,
    description='Pipeline complet Scraping + MinIO',
    schedule_interval='@weekly',
    catchup=False,
    tags=['complete']
) as dag:
    
    start = DummyOperator(task_id='start')
    scrape = PythonOperator(task_id='scrape_task', python_callable=scrape_task)
    upload = PythonOperator(task_id='upload_task', python_callable=upload_task)
    end = DummyOperator(task_id='end')
    
    start >> scrape >> upload >> end