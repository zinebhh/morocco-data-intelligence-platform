"""
DAG 14: Export NLP data vers PostgreSQL pour Metabase
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
    'retry_delay': timedelta(minutes=2),
}


def export_nlp_data(**context):
    """Exporter les publications avec topics vers PostgreSQL"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    import pandas as pd
    import json
    from pathlib import Path
    from sqlalchemy import create_engine
    
    # Connexion PostgreSQL (base analytics)
    PG_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/analytics"
    engine = create_engine(PG_URL)
    
    # Charger les données NLP
    csv_path = Path("/opt/airflow/nlp/data/openalex_with_topics.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} introuvable")
    
    df = pd.read_csv(csv_path)
    logger.info(f"{len(df)} publications chargees")
    
    # Ajouter le nom du topic (depuis topics.json)
    topics_path = Path("/opt/airflow/nlp/topic_modeling/output/topics.json")
    with open(topics_path) as f:
        topics_data = json.load(f)
    
    # Créer une table de mapping topic_id -> mots-clés
    topic_names = {}
    for tid, words in topics_data['topics'].items():
        topic_names[int(tid)] = ", ".join(words[:5])
    
    df['topic_keywords'] = df['main_topic'].map(topic_names)
    
    # Ajouter le nom du domaine de recherche (classification)
    # Mapping manuel basé sur les topics identifiés
    topic_labels = {
        0: "Université & Étudiants",
        1: "Qualité & Évaluation",
        2: "Enseignement Supérieur & Innovation",
        3: "IA & Apprentissage",
        4: "Recherche & Société",
    }
    df['research_domain'] = df['main_topic'].map(topic_labels)
    
    # Colonnes utiles pour Metabase
    export_cols = [
        'openalex_id', 'title', 'publication_year', 'doi',
        'main_topic', 'topic_probability', 'topic_keywords', 'research_domain',
    ]
    
    # Garder seulement ce qui existe
    export_cols = [c for c in export_cols if c in df.columns]
    df_export = df[export_cols].copy()
    
    # Écrire dans PostgreSQL
    table_name = 'nlp_publications'
    df_export.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False,
        method='multi',
        chunksize=500
    )
    logger.info(f"{len(df_export)} lignes ecrites dans {table_name}")
    
    # Créer aussi une table des topics
    topics_df = pd.DataFrame([
        {
            'topic_id': int(tid),
            'keywords': ", ".join(words),
            'label': topic_labels.get(int(tid), f"Topic {tid}")
        }
        for tid, words in topics_data['topics'].items()
    ])
    topics_df.to_sql('nlp_topics', engine, if_exists='replace', index=False)
    logger.info(f"{len(topics_df)} topics ecrits dans nlp_topics")
    
    # Stats du modèle
    metrics_dir = Path("/opt/airflow/nlp/classification/output")
    metrics_rows = []
    for f in metrics_dir.glob("metrics_*.json"):
        with open(f) as fp:
            m = json.load(fp)
            metrics_rows.append({
                'model_type': m.get('model_type'),
                'accuracy': m.get('accuracy'),
                'precision': m.get('precision'),
                'recall': m.get('recall'),
                'f1_score': m.get('f1_score'),
                'train_size': m.get('train_size'),
                'test_size': m.get('test_size'),
                'num_classes': m.get('num_classes'),
            })
    
    if metrics_rows:
        metrics_df = pd.DataFrame(metrics_rows)
        metrics_df.to_sql('nlp_model_metrics', engine, if_exists='replace', index=False)
        logger.info(f"{len(metrics_df)} modeles dans nlp_model_metrics")
    
    return {
        "publications": len(df_export),
        "topics": len(topics_df),
        "models": len(metrics_rows)
    }


with DAG(
    '14_export_nlp_to_postgres',
    default_args=default_args,
    description='Export NLP data vers PostgreSQL pour Metabase',
    schedule_interval=None,
    catchup=False,
    tags=['nlp', 'metabase', 'export']
) as dag:
    
    start = DummyOperator(task_id='start')
    export = PythonOperator(task_id='export_nlp', python_callable=export_nlp_data)
    end = DummyOperator(task_id='end')
    
    start >> export >> end