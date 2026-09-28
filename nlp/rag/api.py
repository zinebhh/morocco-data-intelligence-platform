"""
API FastAPI - EduData NLP Assistant
Expose RAG, recherche sémantique, publications, topics, stats
"""
import sys
sys.path.insert(0, "/opt/airflow")

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

# ============================================================
# CONFIG
# ============================================================
PG_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/analytics"
ES_URL = "http://elasticsearch:9200"
OLLAMA_URL = "http://ollama:11434"
TOPICS_PATH = Path("/opt/airflow/nlp/topic_modeling/output/topics.json")
INDEX_NAME = "publications_semantic"

# ============================================================
# APP
# ============================================================
app = FastAPI(
    title="EduData NLP Assistant API",
    description="API pour l'assistant RAG sur les publications universitaires marocaines",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod: liste blanche
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# SINGLETONS (chargés au démarrage)
# ============================================================
rag_pipeline = None
retriever = None
es_client = None
pg_engine = None


@app.on_event("startup")
def startup():
    global rag_pipeline, retriever, es_client, pg_engine
    import time
    
    logger.info("🚀 Démarrage de l'API...")
    
    # PostgreSQL (retry 30s)
    pg_engine = create_engine(PG_URL, pool_pre_ping=True)
    for i in range(10):
        try:
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ PostgreSQL connecté")
            break
        except Exception:
            logger.info(f"⏳ Attente PostgreSQL... ({i+1}/10)")
            time.sleep(3)
    else:
        raise ConnectionError("❌ PostgreSQL inaccessible après 30s")
    
    # Elasticsearch (retry 60s)
    es_client = Elasticsearch([ES_URL])
    for i in range(20):
        try:
            if es_client.ping():
                logger.info("✅ Elasticsearch connecté")
                break
        except Exception:
            pass
        logger.info(f"⏳ Attente Elasticsearch... ({i+1}/20)")
        time.sleep(3)
    else:
        raise ConnectionError("❌ Elasticsearch inaccessible après 60s")
    
    # RAG
    from nlp.rag.rag_pipeline import RAGPipeline
    from nlp.rag.retriever import Retriever
    
    rag_pipeline = RAGPipeline(top_k=3, provider="ollama")
    retriever = Retriever(top_k=5, use_hybrid=True)
    
    logger.info("✅ API prête")
# ============================================================
# MODELS (Pydantic)
# ============================================================
class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(3, ge=1, le=10)
    return_sources: bool = True


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=300)
    top_k: int = Field(5, ge=1, le=20)
    mode: str = Field("hybrid", pattern="^(hybrid|semantic|keyword)$")


# ============================================================
# ROUTES
# ============================================================

