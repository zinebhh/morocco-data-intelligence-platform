"""
Retriever - récupération de contexte pour le RAG
"""
import logging
from typing import List, Dict
import sys
sys.path.insert(0, "/opt/airflow")

from nlp.embeddings.embedder import Embedder
from nlp.embeddings.elastic_indexer import ElasticIndexer

logger = logging.getLogger(__name__)


class Retriever:
    """Récupère les chunks pertinents pour une question"""
    
    def __init__(self, top_k: int = 5, use_hybrid: bool = True):
        self.top_k = top_k
        self.use_hybrid = use_hybrid
        self.embedder = Embedder("sentence-transformers/all-MiniLM-L6-v2")
        self.indexer = ElasticIndexer()
        logger.info(f"✅ Retriever prêt (top_k={top_k}, hybrid={use_hybrid})")
    
    def retrieve(self, query: str) -> List[Dict]:
        """Récupérer les chunks les plus pertinents"""
        query_vec = self.embedder.embed_query(query)
        
        if self.use_hybrid:
            results = self.indexer.hybrid_search(query, query_vec, top_k=self.top_k)
        else:
            results = self.indexer.semantic_search(query_vec, top_k=self.top_k)
        
        # Dédupliquer par openalex_id (garder le meilleur score par publication)
        seen = {}
        for r in results:
            oid = r.get('openalex_id')
            if oid not in seen or r['score'] > seen[oid]['score']:
                seen[oid] = r
        
        deduped = sorted(seen.values(), key=lambda x: -x['score'])
        logger.info(f"🔍 {len(results)} chunks → {len(deduped)} publications uniques")
        return deduped
    
    def format_context(self, results: List[Dict], max_chars_per_doc: int = 500) -> str:
        """Formater les résultats en contexte pour le LLM"""
        context_parts = []
        for i, r in enumerate(results, 1):
            text = r.get('text', '')[:max_chars_per_doc]
            context_parts.append(
                f"[Source {i}] {r.get('title', 'Sans titre')} "
                f"({r.get('publication_year', 'N/A')})\n{text}"
            )
        return "\n\n---\n\n".join(context_parts)


if __name__ == "__main__":
    retriever = Retriever(top_k=3)
    results = retriever.retrieve("artificial intelligence in education")
    print(retriever.format_context(results))