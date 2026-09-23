"""Chargement des publications depuis PostgreSQL."""

import logging
import pandas as pd
from sqlalchemy import create_engine
from nlp.classification.config import DB_CONFIG, TEXT_COLUMNS, TARGET_COLUMN

logger = logging.getLogger(__name__)


def get_engine():
    """Crée le moteur SQLAlchemy."""
    url = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)


def load_publications(limit: int = None) -> pd.DataFrame:
    """Charge les publications avec texte et label."""
    engine = get_engine()
    
    query = f"""
        SELECT 
            id,
            title,
            abstract,
            {TARGET_COLUMN}
        FROM publications
        WHERE title IS NOT NULL
          AND {TARGET_COLUMN} IS NOT NULL
    """
    if limit:
        query += f" LIMIT {limit}"
    
    df = pd.read_sql(query, engine)
    logger.info(f"✅ {len(df)} publications chargées")
    logger.info(f"📊 Distribution des labels:\n{df[TARGET_COLUMN].value_counts()}")
    
    return df


def build_text_column(df: pd.DataFrame) -> pd.DataFrame:
    """Concatène title + abstract en une seule colonne 'text'."""
    df = df.copy()
    df["text"] = df[TEXT_COLUMNS].fillna("").agg(" ".join, axis=1)
    return df