"""
DAG 8: Entraînement des modèles ML
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


def train_demand_model(**context):
    """Entraîner le modèle de prédiction"""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import r2_score
    import joblib
    import os
    
    logger.info("🚀 Entraînement du modèle de demande")
    
    csv_path = "/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv"
    df = pd.read_csv(csv_path)
    
    # Features
    X = df[['publication_year', 'title_length', 'citation_count']].copy()
    X['title_length'] = X['title_length'].fillna(0)
    X['publication_year'] = X['publication_year'].fillna(2024)
    
    # Encoder le type
    le = LabelEncoder()
    if 'publication_type' in df.columns:
        X['publication_type'] = le.fit_transform(df['publication_type'].fillna('unknown'))
    
    y = df['citation_count'].fillna(0)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraîner
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Évaluer
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"✅ R²: {r2:.4f}")
    
    # Sauvegarder
    os.makedirs("/opt/airflow/data-science/models", exist_ok=True)
    joblib.dump(model, "/opt/airflow/data-science/models/demand_model.pkl")
    
    context['ti'].xcom_push(key='r2_score', value=r2)
    return r2


def train_clustering_model(**context):
    """Entraîner le clustering"""
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    import joblib
    import os
    
    logger.info("🚀 Entraînement du clustering")
    
    csv_path = "/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv"
    df = pd.read_csv(csv_path)
    
    # Features
    features = df[['publication_year', 'citation_count', 'title_length']].dropna()
    
    if len(features) < 10:
        logger.warning("⚠️ Pas assez de données")
        return 0
    
    # Scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # KMeans
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    
    # Score
    silhouette = silhouette_score(X_scaled, labels)
    
    logger.info(f"✅ Silhouette Score: {silhouette:.4f}")
    
    # Sauvegarder
    os.makedirs("/opt/airflow/data-science/models", exist_ok=True)
    joblib.dump({
        'model': kmeans,
        'scaler': scaler,
        'score': silhouette
    }, "/opt/airflow/data-science/models/clustering_model.pkl")
    
    context['ti'].xcom_push(key='silhouette_score', value=silhouette)
    return silhouette


def save_metrics(**context):
    """Sauvegarder les métriques"""
    import json
    import os
    
    r2 = context['ti'].xcom_pull(key='r2_score', task_ids='train_demand')
    silhouette = context['ti'].xcom_pull(key='silhouette_score', task_ids='train_clustering')
    
    metrics = {
        'demand_model_r2': r2,
        'clustering_silhouette': silhouette,
        'timestamp': datetime.now().isoformat()
    }
    
    os.makedirs("/opt/airflow/data-science/evaluation", exist_ok=True)
    with open("/opt/airflow/data-science/evaluation/metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"✅ Métriques sauvegardées: {metrics}")
    return metrics


with DAG(
    '08_ml_training',
    default_args=default_args,
    description='Entraînement des modèles ML',
    schedule_interval='@weekly',
    catchup=False,
    tags=['ml', 'data-science']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    train_demand = PythonOperator(
        task_id='train_demand',
        python_callable=train_demand_model
    )
    
    train_clustering = PythonOperator(
        task_id='train_clustering',
        python_callable=train_clustering_model
    )
    
    save = PythonOperator(
        task_id='save_metrics',
        python_callable=save_metrics
    )
    
    end = DummyOperator(task_id='end')
    
    start >> [train_demand, train_clustering] >> save >> end