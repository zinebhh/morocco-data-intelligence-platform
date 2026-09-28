"""Test interactif du RAG"""
import sys
sys.path.insert(0, "/opt/airflow")

from nlp.rag.rag_pipeline import RAGPipeline

def main():
    print("=" * 70)
    print("🤖 TEST DU RAG ASSISTANT")
    print("=" * 70)
    
    rag = RAGPipeline(top_k=5, provider="ollama")
    
    questions = [
        "Quels sont les principaux domaines de recherche dans les universités marocaines ?",
        "Comment l'intelligence artificielle est-elle utilisée dans l'éducation au Maroc ?",
        "Quelles sont les préoccupations environnementales au Maroc ?",
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\n{'=' * 70}")
        print(f"❓ Question {i}: {q}")
        print("=" * 70)
        
        result = rag.ask(q)
        
        print(f"\n💬 Réponse:\n{result['answer']}")
        print(f"\n📚 Sources ({len(result['sources'])}):")
        for j, s in enumerate(result["sources"], 1):
            print(f"  [{j}] {s['title']} ({s['year']}) - score={s['score']}")


if __name__ == "__main__":
    main()