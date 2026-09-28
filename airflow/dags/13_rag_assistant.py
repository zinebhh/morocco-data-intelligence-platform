"""
DAG 13: Test du RAG Assistant
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
    'retry_delay': timedelta(minutes=3),
}


def test_rag_task(**context):
    """Tester le RAG avec plusieurs questions"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    from nlp.rag.rag_pipeline import RAGPipeline
    
    rag = RAGPipeline(top_k=5)
    
    questions = [
        "Quels sont les principaux domaines de recherche dans les universités marocaines ?",
        "Comment l'IA est-elle utilisée dans l'éducation au Maroc ?",
        "Quelles sont les préoccupations environnementales au Maroc ?",
    ]
    
    results = []
    for q in questions:
        r = rag.ask(q)
        logger.info(f"\n❓ {q}\n💬 {r['answer'][:200]}...")
        results.append({
            "question": q,
            "answer_length": len(r['answer']),
            "num_sources": len(r['sources'])
        })
    
    context['ti'].xcom_push(key='results', value=results)
    return results


with DAG(
    '13_rag_assistant',
    default_args=default_args,
    description='RAG Assistant - Q&A sur publications',
    schedule_interval=None,
    catchup=False,
    tags=['nlp', 'rag', 'llm']
) as dag:
    
    start = DummyOperator(task_id='start')
    test_rag = PythonOperator(task_id='test_rag', python_callable=test_rag_task)
    end = DummyOperator(task_id='end')
    
    start >> test_rag >> end