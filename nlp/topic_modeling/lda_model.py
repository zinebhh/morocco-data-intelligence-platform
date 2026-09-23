"""
Topic Modeling avec LDA (Latent Dirichlet Allocation)
"""
import pandas as pd
import numpy as np
import logging
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
import matplotlib.pyplot as plt

sys.path.insert(0, "/opt/airflow")
from config.paths import NLP_ENRICHED_CSV, NLP, NLP_DATA
from nlp.preprocessing.text_cleaner import TextCleaner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LDATopicModeler:
    """Topic Modeling avec LDA"""
    
    def __init__(self, num_topics: int = 5):
        self.num_topics = num_topics
        self.dictionary = None
        self.corpus = None
        self.model = None
        self.cleaner = TextCleaner()
        self.stopwords = self._get_stopwords()
        self.coherence_score = None
    
    def _get_stopwords(self) -> set:
        """Charger les stopwords"""
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words('english'))
        except:
            # Fallback si NLTK non disponible
            return {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                    'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 
                    'was', 'are', 'were', 'be', 'been', 'being'}
    
    def prepare_corpus(self, df: pd.DataFrame) -> List[List[str]]:
        """Préparer le corpus de textes"""
        logger.info("🔧 Préparation du corpus")
        
        # Combiner title + abstract
        texts = []
        for _, row in df.iterrows():
            title = str(row.get('title', ''))
            abstract = str(row.get('abstract', ''))
            
            # Combiner (title plus important)
            full_text = f"{title} {title} {abstract}"  # title en double
            
            # Nettoyer
            cleaned = self.cleaner.clean(full_text)
            
            # Supprimer stopwords
            filtered = self.cleaner.remove_stopwords(cleaned, self.stopwords)
            
            # Tokeniser
            tokens = [w for w in filtered.split() if len(w) > 2]
            
            if tokens:
                texts.append(tokens)
        
        logger.info(f"✅ {len(texts)} textes préparés")
        return texts
    
    def train(self, texts: List[List[str]]):
        """Entraîner le modèle LDA"""
        logger.info(f"🚀 Entraînement LDA (k={self.num_topics})")
        
        # Créer le dictionnaire
        self.dictionary = corpora.Dictionary(texts)
        
        # Filtrer les mots rares/communs
        self.dictionary.filter_extremes(
            no_below=2,   # Mot doit apparaître dans au moins 2 documents
            no_above=0.8  # Mot ne doit pas apparaître dans plus de 80% des docs
        )
        
        # Créer le corpus (Bag of Words)
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]
        
        # Entraîner LDA
        self.model = LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            random_state=42,
            passes=10,
            alpha='auto',
            per_word_topics=True
        )
        
        # Calculer la cohérence
        coherence_model = CoherenceModel(
            model=self.model,
            texts=texts,
            dictionary=self.dictionary,
            coherence='c_v'
        )
        self.coherence_score = coherence_model.get_coherence()
        
        logger.info(f"✅ Cohérence: {self.coherence_score:.4f}")
        
        return self.model
    
    def get_topics(self, num_words: int = 10) -> Dict[int, List[str]]:
        """Récupérer les topics"""
        if not self.model:
            raise ValueError("Modèle non entraîné")
        
        topics = {}
        for topic_id in range(self.num_topics):
            words = self.model.show_topic(topic_id, topn=num_words)
            topics[topic_id] = [word for word, _ in words]
        
        return topics
    
    def get_document_topics(self, texts: List[List[str]]) -> List[Tuple[int, float]]:
        """Déterminer le topic principal de chaque document"""
        if not self.model or not self.corpus:
            raise ValueError("Modèle non entraîné")
        
        doc_topics = []
        for bow in self.corpus:
            topics = self.model.get_document_topics(bow)
            if topics:
                main_topic, prob = max(topics, key=lambda x: x[1])
                doc_topics.append((main_topic, prob))
            else:
                doc_topics.append((-1, 0.0))
        
        return doc_topics
    
    def visualize_topics(self, output_path: str = None):
        """Visualiser les topics"""
        if not self.model:
            raise ValueError("Modèle non entraîné")
        
        topics = self.get_topics(num_words=8)
        
        fig, axes = plt.subplots(1, self.num_topics, figsize=(20, 4))
        
        if self.num_topics == 1:
            axes = [axes]
        
        for topic_id in range(self.num_topics):
            words_weights = self.model.show_topic(topic_id, topn=8)
            words = [w for w, _ in words_weights]
            weights = [w for _, w in words_weights]
            
            axes[topic_id].barh(range(len(words)), weights, color='steelblue')
            axes[topic_id].set_yticks(range(len(words)))
            axes[topic_id].set_yticklabels(words)
            axes[topic_id].set_title(f'Topic {topic_id}')
            axes[topic_id].invert_yaxis()
        
        plt.tight_layout()
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            logger.info(f"💾 Graphique sauvegardé: {output_path}")
        
        plt.show()
    
    def save(self, output_dir: str):
        """Sauvegarder le modèle"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le modèle
        self.model.save(str(output_path / "lda_model"))
        self.dictionary.save(str(output_path / "dictionary"))
        
        # Sauvegarder les topics en JSON
        topics = self.get_topics()
        with open(output_path / "topics.json", 'w') as f:
            json.dump({
                "num_topics": self.num_topics,
                "coherence_score": self.coherence_score,
                "topics": {str(k): v for k, v in topics.items()}
            }, f, indent=2)
        
        logger.info(f"💾 Modèle sauvegardé: {output_path}")


def run_topic_modeling(num_topics: int = 5) -> Dict:
    """Fonction principale"""
    logger.info("=" * 60)
    logger.info("🚀 TOPIC MODELING avec LDA")
    logger.info("=" * 60)
    
    # 1. Charger les données
    if not NLP_ENRICHED_CSV.exists():
        logger.warning("⚠️ Fichier enrichi non trouvé, utilisation du CSV original")
        csv_path = OPENALEX_CSV
    else:
        csv_path = NLP_ENRICHED_CSV
    
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} publications chargées")
    
    # 2. Créer le modèle
    modeler = LDATopicModeler(num_topics=num_topics)
    
    # 3. Préparer le corpus
    texts = modeler.prepare_corpus(df)
    
    if len(texts) < 10:
        logger.warning(f"⚠️ Pas assez de textes ({len(texts)})")
        return {"status": "error", "message": "Not enough texts"}
    
    # 4. Entraîner
    modeler.train(texts)
    
    # 5. Récupérer les résultats
    topics = modeler.get_topics()
    doc_topics = modeler.get_document_topics(texts)
    
    # 6. Ajouter les topics au DataFrame
    df['main_topic'] = [t[0] for t in doc_topics]
    df['topic_probability'] = [t[1] for t in doc_topics]
    
    # 7. Sauvegarder
    output_dir = NLP / "topic_modeling" / "output"
    modeler.save(str(output_dir))
    
    # Sauvegarder les données avec topics
    output_csv = NLP_DATA / "openalex_with_topics.csv"
    df.to_csv(output_csv, index=False)
    logger.info(f"💾 Données avec topics: {output_csv}")
    
    # 8. Visualiser
    modeler.visualize_topics(
        output_path=str(NLP / "evaluation" / "topics_visualization.png")
    )
    
    # 9. Résumé
    logger.info("=" * 60)
    logger.info("📊 RÉSULTATS")
    logger.info("=" * 60)
    logger.info(f"Cohérence: {modeler.coherence_score:.4f}")
    logger.info(f"Nombre de topics: {num_topics}")
    logger.info("\nTopics découverts:")
    for topic_id, words in topics.items():
        logger.info(f"  Topic {topic_id}: {', '.join(words[:5])}")
    
    return {
        "status": "success",
        "num_topics": num_topics,
        "coherence": modeler.coherence_score,
        "topics": topics,
        "output_csv": str(output_csv)
    }


if __name__ == "__main__":
    result = run_topic_modeling(num_topics=5)
    print("\n✅ Résultat:", result["status"])