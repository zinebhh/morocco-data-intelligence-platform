"""Extraction de features (TF-IDF) pour la classification."""

import logging
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from nlp.classification.config import TFIDF_PARAMS, VECTORIZER_PATH
from nlp.preprocessing.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Wrapper autour de TF-IDF avec nettoyage intégré."""

    def __init__(self, **params):
        self.params = {**TFIDF_PARAMS, **params}
        self.vectorizer = TfidfVectorizer(**self.params)
        self.cleaner = TextCleaner()

    def fit(self, texts: list) -> "FeatureExtractor":
        cleaned = [self.cleaner.clean(t) for t in texts]
        self.vectorizer.fit(cleaned)
        logger.info(f"✅ TF-IDF fit : {len(self.vectorizer.vocabulary_)} features")
        return self

    def transform(self, texts: list):
        cleaned = [self.cleaner.clean(t) for t in texts]
        return self.vectorizer.transform(cleaned)

    def fit_transform(self, texts: list):
        cleaned = [self.cleaner.clean(t) for t in texts]
        return self.vectorizer.fit_transform(cleaned)

    def save(self, path=VECTORIZER_PATH):
        joblib.dump(self.vectorizer, path)
        logger.info(f"💾 Vectorizer sauvegardé : {path}")

    @classmethod
    def load(cls, path=VECTORIZER_PATH):
        extractor = cls()
        extractor.vectorizer = joblib.load(path)
        return extractor