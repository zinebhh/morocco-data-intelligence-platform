"""
Feature Engineering pour le ML
"""
import pandas as pd
import numpy as np
import re
import logging

logger = logging.getLogger(__name__)


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extraire des features à partir des données brutes
    """
    logger.info("🔧 Extraction des features")
    
    df = df.copy()
    
    # 1. Features textuelles
    df['title_word_count'] = df['title'].str.split().str.len()
    df['title_has_ai'] = df['title'].str.lower().str.contains('ai|artificial intelligence|machine learning|deep learning', regex=True).astype(int)
    df['title_has_morocco'] = df['title'].str.lower().str.contains('morocco|moroccan', regex=True).astype(int)
    df['title_has_university'] = df['title'].str.lower().str.contains('university|université', regex=True).astype(int)
    
    # 2. Features de citation
    df['citation_per_year'] = df.apply(
        lambda row: row['citation_count'] / max(2024 - row['publication_year'], 1) 
        if pd.notna(row['publication_year']) else 0,
        axis=1
    )
    
    # 3. Catégories de citations
    df['citation_category'] = pd.cut(
        df['citation_count'],
        bins=[-1, 0, 5, 20, 100, float('inf')],
        labels=['Aucune', 'Faible', 'Moyenne', 'Élevée', 'Très élevée']
    )
    
    # 4. Catégories d'années
    df['year_category'] = pd.cut(
        df['publication_year'],
        bins=[2019, 2021, 2023, 2024, 2026],
        labels=['2020-2021', '2022-2023', '2024', '2025+']
    )
    
    # 5. Features du journal
    df['has_journal'] = df['journal'].notna().astype(int)
    df['journal_length'] = df['journal'].fillna('').str.len()
    
    # 6. Open Access features
    df['oa_binary'] = df['is_open_access'].fillna(False).astype(int)
    
    # 7. Langue
    df['is_english'] = (df['language'] == 'en').astype(int)
    
    logger.info(f"✅ Features extraites: {len(df.columns)} colonnes")
    
    return df


def prepare_ml_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Préparer le dataset pour le ML
    """
    logger.info("🔧 Préparation du dataset ML")
    
    # Sélectionner les colonnes pour le ML
    ml_columns = [
        'id', 'title', 'publication_year', 'citation_count',
        'publication_type', 'language', 'journal', 'is_open_access',
        'title_length', 'title_word_count', 'title_has_ai',
        'title_has_morocco', 'title_has_university', 'citation_per_year',
        'citation_category', 'year_category', 'has_journal',
        'journal_length', 'oa_binary', 'is_english'
    ]
    
    # Filtrer les colonnes existantes
    existing_cols = [col for col in ml_columns if col in df.columns]
    ml_df = df[existing_cols].copy()
    
    # Supprimer les lignes avec des valeurs manquantes critiques
    ml_df = ml_df.dropna(subset=['citation_count', 'publication_year'])
    
    logger.info(f"✅ Dataset ML: {len(ml_df)} lignes, {len(ml_df.columns)} colonnes")
    
    return ml_df


if __name__ == "__main__":
    # Test
    df = pd.read_csv("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    df = extract_features(df)
    ml_df = prepare_ml_dataset(df)
    print(ml_df.head())
    print(f"\nDataset ML: {len(ml_df)} lignes")