@app.get("/")
def root():
    return {
        "service": "EduData NLP Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health():
    """Vérifier que tous les services sont up"""
    status = {"api": "ok", "postgres": "ko", "elasticsearch": "ko", "ollama": "ko"}
    
    try:
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["postgres"] = "ok"
    except Exception as e:
        status["postgres"] = f"error: {e}"
    
    try:
        if es_client.ping():
            count = es_client.count(index=INDEX_NAME)["count"]
            status["elasticsearch"] = f"ok ({count} docs)"
    except Exception as e:
        status["elasticsearch"] = f"error: {e}"
    
    try:
        import requests
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        status["ollama"] = f"ok ({len(models)} models)"
    except Exception as e:
        status["ollama"] = f"error: {e}"
    
    return status


@app.post("/ask")
def ask(req: AskRequest):
    """Poser une question au RAG (réponse + sources)"""
    if rag_pipeline is None:
        raise HTTPException(503, "RAG non initialisé")
    
    try:
        result = rag_pipeline.ask(req.question, return_sources=req.return_sources)
        return result
    except Exception as e:
        logger.exception("Erreur RAG")
        raise HTTPException(500, f"Erreur RAG: {e}")


@app.post("/search")
def search(req: SearchRequest):
    """Recherche sémantique ou hybride"""
    try:
        if req.mode == "semantic":
            from nlp.rag.retriever import Retriever
            r = Retriever(top_k=req.top_k, use_hybrid=False)
            results = r.retrieve(req.query)
        elif req.mode == "keyword":
            resp = es_client.search(
                index=INDEX_NAME,
                body={"query": {"multi_match": {"query": req.query, "fields": ["text^2", "title^3"]}}, "size": req.top_k}
            )
            results = [{"score": h["_score"], **h["_source"]} for h in resp["hits"]["hits"]]
        else:  # hybrid
            results = retriever.retrieve(req.query)
        
        return {
            "query": req.query,
            "mode": req.mode,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.exception("Erreur search")
        raise HTTPException(500, f"Erreur search: {e}")


@app.get("/publications")
def list_publications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    topic: Optional[int] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
):
    """Liste paginée des publications avec filtres"""
    offset = (page - 1) * size
    where, params = [], {}
    
    if topic is not None:
        where.append("main_topic = :topic")
        params["topic"] = topic
    if year_min is not None:
        where.append("publication_year >= :year_min")
        params["year_min"] = year_min
    if year_max is not None:
        where.append("publication_year <= :year_max")
        params["year_max"] = year_max
    
    where_clause = ("WHERE " + " AND ".join(where)) if where else ""
    
    with pg_engine.connect() as conn:
        total = conn.execute(
            text(f"SELECT COUNT(*) FROM nlp_publications {where_clause}"), params
        ).scalar()
        
        rows = conn.execute(
            text(f"""
                SELECT openalex_id, title, publication_year, doi,
                       main_topic, topic_probability, research_domain
                FROM nlp_publications
                {where_clause}
                ORDER BY publication_year DESC NULLS LAST
                LIMIT :limit OFFSET :offset
            """),
            {**params, "limit": size, "offset": offset}
        ).mappings().all()
    
    return {
        "page": page,
        "size": size,
        "total": total,
        "pages": (total + size - 1) // size,
        "items": [dict(r) for r in rows]
    }


@app.get("/publications/{openalex_id:path}")
def get_publication(openalex_id: str):
    """Détail d'une publication"""
    with pg_engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM nlp_publications WHERE openalex_id = :id"),
            {"id": openalex_id}
        ).mappings().first()
    
    if not row:
        raise HTTPException(404, "Publication introuvable")
    return dict(row)


@app.get("/topics")
def list_topics():
    """Liste des topics NLP"""
    with pg_engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT t.topic_id, t.label, t.keywords,
                       COUNT(p.openalex_id) AS nb_publications
                FROM nlp_topics t
                LEFT JOIN nlp_publications p ON p.main_topic = t.topic_id
                GROUP BY t.topic_id, t.label, t.keywords
                ORDER BY t.topic_id
            """)
        ).mappings().all()
    return {"topics": [dict(r) for r in rows]}


@app.get("/stats")
def stats():
    """Statistiques globales pour dashboard"""
    with pg_engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM nlp_publications")).scalar()
        
        by_year = conn.execute(text("""
            SELECT publication_year AS year, COUNT(*) AS count
            FROM nlp_publications
            WHERE publication_year IS NOT NULL
            GROUP BY publication_year
            ORDER BY publication_year
        """)).mappings().all()
        
        by_topic = conn.execute(text("""
            SELECT t.label AS topic, COUNT(p.openalex_id) AS count
            FROM nlp_topics t
            LEFT JOIN nlp_publications p ON p.main_topic = t.topic_id
            GROUP BY t.label
            ORDER BY count DESC
        """)).mappings().all()
        
        avg_conf = conn.execute(text("""
            SELECT ROUND(AVG(topic_probability)::numeric, 3) FROM nlp_publications
        """)).scalar()
        
        models = conn.execute(text("""
            SELECT model_type, accuracy, f1_score
            FROM nlp_model_metrics
            ORDER BY accuracy DESC
        """)).mappings().all()
    
    # Cohérence LDA
    coherence = None
    if TOPICS_PATH.exists():
        with open(TOPICS_PATH) as f:
            coherence = json.load(f).get("coherence")
    
    return {
        "total_publications": total,
        "avg_topic_confidence": float(avg_conf) if avg_conf else None,
        "lda_coherence": coherence,
        "publications_by_year": [dict(r) for r in by_year],
        "publications_by_topic": [dict(r) for r in by_topic],
        "models": [dict(r) for r in models],
    }


@app.get("/models")
def list_models():
    """Métriques des modèles de classification"""
    with pg_engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT model_type, accuracy, precision, recall, f1_score,
                   train_size, test_size, num_classes
            FROM nlp_model_metrics
            ORDER BY accuracy DESC
        """)).mappings().all()
    return {"models": [dict(r) for r in rows]}