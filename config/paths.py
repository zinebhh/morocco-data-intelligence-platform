"""
Configuration des chemins du projet
"""
import os
from pathlib import Path

# Détecter si on est dans Docker
IN_DOCKER = os.path.exists("/opt/airflow")

if IN_DOCKER:
    PROJECT_ROOT = Path("/opt/airflow")
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Chemins principaux
DATA_ENGINEERING = PROJECT_ROOT / "data_engineering"
DATA_SCIENCE = PROJECT_ROOT / "data-science"
NLP = PROJECT_ROOT / "nlp"
LAKEHOUSE = PROJECT_ROOT / "lakehouse"

# Données
RAW_DATA = DATA_ENGINEERING / "ingestion" / "raw"
PROCESSED_DATA = DATA_ENGINEERING / "transformations" / "output"
NLP_DATA = NLP / "data"

# Fichiers
OPENALEX_CSV = PROCESSED_DATA / "openalex_transformed.csv"
NLP_ENRICHED_CSV = NLP_DATA / "openalex_enriched.csv"

# Créer les dossiers
for folder in [NLP_DATA, NLP / "models", NLP / "evaluation"]:
    folder.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"IN_DOCKER: {IN_DOCKER}")
    print(f"OPENALEX_CSV: {OPENALEX_CSV}")
    print(f"Existe: {OPENALEX_CSV.exists()}")