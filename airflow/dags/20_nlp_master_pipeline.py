"""
DAG 20: Master NLP Pipeline
Orchestre: Topic Modeling -> Classification -> Embeddings -> RAG
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.dummy import DummyOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}


def validate_pipeline(**context):
    """Valider que tous les artefacts existent"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    from pathlib import Path
    import json

    checks = {
        "topics.json": Path("/opt/airflow/nlp/topic_modeling/output/topics.json"),
        "openalex_with_topics.csv": Path("/opt/airflow/nlp/data/openalex_with_topics.csv"),
        "classifier_svm.pkl": Path("/opt/airflow/nlp/classification/output/classifier_svm.pkl"),
        "metrics_svm.json": Path("/opt/airflow/nlp/classification/output/metrics_svm.json"),
    }

    missing = []
    for name, path in checks.items():
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        logger.info(f"{'OK' if exists else 'KO'} {name}: {size} bytes")
        if not exists:
            missing.append(name)

    if missing:
        raise FileNotFoundError(f"Fichiers manquants: {missing}")

    from elasticsearch import Elasticsearch
    es = Elasticsearch(["http://elasticsearch:9200"])
    count = es.count(index="publications_semantic")['count']
    logger.info(f"Elasticsearch: {count} documents indexes")

    if count < 10:
        raise ValueError(f"Trop peu de documents dans ES: {count}")

    import requests
    try:
        r = requests.get("http://ollama:11434/api/tags", timeout=10)
        models = [m['name'] for m in r.json().get('models', [])]
        logger.info(f"Ollama: {models}")
        if not models:
            raise ValueError("Aucun modele Ollama installe")
    except Exception as e:
        raise ConnectionError(f"Ollama inaccessible: {e}")

    with open(checks["topics.json"]) as f:
        topics = json.load(f)

    logger.info("=" * 60)
    logger.info("PIPELINE NLP COMPLET VALIDE")
    logger.info(f"   Topics: {topics['num_topics']}")
    logger.info(f"   Coherence LDA: {topics['coherence']:.4f}")
    logger.info(f"   Embeddings: {count} chunks")
    logger.info(f"   LLM: {models}")
    logger.info("=" * 60)

    context['ti'].xcom_push(key='total_chunks', value=count)
    return {"status": "success", "chunks": count}


with DAG(
    '20_nlp_master_pipeline',
    default_args=default_args,
    description='Master NLP Pipeline - Orchestration complete',
    schedule='@weekly',
    catchup=False,
    max_active_runs=1,
    tags=['nlp', 'master', 'orchestration']
) as dag:

    start = DummyOperator(task_id='start')

    trigger_topic_modeling = TriggerDagRunOperator(
        task_id='trigger_topic_modeling',
        trigger_dag_id='10_topic_modeling',
        wait_for_completion=True,
        poke_interval=30,
        allowed_states=['success'],
        failed_states=['failed'],
        reset_dag_run=True,
    )

    trigger_classification = TriggerDagRunOperator(
        task_id='trigger_classification',
        trigger_dag_id='11_classification',
        wait_for_completion=True,
        poke_interval=30,
        allowed_states=['success'],
        failed_states=['failed'],
        reset_dag_run=True,
    )

    trigger_embeddings = TriggerDagRunOperator(
        task_id='trigger_embeddings',
        trigger_dag_id='12_embeddings_semantic',
        wait_for_completion=True,
        poke_interval=30,
        allowed_states=['success'],
        failed_states=['failed'],
        reset_dag_run=True,
    )

    trigger_rag = TriggerDagRunOperator(
        task_id='trigger_rag_test',
        trigger_dag_id='13_rag_assistant',
        wait_for_completion=True,
        poke_interval=30,
        allowed_states=['success'],
        failed_states=['failed'],
        reset_dag_run=True,
    )

    validate = PythonOperator(
        task_id='validate_pipeline',
        python_callable=validate_pipeline
    )

    end = DummyOperator(task_id='end')

    start >> trigger_topic_modeling >> trigger_classification >> trigger_embeddings >> trigger_rag >> validate >> end