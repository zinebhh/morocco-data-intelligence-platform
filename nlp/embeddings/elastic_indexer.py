"""
Indexation des embeddings dans Elasticsearch
"""
import logging
from typing import List, Dict
from elasticsearch import Elasticsearch, helpers

logger = logging.getLogger(__name__)


class ElasticIndexer:
    """Gestion de l'index Elasticsearch avec vecteurs denses"""
    
    def __init__(self, host: str = "elasticsearch", port: int = 9200, 
                 index_name: str = "publications_semantic"):
        self.es = Elasticsearch([f"http://{host}:{port}"])
        self.index_name = index_name
        
        if not self.es.ping():
            raise ConnectionError(f"❌ Impossible de se connecter à Elasticsearch ({host}:{port})")
        
        logger.info(f"✅ Connecté à Elasticsearch ({host}:{port})")
    
    def create_index(self, embedding_dim: int, force_recreate: bool = False):
        """Créer l'index avec mapping pour dense_vector + BM25"""
        
        if self.es.indices.exists(index=self.index_name):
            if force_recreate:
                logger.info(f"🗑️  Suppression de l'index existant: {self.index_name}")
                self.es.indices.delete(index=self.index_name)
            else:
                logger.info(f"✅ Index existant: {self.index_name}")
                return
        
        mapping = {
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "openalex_id": {"type": "keyword"},
                    "text": {
                        "type": "text",
                        "analyzer": "english"  # BM25 classique
                    },
                    "title": {"type": "text"},
                    "publication_year": {"type": "integer"},
                    "main_topic": {"type": "integer"},
                    "topic_probability": {"type": "float"},
                    "doi": {"type": "keyword"},
                    "chunk_type": {"type": "keyword"},
                    "position": {"type": "integer"},
                    # ⭐ Le vecteur dense
                    "embedding": {
                        "type": "dense_vector",
                        "dims": embedding_dim,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        self.es.indices.create(index=self.index_name, body=mapping)
        logger.info(f"✅ Index créé: {self.index_name} (dim={embedding_dim})")
    
    def index_chunks(self, chunks: List[Dict], embeddings, batch_size: int = 100):
        """Indexer les chunks avec leurs embeddings"""
        logger.info(f"📥 Indexation de {len(chunks)} chunks...")
        
        actions = []
        for chunk, emb in zip(chunks, embeddings):
            doc = {
                **{k: v for k, v in chunk.items() if k != 'embedding'},
                'embedding': emb.tolist()
            }
            actions.append({
                "_index": self.index_name,
                "_id": chunk['chunk_id'],
                "_source": doc
            })
        
        success, errors = helpers.bulk(
            self.es, actions, chunk_size=batch_size, raise_on_error=False
        )
        
        logger.info(f"✅ {success} chunks indexés ({len(errors)} erreurs)")
        return success
    
    def semantic_search(self, query_embedding, top_k: int = 10) -> List[Dict]:
        """Recherche par similarité cosinus (kNN)"""
        response = self.es.search(
            index=self.index_name,
            body={
                "knn": {
                    "field": "embedding",
                    "query_vector": query_embedding.tolist(),
                    "k": top_k,
                    "num_candidates": top_k * 10
                },
                "_source": ["chunk_id", "openalex_id", "title", "text", 
                           "main_topic", "publication_year", "chunk_type"]
            }
        )
        
        return [{"score": h["_score"], **h["_source"]} for h in response["hits"]["hits"]]
    
    def hybrid_search(self, query: str, query_embedding, top_k: int = 10,
                      alpha: float = 0.5) -> List[Dict]:
        """
        Recherche hybride: BM25 + kNN
        alpha=0 → BM25 pur, alpha=1 → vecteurs purs
        """
        response = self.es.search(
            index=self.index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["text^2", "title^3"]
                    }
                },
                "knn": {
                    "field": "embedding",
                    "query_vector": query_embedding.tolist(),
                    "k": top_k,
                    "num_candidates": top_k * 10,
                    "boost": alpha * 2
                },
                "size": top_k,
                "_source": ["chunk_id", "openalex_id", "title", "text",
                           "main_topic", "publication_year", "chunk_type"]
            }
        )
        
        return [{"score": h["_score"], **h["_source"]} for h in response["hits"]["hits"]]
    
    def get_stats(self) -> Dict:
        """Statistiques de l'index"""
        count = self.es.count(index=self.index_name)['count']
        return {
            "index": self.index_name,
            "total_docs": count,
            "size_mb": self.es.indices.stats(index=self.index_name)['_all']['total']['store']['size_in_bytes'] / 1024 / 1024
        }