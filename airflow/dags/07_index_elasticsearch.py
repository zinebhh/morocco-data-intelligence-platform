"""
DAG 7: Indexation Elasticsearch (version Pandas)
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import os
import pandas as pd
import json

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def check_data_task(**context):
    """Vérifier les données"""
    csv_path = "/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv"
    
    if not os.path.exists(csv_path):
        raise ValueError(f"❌ Fichier introuvable: {csv_path}")
    
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} lignes à indexer")
    
    if len(df) == 0:
        raise ValueError("❌ Aucune donnée")
    
    context['ti'].xcom_push(key='rows_count', value=len(df))
    return len(df)


def index_elasticsearch_task(**context):
    """Indexer dans Elasticsearch"""
    from elasticsearch import Elasticsearch, helpers
    
    logger.info("🚀 Indexation Elasticsearch")
    
    # 1. Connexion
    es = Elasticsearch(
        hosts=["http://elasticsearch:9200"],
        request_timeout=60,
        max_retries=3,
        retry_on_timeout=True
    )
    
    if not es.ping():
        raise Exception("❌ Impossible de se connecter à Elasticsearch")
    
    logger.info("✅ Connecté à Elasticsearch")
    
    index_name = "publications"
    
    # 2. Créer l'index
    if not es.indices.exists(index=index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "standard"},
                    "publication_year": {"type": "integer"},
                    "doi": {"type": "keyword"},
                    "citation_count": {"type": "integer"},
                    "publication_type": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "journal": {"type": "text"},
                    "is_open_access": {"type": "boolean"}
                }
            }
        }
        es.indices.create(index=index_name, body=mapping)
        logger.info(f"✅ Index créé: {index_name}")
    else:
        logger.info(f"✅ Index existe: {index_name}")
    
    # 3. Lire le CSV
    csv_path = "/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv"
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} lignes à indexer")
    
    # 4. Préparer les documents
    actions = []
    for _, row in df.iterrows():
        doc = {
            "_index": index_name,
            "_id": str(row['id']),
            "_source": {
                "title": str(row['title']) if pd.notna(row['title']) else "",
                "publication_year": int(row['publication_year']) if pd.notna(row['publication_year']) else None,
                "doi": str(row['doi']) if pd.notna(row['doi']) else None,
                "citation_count": int(row['citation_count']) if pd.notna(row['citation_count']) else 0,
                "publication_type": str(row['publication_type']) if pd.notna(row['publication_type']) else None,
                "language": str(row['language']) if pd.notna(row['language']) else None,
                "journal": str(row['journal']) if pd.notna(row['journal']) else None,
                "is_open_access": bool(row['is_open_access']) if pd.notna(row['is_open_access']) else False
            }
        }
        actions.append(doc)
    
    # 5. Indexer par batch
    if actions:
        success, errors = helpers.bulk(es, actions, raise_on_error=False, chunk_size=100)
        logger.info(f"✅ {success} documents indexés")
        if errors:
            logger.warning(f"⚠️ {len(errors)} erreurs")
    
    # 6. Rafraîchir
    es.indices.refresh(index=index_name)
    
    # 7. Compter
    count = es.count(index=index_name)
    total = count['count']
    logger.info(f"📊 Total dans l'index: {total}")
    
    context['ti'].xcom_push(key='indexed_count', value=total)
    return total


def verify_task(**context):
    """Vérifier l'index"""
    from elasticsearch import Elasticsearch
    
    logger.info("🔍 Vérification de l'index")
    
    es = Elasticsearch(hosts=["http://elasticsearch:9200"])
    
    count = es.count(index="publications")
    total = count['count']
    logger.info(f"📊 Total dans Elasticsearch: {total}")
    
    # Recherche test
    result = es.search(
        index="publications",
        body={"query": {"match": {"title": "ChatGPT"}}, "size": 3}
    )
    
    hits = result['hits']['hits']
    logger.info(f"🔍 Recherche 'ChatGPT': {len(hits)} résultats")
    for hit in hits:
        logger.info(f"   - {hit['_source']['title'][:80]}...")
    
    if total == 0:
        raise ValueError("❌ Aucune donnée dans Elasticsearch")
    
    return total


with DAG(
    '07_index_elasticsearch',
    default_args=default_args,
    description='Indexation Elasticsearch',
    schedule_interval='@daily',
    catchup=False,
    tags=['elasticsearch']
) as dag:
    
    start = DummyOperator(task_id='start')
    check = PythonOperator(task_id='check_data', python_callable=check_data_task)
    index = PythonOperator(task_id='index_task', python_callable=index_elasticsearch_task)
    verify = PythonOperator(task_id='verify_task', python_callable=verify_task)
    end = DummyOperator(task_id='end')
    
    start >> check >> index >> verify >> end