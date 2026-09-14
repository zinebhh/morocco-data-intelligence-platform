"""
Spark job - Indexation dans Elasticsearch
"""
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_es_client():
    """Client Elasticsearch"""
    return Elasticsearch(
        hosts=["http://elasticsearch:9200"],
        request_timeout=30
    )


def create_index(es, index_name: str):
    """Créer l'index avec mapping"""
    if es.indices.exists(index=index_name):
        logger.info(f"Index {index_name} existe déjà")
        return
    
    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text", "analyzer": "standard"},
                "publication_year": {"type": "integer"},
                "doi": {"type": "keyword"},
                "citation_count": {"type": "integer"},
                "publication_type": {"type": "keyword"},
                "language": {"type": "keyword"},
                "journal": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "is_open_access": {"type": "boolean"},
                "oa_status": {"type": "keyword"},
            }
        }
    }
    
    es.indices.create(index=index_name, body=mapping)
    logger.info(f"✅ Index créé: {index_name}")


def index_publications(es, index_name: str, json_pattern: str):
    """Indexer les publications"""
    logger.info(f"📖 Lecture: {json_pattern}")
    
    files = glob.glob(json_pattern)
    if not files:
        logger.warning("⚠️ Aucun fichier")
        return 0
    
    actions = []
    total = 0
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            continue
        
        for item in data:
            doc = {
                "_index": index_name,
                "_id": item.get("id", ""),
                "_source": {
                    "title": item.get("display_name", ""),
                    "publication_year": item.get("publication_year"),
                    "doi": item.get("doi"),
                    "citation_count": item.get("cited_by_count", 0),
                    "publication_type": item.get("type"),
                    "language": item.get("language"),
                    "journal": (item.get("primary_location", {}) or {}).get("source", {}).get("display_name"),
                    "is_open_access": (item.get("open_access", {}) or {}).get("is_oa", False),
                    "oa_status": (item.get("open_access", {}) or {}).get("oa_status"),
                }
            }
            
            if doc["_id"] and doc["_source"]["title"]:
                actions.append(doc)
        
        total += len(data)
        
        # Indexer par batch
        if len(actions) >= 500:
            success, errors = bulk(es, actions, raise_on_error=False)
            logger.info(f"✅ Batch indexé: {success} documents")
            actions = []
    
    # Dernier batch
    if actions:
        success, errors = bulk(es, actions, raise_on_error=False)
        logger.info(f"✅ Dernier batch: {success} documents")
    
    logger.info(f"✅ Total: {total} documents traités")
    return total


if __name__ == "__main__":
    es = get_es_client()
    
    # Vérifier la connexion
    if not es.ping():
        logger.error("❌ Impossible de se connecter à Elasticsearch")
        exit(1)
    
    logger.info("✅ Connecté à Elasticsearch")
    
    index_name = "publications"
    
    # Créer l'index
    create_index(es, index_name)
    
    # Indexer
    json_pattern = "/opt/spark/data_engineering/ingestion/raw/openalex_*.json"
    index_publications(es, index_name, json_pattern)
    
    # Rafraîchir
    es.indices.refresh(index=index_name)
    
    # Vérifier
    count = es.count(index=index_name)
    logger.info(f"📊 Documents dans l'index: {count['count']}")