"""
Classification NLP - Prédire le domaine de recherche
"""
import pandas as pd
import numpy as np
import logging
import sys
import json
import joblib
from pathlib import Path
from typing import Dict, List, Tuple

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchFieldClassifier:
    """Classifieur de domaine de recherche"""
    
    def __init__(self, model_type: str = "logistic"):
        self.model_type = model_type
        self.model = None
        self.vectorizer = None
        self.metrics = {}
        self.label_names = {}
    
    def _create_model(self):
        """Créer le modèle selon le type"""
        if self.model_type == "logistic":
            return LogisticRegression(max_iter=1000, random_state=42)
        elif self.model_type == "random_forest":
            return RandomForestClassifier(n_estimators=100, random_state=42)
        elif self.model_type == "naive_bayes":
            return MultinomialNB()
        elif self.model_type == "svm":
            return LinearSVC(random_state=42, max_iter=2000)
        else:
            return LogisticRegression(max_iter=1000, random_state=42)
    
    def prepare_data(self, df: pd.DataFrame, text_column: str = "text", label_column: str = "main_topic"):
        """Préparer les données"""
        logger.info(f"🔧 Préparation des données")
        
        # Vérifier les colonnes
        if text_column not in df.columns:
            # Créer la colonne text si nécessaire
            df['text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
            text_column = 'text'
        
        if label_column not in df.columns:
            raise ValueError(f"❌ Colonne {label_column} manquante")
        
        # Filtrer les lignes valides
        df = df[df[text_column].fillna('').str.len() > 10].copy()
        df = df[df[label_column] >= 0].copy()  # Exclure topic -1
        
        logger.info(f"📊 {len(df)} lignes valides")
        logger.info(f"📋 Distribution des labels:")
        for label, count in df[label_column].value_counts().items():
            logger.info(f"   Topic {label}: {count} publications")
            self.label_names[label] = f"Topic {label}"
        
        X = df[text_column].values
        y = df[label_column].values
        
        return X, y
    
    def train(self, X, y):
        """Entraîner le classifieur"""
        logger.info(f"🚀 Entraînement ({self.model_type})")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Vectorizer TF-IDF
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9,
            stop_words='english'
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Modèle
        self.model = self._create_model()
        self.model.fit(X_train_vec, y_train)
        
        # Prédictions
        y_pred = self.model.predict(X_test_vec)
        
        # Métriques
        self.metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
            "f1_score": f1_score(y_test, y_pred, average='weighted', zero_division=0),
            "model_type": self.model_type,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "num_classes": len(np.unique(y))
        }
        
        logger.info(f"✅ Accuracy: {self.metrics['accuracy']:.4f}")
        logger.info(f"✅ F1-Score: {self.metrics['f1_score']:.4f}")
        logger.info(f"✅ Precision: {self.metrics['precision']:.4f}")
        logger.info(f"✅ Recall: {self.metrics['recall']:.4f}")
        
        # Rapport détaillé
        logger.info("\n📊 Rapport de classification:")
        logger.info(classification_report(y_test, y_pred, zero_division=0))
        
        return self.metrics
    
    def predict(self, texts: List[str]) -> List[int]:
        """Prédire le domaine"""
        if not self.model or not self.vectorizer:
            raise ValueError("❌ Modèle non entraîné")
        
        X_vec = self.vectorizer.transform(texts)
        return self.model.predict(X_vec).tolist()
    
    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Probabilités de prédiction"""
        if not self.model or not self.vectorizer:
            raise ValueError("❌ Modèle non entraîné")
        
        X_vec = self.vectorizer.transform(texts)
        
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_vec)
        else:
            return None
    
    def plot_confusion_matrix(self, X_test, y_test, output_path: str = None):
        """Créer la matrice de confusion"""
        X_vec = self.vectorizer.transform(X_test)
        y_pred = self.model.predict(X_vec)
        
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=[f"Topic {i}" for i in range(len(cm))],
            yticklabels=[f"Topic {i}" for i in range(len(cm))]
        )
        plt.xlabel('Prédit')
        plt.ylabel('Réel')
        plt.title(f'Matrice de confusion ({self.model_type})')
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            logger.info(f"💾 Sauvegardé: {output_path}")
        
        plt.close()
        return cm
    
    def save(self, output_dir: str):
        """Sauvegarder le modèle"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'vectorizer': self.vectorizer,
            'metrics': self.metrics,
            'label_names': self.label_names,
            'model_type': self.model_type
        }, output_path / f"classifier_{self.model_type}.pkl")
        
        with open(output_path / f"metrics_{self.model_type}.json", 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info(f"💾 Modèle sauvegardé: {output_path}")


def train_all_models(df: pd.DataFrame) -> Dict:
    """Entraîner et comparer plusieurs modèles"""
    logger.info("=" * 60)
    logger.info("🚀 CLASSIFICATION NLP - Comparaison de modèles")
    logger.info("=" * 60)
    
    results = {}
    models = ["logistic", "random_forest", "naive_bayes", "svm"]
    
    for model_type in models:
        try:
            logger.info(f"\n{'='*40}")
            logger.info(f"📊 Modèle: {model_type}")
            logger.info(f"{'='*40}")
            
            classifier = ResearchFieldClassifier(model_type=model_type)
            X, y = classifier.prepare_data(df)
            
            if len(X) < 10:
                logger.warning(f"⚠️ Pas assez de données pour {model_type}")
                continue
            
            metrics = classifier.train(X, y)
            results[model_type] = metrics
            
            # Sauvegarder
            output_dir = "/opt/airflow/nlp/classification/output"
            classifier.save(output_dir)
            
        except Exception as e:
            logger.error(f"❌ Erreur {model_type}: {e}")
            results[model_type] = {"error": str(e)}
    
    # Meilleur modèle
    if results:
        best = max(
            [(k, v) for k, v in results.items() if "accuracy" in v],
            key=lambda x: x[1]["accuracy"],
            default=(None, {})
        )
        logger.info(f"\n🏆 Meilleur modèle: {best[0]} (accuracy={best[1].get('accuracy', 0):.4f})")
    
    return results


if __name__ == "__main__":
    # Test
    df = pd.read_csv("/opt/airflow/nlp/data/openalex_with_topics.csv")
    results = train_all_models(df)
    print(json.dumps(results, indent=2))