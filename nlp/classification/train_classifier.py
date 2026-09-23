"""Entraînement du classifieur de domaine de recherche."""

import logging
import joblib
import json
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from nlp.classification.config import (
    CLASSIFIER_PARAMS, TEST_SIZE, RANDOM_STATE,
    CLASSIFIER_PATH, LABEL_ENCODER_PATH, MODELS_DIR,
)
from nlp.classification.data_loader import load_publications, build_text_column
from nlp.classification.feature_extractor import FeatureExtractor
from nlp.classification.evaluate_classifier import evaluate_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def train():
    # 1. Chargement des données
    logger.info("📥 Chargement des publications...")
    df = load_publications()
    df = build_text_column(df)

    if len(df) < 50:
        raise ValueError(f"Pas assez de données ({len(df)}) pour entraîner le modèle")

    # 2. Encodage des labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["research_field"])
    logger.info(f"🏷️ {len(label_encoder.classes_)} classes : {list(label_encoder.classes_)}")

    # 3. Split train/test
    X_text_train, X_text_test, y_train, y_test = train_test_split(
        df["text"].tolist(), y,
        test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y,
    )

    # 4. Extraction de features
    logger.info("🔢 Extraction TF-IDF...")
    extractor = FeatureExtractor()
    X_train = extractor.fit_transform(X_text_train)
    X_test = extractor.transform(X_text_test)

    # 5. Entraînement
    logger.info("🤖 Entraînement RandomForest...")
    clf = RandomForestClassifier(**CLASSIFIER_PARAMS)
    clf.fit(X_train, y_train)

    # 6. Évaluation
    logger.info("📊 Évaluation...")
    metrics = evaluate_model(clf, X_test, y_test, label_encoder)

    # 7. Sauvegarde
    joblib.dump(clf, CLASSIFIER_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    extractor.save()
    logger.info(f"💾 Modèle sauvegardé : {CLASSIFIER_PATH}")

    # 8. Métriques JSON (pour Airflow XCom / Metabase)
    metrics_file = MODELS_DIR / f"metrics_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    logger.info(f"✅ Entraînement terminé. Accuracy = {metrics['accuracy']:.4f}")
    return metrics


if __name__ == "__main__":
    train()