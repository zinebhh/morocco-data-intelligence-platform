"""DAG : Entraînement et évaluation du classifieur NLP."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "nlp-team",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="11_nlp_classification",
    description="Classification NLP des publications par domaine de recherche",
    default_args=default_args,
    start_date=datetime(2026, 9, 1),
    schedule_interval="@weekly",
    catchup=False,
    tags=["nlp", "classification", "ml"],
) as dag:

    check_data = BashOperator(
        task_id="check_data",
        bash_command="""
        python -c "
from nlp.classification.data_loader import load_publications
df = load_publications()
assert len(df) >= 50, f'Pas assez de données: {len(df)}'
print(f'OK: {len(df)} publications')
"
        """,
    )

    train_task = BashOperator(
        task_id="train_classifier",
        bash_command="cd /opt/airflow && python -m nlp.classification.train_classifier",
    )

    verify_task = BashOperator(
        task_id="verify_model",
        bash_command="""
        python -c "
import joblib
from nlp.classification.config import CLASSIFIER_PATH, LABEL_ENCODER_PATH
clf = joblib.load(CLASSIFIER_PATH)
le = joblib.load(LABEL_ENCODER_PATH)
print(f'Modèle OK - {len(le.classes_)} classes')
"
        """,
    )

    check_data >> train_task >> verify_task