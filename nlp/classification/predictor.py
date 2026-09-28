"""
Prédicteur de domaine de recherche
"""
import joblib
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class ResearchFieldPredictor:
    """Prédicteur utilisant le modèle entraîné"""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = "/opt/airflow/nlp/classification/output/classifier_logistic.pkl"
        
        if not Path(model_path).exists():
            raise ValueError(f"❌ Modèle non trouvé: {model_path}")
        
        data = joblib.load(model_path)
        self.model = data['model']
        self.vectorizer = data['vectorizer']
        self.metrics = data.get('metrics', {})
        self.label_names = data.get('label_names', {})
        
        logger.info(f"✅ Modèle chargé ({data.get('model_type', 'unknown')})")
    
    def predict(self, title: str, abstract: str = "") -> Dict:
        """Prédire le domaine d'une publication"""
        text = f"{title} {title} {abstract}"
        X_vec = self.vectorizer.transform([text])
        pred = self.model.predict(X_vec)[0]
        
        result = {
            "topic_id": int(pred),
            "topic_name": self.label_names.get(pred, f"Topic {pred}")
        }
        
        # Probabilités si disponibles
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(X_vec)[0]
            result["confidence"] = float(max(proba))
        else:
            result["confidence"] = None
        
        return result
    
    def predict_batch(self, publications: List[Dict]) -> List[Dict]:
        """Prédire plusieurs publications"""
        results = []
        for pub in publications:
            try:
                pred = self.predict(pub.get('title', ''), pub.get('abstract', ''))
                results.append({**pub, **pred})
            except Exception as e:
                logger.error(f"❌ Erreur: {e}")
                results.append(pub)
        return results


if __name__ == "__main__":
    # Test
    predictor = ResearchFieldPredictor()
    
    test_pubs = [
        {"title": "Deep learning for medical image analysis", "abstract": ""},
        {"title": "Machine learning in Moroccan universities", "abstract": ""},
        {"title": "Climate change impact on agriculture", "abstract": ""},
    ]
    
    for pub in test_pubs:
        result = predictor.predict(pub['title'], pub['abstract'])
        print(f"📄 {pub['title'][:50]}...")
        print(f"   → {result['topic_name']} (confiance: {result['confidence']:.2f})")