"""
Chunking des publications pour le RAG
"""
import re
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class PublicationChunker:
    """Découpe les publications en chunks pour l'embedding"""
    
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Args:
            chunk_size: nombre de mots par chunk (~300 mots ≈ 400 tokens)
            chunk_overlap: chevauchement pour garder le contexte
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Découper un texte en chunks avec overlap"""
        if not text or len(text.strip()) < 50:
            return []
        
        # Nettoyer
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Découper par phrases
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            words = sentence.split()
            
            if current_size + len(words) > self.chunk_size and current_chunk:
                # Sauvegarder le chunk
                chunks.append(' '.join(current_chunk))
                
                # Garder l'overlap
                overlap_words = current_chunk[-self.chunk_overlap:]
                current_chunk = overlap_words
                current_size = len(overlap_words)
            
            current_chunk.extend(words)
            current_size += len(words)
        
        # Dernier chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return [c for c in chunks if len(c.split()) > 20]
    
    def chunk_publication(self, pub: Dict) -> List[Dict]:
        """Créer les chunks pour une publication"""
        title = str(pub.get('title', ''))
        abstract = str(pub.get('abstract', ''))
        
        # Le titre est TOUJOURS le premier chunk (toujours pertinent)
        chunks = []
        
        if title and len(title) > 10:
            chunks.append({
                'chunk_id': f"{pub.get('openalex_id', 'unknown')}_0",
                'text': title,
                'chunk_type': 'title',
                'position': 0
            })
        
        # Puis les chunks de l'abstract
        abstract_chunks = self.chunk_text(abstract)
        for i, chunk_text in enumerate(abstract_chunks):
            chunks.append({
                'chunk_id': f"{pub.get('openalex_id', 'unknown')}_{i+1}",
                'text': chunk_text,
                'chunk_type': 'abstract',
                'position': i + 1
            })
        
        return chunks
    
    def chunk_dataframe(self, df) -> List[Dict]:
        """Chunker tout un DataFrame de publications"""
        all_chunks = []
        
        for _, row in df.iterrows():
            pub = row.to_dict()
            chunks = self.chunk_publication(pub)
            
            # Enrichir chaque chunk avec les métadonnées de la publication
            for chunk in chunks:
                chunk.update({
                    'openalex_id': pub.get('openalex_id'),
                    'title': pub.get('title'),
                    'publication_year': pub.get('publication_year'),
                    'main_topic': pub.get('main_topic'),
                    'topic_probability': pub.get('topic_probability'),
                    'doi': pub.get('doi'),
                })
            
            all_chunks.extend(chunks)
        
        logger.info(f"✅ {len(all_chunks)} chunks créés depuis {len(df)} publications")
        return all_chunks


if __name__ == "__main__":
    import pandas as pd
    
    df = pd.read_csv("/opt/airflow/nlp/data/openalex_with_topics.csv")
    chunker = PublicationChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_dataframe(df.head(20))
    
    print(f"Total chunks: {len(chunks)}")
    for c in chunks[:3]:
        print(f"\n--- {c['chunk_id']} ({c['chunk_type']}) ---")
        print(c['text'][:200])