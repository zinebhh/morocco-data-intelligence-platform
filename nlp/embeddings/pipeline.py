"""
Pipeline Embeddings + Semantic Search
"""
import logging
from pathlib import Path
import pandas as pd
import numpy as np

from nlp.embeddings.chunker import PublicationChunker
from nlp.embeddings.embedder import Embedder
from nlp.embeddings.elastic_indexer import ElasticIndexer

logger = logging.getLogger(__name__)


def run_embedding_pipeline(csv_path: str, recreate_index: bool = True) -> dict:
    """Pipeline complet: chunk → embed → index"""
    logger.info("=" * 60)
    logger.info("🚀 PIPELINE EMBEDDINGS + SEMANTIC SEARCH")
    logger.info("=" * 60)
    
    # 1. Charger
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} publications chargées")
    
    # 2. Chunker
    chunker = PublicationChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_dataframe(df)
    logger.info(f"📦 {len(chunks)} chunks créés")
    
    if not chunks:
        raise ValueError("❌ Aucun chunk créé")
    
    # 3. Embedder
    embedder = Embedder("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = embedder.embed_chunks(chunks)
    logger.info(f"🧠 Embeddings: {embeddings.shape}")
    
    # 4. Indexer
    indexer = ElasticIndexer()
    indexer.create_index(
        embedding_dim=embedder.embedding_dim,
        force_recreate=recreate_index
    )
    indexer.index_chunks(chunks, embeddings)
    
    stats = indexer.get_stats()
    logger.info(f"✅ {stats}")
    
    return stats


def semantic_search_example(query: str, top_k: int = 5):
    """Exemple de recherche sémantique"""
    embedder = Embedder()
    indexer = ElasticIndexer()
    
    query_vec = embedder.embed_query(query)
    
    logger.info(f"🔍 Recherche: '{query}'")
    results = indexer.semantic_search(query_vec, top_k=top_k)
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. [{r['score']:.3f}] {r['title']}")
        print(f"   Topic {r.get('main_topic')} | {r.get('publication_year')} | {r['chunk_type']}")
        print(f"   {r['text'][:150]}...")
    
    return results


if __name__ == "__main__":
    # Test
    csv = "/opt/airflow/nlp/data/openalex_with_topics.csv"
    run_embedding_pipeline(csv, recreate_index=True)
    
    # Exemple
    semantic_search_example(
        "applications of artificial intelligence in Moroccan universities"
    )