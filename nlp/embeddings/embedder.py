"""
Génération d'embeddings avec Sentence Transformers
"""
import logging
import numpy as np
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class Embedder:
    """Générateur d'embeddings"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Modèles recommandés:
        - all-MiniLM-L6-v2 (rapide, 384 dim) ← par défaut
        - all-mpnet-base-v2 (meilleur, 768 dim)
        - BAAI/bge-small-en-v1.5 (bon compromis, 384 dim)
        - BAAI/bge-base-en-v1.5 (meilleur, 768 dim)
        """
        from sentence_transformers import SentenceTransformer
        
        logger.info(f"🔧 Chargement du modèle: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"✅ Modèle chargé (dim={self.embedding_dim})")
    
    def embed_texts(self, texts: List[str], batch_size: int = 32, 
                    show_progress: bool = True) -> np.ndarray:
        """Générer les embeddings pour une liste de textes"""
        logger.info(f"🧠 Génération de {len(texts)} embeddings...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,  # Important pour cosine similarity
            convert_to_numpy=True
        )
        
        logger.info(f"✅ Embeddings: shape={embeddings.shape}")
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embedding d'une requête"""
        return self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )[0]
    
    def embed_chunks(self, chunks: List[Dict]) -> np.ndarray:
        """Embeddings pour une liste de chunks"""
        texts = [c['text'] for c in chunks]
        return self.embed_texts(texts)


if __name__ == "__main__":
    embedder = Embedder()
    
    test = ["Machine learning for healthcare", "Climate change impacts"]
    vecs = embedder.embed_texts(test, show_progress=False)
    print(f"Shape: {vecs.shape}")
    print(f"Similarité: {np.dot(vecs[0], vecs[1]):.4f}")