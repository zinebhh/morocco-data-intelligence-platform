"""
Enrichir les publications avec les abstracts OpenAlex
"""
import requests
import pandas as pd
import logging
import time
import sys
from pathlib import Path

sys.path.insert(0, "/opt/airflow")
from config.paths import OPENALEX_CSV, NLP_ENRICHED_CSV, NLP_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruire l'abstract à partir de l'inverted_index"""
    if not inverted_index:
        return ""
    
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    
    word_positions.sort()
    return " ".join([word for _, word in word_positions])


def enrich_publications(df: pd.DataFrame, limit: int = None) -> pd.DataFrame:
    """Récupérer les abstracts depuis OpenAlex"""
    logger.info(f"📊 {len(df)} publications à enrichir")
    
    abstracts = []
    total = len(df) if limit is None else min(limit, len(df))
    
    for i, (idx, row) in enumerate(df.iterrows()):
        if i >= total:
            abstracts.append("")
            continue
        
        openalex_id = row.get('openalex_id', '')
        
        if not openalex_id or pd.isna(openalex_id):
            abstracts.append("")
            continue
        
        try:
            work_id = openalex_id.split('/')[-1]
            url = f"https://api.openalex.org/works/{work_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                inverted_index = data.get('abstract_inverted_index')
                
                if inverted_index:
                    abstract = reconstruct_abstract(inverted_index)
                    abstracts.append(abstract)
                    logger.info(f"✅ {i+1}/{total}: {len(abstract)} car.")
                else:
                    abstracts.append("")
            else:
                abstracts.append("")
            
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ Erreur {openalex_id}: {e}")
            abstracts.append("")
    
    df = df.copy()
    df['abstract'] = abstracts[:len(df)]
    df['has_abstract'] = df['abstract'].str.len() > 0
    
    logger.info(f"✅ {df['has_abstract'].sum()}/{len(df)} avec abstract")
    return df


if __name__ == "__main__":
    NLP_DATA.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(OPENALEX_CSV)
    logger.info(f"📁 Chargé: {OPENALEX_CSV}")
    
    # Enrichir (10 en premier pour test)
    df_enriched = enrich_publications(df, limit=10)
    
    df_enriched.to_csv(NLP_ENRICHED_CSV, index=False)
    logger.info(f"💾 Sauvegardé: {NLP_ENRICHED_CSV}")