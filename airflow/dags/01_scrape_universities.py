"""
DAG 1: Scraping des universités marocaines
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def scrape_university_task(**context):
    from data_engineering.ingestion.scrapers.universities_scraper import scrape_university
    
    university_name = Variable.get("scrape_university_name", default_var="Université Hassan II")
    university_url = Variable.get("scrape_university_url", default_var="https://www.univh2c.ma/")
    max_pages = int(Variable.get("scrape_max_pages", default_var=10))
    
    logger.info(f"🚀 Scraping: {university_name}")
    result = scrape_university(university_name, university_url, max_pages)
    
    context['ti'].xcom_push(key='pages_count', value=result.get('pages_scraped', 0))
    context['ti'].xcom_push(key='output_dir', value=result.get('output_dir'))
    return result

def validate_task(**context):
    pages_count = context['ti'].xcom_pull(key='pages_count', task_ids='scrape_task')
    logger.info(f"🔍 Validation: {pages_count} pages")
    
    if pages_count == 0:
        logger.warning("⚠️ Aucune page scrappée")
        return False
    return True

with DAG(
    'scrape_universities',
    default_args=default_args,
    description='Scraping des universités marocaines',
    schedule_interval='@weekly',
    catchup=False,
    max_active_runs=1,
    tags=['scraping', 'universities']
) as dag:
    
    start = DummyOperator(task_id='start')
    scrape = PythonOperator(task_id='scrape_task', python_callable=scrape_university_task)
    validate = PythonOperator(task_id='validate_task', python_callable=validate_task)
    end = DummyOperator(task_id='end')
    
    start >> scrape >> validate >> end