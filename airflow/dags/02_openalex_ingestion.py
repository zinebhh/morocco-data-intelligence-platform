"""
DAG 2: Ingestion OpenAlex
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
import logging
import sys
import json
import requests

sys.path.insert(0, "/opt/airflow")

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

def fetch_openalex(**context):
    """Récupérer les publications OpenAlex"""
    search_query = Variable.get("openalex_search", default_var="Morocco university")
    per_page = int(Variable.get("openalex_per_page", default_var=100))
    year = Variable.get("openalex_year", default_var="2024")
    
    logger.info(f"📡 Recherche: {search_query}")
    
    url = "https://api.openalex.org/works"
    params = {
        "search": search_query,
        "per-page": per_page,
        "filter": f"publication_year:{year}"
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    
    logger.info(f"✅ {len(results)} publications récupérées")
    
    # Sauvegarder
    from pathlib import Path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("/opt/airflow/data_engineering/ingestion/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"openalex_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    context['ti'].xcom_push(key='publications_count', value=len(results))
    return len(results)

with DAG(
    '02_openalex_ingestion',
    default_args=default_args,
    description='Ingestion OpenAlex',
    schedule_interval='@daily',
    catchup=False,
    tags=['openalex']
) as dag:
    
    start = DummyOperator(task_id='start')
    fetch = PythonOperator(task_id='fetch_task', python_callable=fetch_openalex)
    end = DummyOperator(task_id='end')
    
    start >> fetch >> end