"""Prédiction du domaine de recherche pour de nouvelles publications."""

import logging
import joblib
from nlp.classification.config import CLASSIFIER_PATH, LABEL_ENCODER_PATH
from nlp.classification.feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)


class ResearchFieldPredictor:
    """Prédit le domaine d'une publication."""

    def __init__(self):
        self.clf = joblib.load(CLASSIFIER_PATH)
        self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
        self.extractor = FeatureExtractor.load()
        logger.info("✅ Modèle chargé")

    def predict(self, title: str, abstract: str = "") -> dict:
        """Retourne le label prédit + probabilités."""
        text = f"{title} {abstract}".strip()
        X = self.extractor.transform([text])

        pred_idx = self.clf.predict(X)[0]
        probas = self.clf.predict_proba(X)[0]

        label = self.label_encoder.inverse_transform([pred_idx])[0]
        confidence = float(probas[pred_idx])

        # Top 3
        top3_idx = probas.argsort()[-3:][::-1]
        top3 = [
            {"label": self.label_encoder.inverse_transform([i])[0], "score": float(probas[i])}
            for i in top3_idx
        ]

        return {
            "predicted_label": label,
            "confidence": confidence,
            "top_3": top3,
        }


if __name__ == "__main__":
    predictor = ResearchFieldPredictor()
    result = predictor.predict(
        title="Deep learning methods for detecting cancer in medical images",
    )
    print(result)