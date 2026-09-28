"""
DAG 11: Classification NLP
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


def classification_task(**context):
    """Entraîner les classifieurs"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    
    import pandas as pd
    import json
    from pathlib import Path
    from nlp.classification.classifier import train_all_models
    
    # Chercher le fichier avec topics
    paths = [
        Path("/opt/airflow/nlp/data/openalex_with_topics.csv"),
        Path("/opt/airflow/nlp/data/openalex_enriched.csv"),
        Path("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    ]
    
    csv_path = None
    for p in paths:
        if p.exists():
            csv_path = p
            break
    
    if not csv_path:
        raise ValueError("❌ Aucun fichier trouvé")
    
    logger.info(f"📁 Chargement: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Créer colonne text si manquante
    if 'text' not in df.columns:
        df['text'] = df['title'].fillna('') + ' ' + df.get('abstract', pd.Series([''] * len(df))).fillna('')
    
    # Créer labels si manquants (fallback basé sur le titre)
    if 'main_topic' not in df.columns:
        logger.warning("⚠️ main_topic manquant, création basée sur le titre")
        import re
        def guess_topic(title):
            title_lower = str(title).lower()
            if any(w in title_lower for w in ['ai', 'machine learning', 'deep learning', 'neural']):
                return 0  # IA
            elif any(w in title_lower for w in ['climate', 'environment', 'energy']):
                return 1  # Environnement
            elif any(w in title_lower for w in ['health', 'medical', 'covid']):
                return 2  # Santé
            elif any(w in title_lower for w in ['education', 'university', 'student']):
                return 3  # Éducation
            else:
                return 4  # Autre
        df['main_topic'] = df['title'].apply(guess_topic)
    
    # Entraîner tous les modèles
    results = train_all_models(df)
    
    # Résumé
    best_model = None
    best_acc = 0
    for name, metrics in results.items():
        if "accuracy" in metrics and metrics["accuracy"] > best_acc:
            best_acc = metrics["accuracy"]
            best_model = name
    
    logger.info(f"🏆 Meilleur: {best_model} (accuracy={best_acc:.4f})")
    
    context['ti'].xcom_push(key='best_model', value=best_model)
    context['ti'].xcom_push(key='best_accuracy', value=best_acc)
    
    return best_model


with DAG(
    '11_classification',
    default_args=default_args,
    description='Classification NLP - Domaine de recherche',
    schedule_interval=None,
    catchup=False,
    tags=['nlp', 'classification']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    classification = PythonOperator(
        task_id='classification',
        python_callable=classification_task
    )
    
    end = DummyOperator(task_id='end')
    
    start >> classification >> end