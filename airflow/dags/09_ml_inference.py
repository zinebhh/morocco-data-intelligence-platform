"""
DAG 9: Inférence ML (Prédictions)
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


def predict_task(**context):
    """Générer des prédictions"""
    import joblib
    import pandas as pd
    import os
    from sklearn.preprocessing import LabelEncoder
    
    logger.info("🚀 Génération des prédictions")
    
    # Charger le modèle
    model_path = "/opt/airflow/data-science/models/demand_model.pkl"
    
    if not os.path.exists(model_path):
        raise ValueError(f"❌ Modèle non trouvé: {model_path}")
    
    model = joblib.load(model_path)
    logger.info(f"✅ Modèle chargé: {type(model).__name__}")
    
    # Charger les données
    csv_path = "/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv"
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} lignes chargées")
    
    # Préparer les features (AVEC publication_type)
    X = df[['publication_year', 'title_length', 'citation_count', 'publication_type']].copy()
    X['title_length'] = X['title_length'].fillna(0)
    X['publication_year'] = X['publication_year'].fillna(2024)
    X['citation_count'] = X['citation_count'].fillna(0)
    
    # Encoder publication_type (comme à l'entraînement)
    le = LabelEncoder()
    X['publication_type'] = le.fit_transform(X['publication_type'].fillna('unknown'))
    
    logger.info(f"📋 Features: {list(X.columns)}")
    
    # Prédire
    predictions = model.predict(X)
    logger.info(f"✅ {len(predictions)} prédictions générées")
    
    # Ajouter les prédictions
    df['predicted_citations'] = predictions
    df['prediction_error'] = abs(df['citation_count'] - df['predicted_citations'])
    
    # Sauvegarder
    os.makedirs("/opt/airflow/data-science/evaluation", exist_ok=True)
    output_path = "/opt/airflow/data-science/evaluation/predictions.csv"
    df[['id', 'title', 'citation_count', 'predicted_citations', 'prediction_error']].to_csv(output_path, index=False)
    
    logger.info(f"💾 Sauvegardé: {output_path}")
    
    # Statistiques
    stats = {
        'total_predictions': len(predictions),
        'mean_error': float(df['prediction_error'].mean()),
        'max_error': float(df['prediction_error'].max()),
        'min_error': float(df['prediction_error'].min())
    }
    
    logger.info(f"📊 Statistiques: {stats}")
    
    context['ti'].xcom_push(key='predictions_count', value=len(predictions))
    return len(predictions)


with DAG(
    '09_ml_inference',
    default_args=default_args,
    description='Inférence ML',
    schedule_interval='@daily',
    catchup=False,
    tags=['ml', 'inference']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    predict = PythonOperator(
        task_id='predict_task',
        python_callable=predict_task
    )
    
    end = DummyOperator(task_id='end')
    
    start >> predict >> end