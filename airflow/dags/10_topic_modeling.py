"""
DAG 10: Topic Modeling avec LDA
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'edudata',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def enrich_task(**context):
    """Enrichir avec les abstracts"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    
    import pandas as pd
    import requests
    import time
    from pathlib import Path
    
    # Chemins directs
    OPENALEX_CSV = Path("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    NLP_DATA = Path("/opt/airflow/nlp/data")
    NLP_ENRICHED_CSV = NLP_DATA / "openalex_enriched.csv"
    
    NLP_DATA.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Chargement: {OPENALEX_CSV}")
    df = pd.read_csv(OPENALEX_CSV)
    logger.info(f"📊 {len(df)} publications")
    
    # Reconstruction abstract
    def reconstruct_abstract(inverted_index):
        if not inverted_index:
            return ""
        positions = []
        for word, pos_list in inverted_index.items():
            for pos in pos_list:
                positions.append((pos, word))
        positions.sort()
        return " ".join([w for _, w in positions])
    
    # Enrichir (limité à 100)
    abstracts = []
    total = min(100, len(df))
    
    for i, (_, row) in enumerate(df.iterrows()):
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
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                inv = data.get('abstract_inverted_index')
                if inv:
                    abstracts.append(reconstruct_abstract(inv))
                else:
                    abstracts.append("")
            else:
                abstracts.append("")
            time.sleep(0.1)
        except Exception as e:
            logger.warning(f"Erreur {openalex_id}: {e}")
            abstracts.append("")
    
    df['abstract'] = abstracts[:len(df)]
    df['has_abstract'] = df['abstract'].str.len() > 0
    
    df.to_csv(NLP_ENRICHED_CSV, index=False)
    logger.info(f"✅ {df['has_abstract'].sum()}/{len(df)} avec abstract")
    logger.info(f"💾 Sauvegardé: {NLP_ENRICHED_CSV}")
    
    context['ti'].xcom_push(key='count', value=len(df))
    return len(df)


def topic_modeling_task(**context):
    """Entraîner le modèle LDA (sans multiprocessing)"""
    import sys
    sys.path.insert(0, "/opt/airflow")
    
    import pandas as pd
    import json
    from pathlib import Path
    from gensim import corpora
    from gensim.models import LdaModel, CoherenceModel
    from nltk.corpus import stopwords
    import re
    
    logger.info("🚀 Topic Modeling LDA")
    
    # Chemins
    NLP_DATA = Path("/opt/airflow/nlp/data")
    NLP_OUTPUT = Path("/opt/airflow/nlp/topic_modeling/output")
    NLP_OUTPUT.mkdir(parents=True, exist_ok=True)
    
    NLP_ENRICHED_CSV = NLP_DATA / "openalex_enriched.csv"
    OPENALEX_CSV = Path("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    
    csv_path = NLP_ENRICHED_CSV if NLP_ENRICHED_CSV.exists() else OPENALEX_CSV
    df = pd.read_csv(csv_path)
    logger.info(f"📊 {len(df)} publications")
    
    # Stopwords
    try:
        stopwords_set = set(stopwords.words('english'))
    except:
        stopwords_set = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    # Nettoyer
    def clean_text(text):
        text = str(text).lower()
        text = re.sub(r'http\S+', ' ', text)
        text = re.sub(r'[^a-z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        tokens = [w for w in text.split() if w not in stopwords_set and len(w) > 2]
        return tokens
    
    # Préparer les textes
    texts = []
    for _, row in df.iterrows():
        title = str(row.get('title', ''))
        abstract = str(row.get('abstract', ''))
        full = f"{title} {title} {abstract}"
        tokens = clean_text(full)
        if tokens:
            texts.append(tokens)
    
    logger.info(f"📝 {len(texts)} textes préparés")
    
    if len(texts) < 10:
        raise ValueError(f"Pas assez de textes: {len(texts)}")
    
    # Créer dictionnaire
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=2, no_above=0.8)
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    # Entraîner LDA
    num_topics = 5
    model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        passes=10,
        alpha='auto'
    )
    
    # Calculer la cohérence SANS multiprocessing
    logger.info("🔍 Calcul de la cohérence (single process)...")
    coherence = CoherenceModel(
        model=model,
        texts=texts,
        dictionary=dictionary,
        coherence='c_v',
        processes=1  # ← IMPORTANT : 1 seul processus
    ).get_coherence()
    
    logger.info(f"✅ Cohérence: {coherence:.4f}")
    
    # Récupérer les topics
    topics = {}
    for topic_id in range(num_topics):
        words = model.show_topic(topic_id, topn=10)
        topics[topic_id] = [w for w, _ in words]
        logger.info(f"  Topic {topic_id}: {', '.join(topics[topic_id][:5])}")
    
    # Sauvegarder
    with open(NLP_OUTPUT / "topics.json", 'w') as f:
        json.dump({
            "num_topics": num_topics,
            "coherence": coherence,
            "topics": {str(k): v for k, v in topics.items()}
        }, f, indent=2)
    
    # Ajouter les topics au DataFrame
    doc_topics = []
    for bow in corpus:
        t = model.get_document_topics(bow)
        if t:
            main_topic, prob = max(t, key=lambda x: x[1])
            doc_topics.append((main_topic, prob))
        else:
            doc_topics.append((-1, 0.0))
    
    df['main_topic'] = [t[0] for t in doc_topics]
    df['topic_probability'] = [t[1] for t in doc_topics]
    
    output_csv = NLP_DATA / "openalex_with_topics.csv"
    df.to_csv(output_csv, index=False)
    
    logger.info(f"💾 Sauvegardé: {output_csv}")
    context['ti'].xcom_push(key='coherence', value=coherence)
    return coherence

with DAG(
    '10_topic_modeling',
    default_args=default_args,
    description='Topic Modeling avec LDA',
    schedule_interval='@weekly',
    catchup=False,
    tags=['nlp', 'topic-modeling']
) as dag:
    
    start = DummyOperator(task_id='start')
    
    enrich = PythonOperator(
        task_id='enrich_abstracts',
        python_callable=enrich_task
    )
    
    topic_modeling = PythonOperator(
        task_id='topic_modeling',
        python_callable=topic_modeling_task
    )
    
    end = DummyOperator(task_id='end')
    
    start >> enrich >> topic_modeling >> end