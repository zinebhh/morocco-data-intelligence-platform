"""
Pipeline RAG complet
"""
import logging
from typing import Dict, List
import sys
sys.path.insert(0, "/opt/airflow")

from nlp.rag.retriever import Retriever
from nlp.rag.llm_service import LLMService

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Tu es un assistant de recherche universitaire marocain.
Tu réponds UNIQUEMENT à partir des sources fournies dans le contexte.
Si l'information n'est pas dans le contexte, dis-le clairement.
Cite toujours tes sources avec [Source N].
Réponds en français, de manière structurée et concise."""


class RAGPipeline:
    """Pipeline RAG: retrieval + generation"""
    
    def __init__(self, top_k: int = 5, provider: str = "ollama"):
        self.retriever = Retriever(top_k=top_k, use_hybrid=True)
        self.llm = LLMService(provider=provider)
        logger.info("✅ RAG Pipeline prêt")
    
    def ask(self, question: str, return_sources: bool = True) -> Dict:
        """Poser une question au système RAG"""
        logger.info(f"❓ Question: {question}")
        
        # 1. Retrieve
        results = self.retriever.retrieve(question)
        
        if not results:
            return {
                "question": question,
                "answer": "Aucun document pertinent trouvé.",
                "sources": []
            }
        
        # 2. Build context
        context = self.retriever.format_context(results, max_chars_per_doc=500)
        
        # 3. Build prompt
        prompt = f"""Contexte (publications académiques):
{context}

Question: {question}

Réponse basée UNIQUEMENT sur le contexte ci-dessus:"""
        
        # 4. Generate
        answer = self.llm.generate(prompt, system=SYSTEM_PROMPT, temperature=0.3)
        
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "title": r.get('title'),
                    "year": r.get('publication_year'),
                    "topic": r.get('main_topic'),
                    "score": round(r['score'], 3),
                    "excerpt": r.get('text', '')[:200]
                }
                for r in results
            ] if return_sources else []
        }


if __name__ == "__main__":
    rag = RAGPipeline(top_k=5)
    
    questions = [
        "Quels sont les principaux domaines de recherche dans les universités marocaines ?",
        "Comment l'IA est-elle utilisée dans l'éducation au Maroc ?",
    ]
    
    for q in questions:
        print(f"\n{'='*70}")
        print(f"❓ {q}")
        print('='*70)
        result = rag.ask(q)
        print(f"\n💬 {result['answer']}\n")
        print("📚 Sources:")
        for i, s in enumerate(result['sources'], 1):
            print(f"  [{i}] {s['title']} ({s['year']}) - score={s['score']}")