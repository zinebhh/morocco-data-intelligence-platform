"""
DAG 12: Embeddings + Semantic Search
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def embeddings_task(**context):
    """Générer et indexer les embeddings"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    
    from pathlib import Path
    from nlp.embeddings.pipeline import run_embedding_pipeline
    
    csv_path = Path("/opt/airflow/nlp/data/openalex_with_topics.csv")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"❌ {csv_path} introuvable - lancez d'abord 10_topic_modeling")
    
    stats = run_embedding_pipeline(str(csv_path), recreate_index=True)
    
    context['ti'].xcom_push(key='total_docs', value=stats.get('total_docs', 0))
    return stats


def test_search_task(**context):
    """Tester la recherche sémantique"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    
    from nlp.embeddings.pipeline import semantic_search_example
    
    queries = [
        "artificial intelligence in education",
        "climate change",
        "medical applications of machine learning"
    ]
    
    for q in queries:
        logger.info(f"\n{'='*60}")
        semantic_search_example(q, top_k=3)


with DAG(
    '12_embeddings_semantic',
    default_args=default_args,
    description='Embeddings + Semantic Search (Elasticsearch)',
    schedule_interval=None,
    catchup=False,
    tags=['nlp', 'embeddings', 'elasticsearch', 'rag']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    embeddings = PythonOperator(
        task_id='embeddings',
        python_callable=embeddings_task
    )
    
    test = PythonOperator(
        task_id='test_search',
        python_callable=test_search_task
    )
    
    end = DummyOperator(task_id='end')
    
    start >> embeddings >> test >> end