"""Configuration pour la classification NLP des publications."""

from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True, parents=True)

CLASSIFIER_PATH = MODELS_DIR / "research_field_classifier.pkl"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"

# Base de données
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "analytics",
    "user": "postgres",
    "password": "postgres",
}

# Colonnes utilisées pour la classification
TEXT_COLUMNS = ["title", "abstract"]
TARGET_COLUMN = "research_field"  # à adapter selon votre schéma

# Hyperparamètres
TFIDF_PARAMS = {
    "max_features": 10000,
    "ngram_range": (1, 2),
    "min_df": 2,
    "max_df": 0.95,
    "stop_words": "english",
}

CLASSIFIER_PARAMS = {
    "n_estimators": 200,
    "max_depth": 50,
    "min_samples_split": 5,
    "random_state": 42,
    "n_jobs": -1,
}

TEST_SIZE = 0.2
RANDOM_STATE = 42