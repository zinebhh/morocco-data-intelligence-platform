"""Évaluation du classifieur : accuracy, precision, recall, F1, matrice de confusion."""

import logging
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report, confusion_matrix,
)

logger = logging.getLogger(__name__)


def evaluate_model(clf, X_test, y_test, label_encoder) -> dict:
    """Retourne un dict de métriques."""
    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="weighted", zero_division=0
    )

    report = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        output_dict=True, zero_division=0,
    )
    cm = confusion_matrix(y_test, y_pred).tolist()

    logger.info(f"\n📊 Accuracy  : {accuracy:.4f}")
    logger.info(f"📊 Precision : {precision:.4f}")
    logger.info(f"📊 Recall    : {recall:.4f}")
    logger.info(f"📊 F1-score  : {f1:.4f}")
    logger.info(f"\n📋 Classification report:\n{classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0)}")

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "classes": list(label_encoder.classes_),
        "classification_report": report,
        "confusion_matrix": cm,
    }