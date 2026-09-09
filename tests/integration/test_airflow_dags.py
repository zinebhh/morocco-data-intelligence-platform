"""
Tests d'intégration pour les DAGs Airflow
"""
import pytest
from airflow.models import DagBag
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def test_dag_loading():
    """Vérifier que tous les DAGs se chargent correctement"""
    dag_bag = DagBag(dag_folder=str(PROJECT_ROOT / "airflow" / "dags"))
    
    assert dag_bag.import_errors == {}, f"Erreurs d'import: {dag_bag.import_errors}"
    
    dags = dag_bag.dags
    assert len(dags) > 0, "Aucun DAG trouvé"
    
    for dag_id in dags:
        print(f"✅ DAG chargé: {dag_id}")

def test_openalex_dag_structure():
    """Vérifier la structure du DAG OpenAlex"""
    dag_bag = DagBag(dag_folder=str(PROJECT_ROOT / "airflow" / "dags"))
    dag = dag_bag.get_dag('openalex_ingestion')
    
    assert dag is not None, "DAG openalex_ingestion non trouvé"
    
    tasks = dag.task_dict
    expected_tasks = ['start', 'ingest_openalex', 'validate_data', 'notify_completion', 'end']
    
    for task in expected_tasks:
        assert task in tasks, f"Tâche {task} manquante"
    
    print(f"✅ Structure du DAG OpenAlex valide")