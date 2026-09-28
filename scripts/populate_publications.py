"""Peuple les colonnes abstract et research_field depuis les fichiers OpenAlex raw."""

import json
import logging
import glob
import os
from pathlib import Path

# ⚠️ IMPORTANT: forcer UTF-8 AVANT d'importer psycopg2
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["LC_ALL"] = "C.UTF-8"

import psycopg2
from psycopg2.extras import execute_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Config PostgreSQL - on utilise un DSN pour éviter les problèmes d'encodage
DB_DSN = "host=localhost port=5432 dbname=analytics user=airflow password=airflow client_encoding=utf8"

RAW_DIR = Path("data_engineering/ingestion/raw")


def extract_abstract(work: dict) -> str:
    """Reconstruit l'abstract depuis l'index inversé OpenAlex."""
    inverted = work.get("abstract_inverted_index")
    if not inverted:
        return ""
    positions = {}
    for word, pos_list in inverted.items():
        for pos in pos_list:
            positions[pos] = word
    return " ".join(positions[i] for i in sorted(positions.keys()))


def extract_research_field(work: dict) -> str:
    """Extrait le domaine principal depuis les concepts OpenAlex."""
    concepts = work.get("concepts", [])
    if not concepts:
        topic = work.get("primary_topic", {})
        if topic:
            return topic.get("display_name", "Unknown")
        return "Unknown"
    top = max(concepts, key=lambda c: c.get("score", 0))
    return top.get("display_name", "Unknown")


def load_all_works():
    works_by_id = {}
    files = sorted(glob.glob(str(RAW_DIR / "openalex_*.json")))
    logger.info(f"📂 {len(files)} fichiers OpenAlex trouvés")

    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            results = data.get("results", data) if isinstance(data, dict) else data
            for work in results:
                oa_id = work.get("id", "")
                if oa_id:
                    works_by_id[oa_id] = work
        except Exception as e:
            logger.warning(f"⚠️ Erreur lecture {fpath}: {e}")

    logger.info(f"✅ {len(works_by_id)} works uniques chargés")
    return works_by_id


def update_publications(works_by_id: dict):
    # ✅ Utilisation d'un DSN, plus robuste sous Windows
    conn = psycopg2.connect(DB_DSN)
    conn.set_client_encoding("UTF8")
    cur = conn.cursor()

    cur.execute("SELECT id, openalex_id FROM publications WHERE openalex_id IS NOT NULL")
    rows = cur.fetchall()
    logger.info(f"📊 {len(rows)} publications à mettre à jour")

    updates = []
    for pub_id, oa_id in rows:
        work = works_by_id.get(oa_id)
        if not work:
            continue

        abstract = extract_abstract(work)
        research_field = extract_research_field(work)
        authors = json.dumps([
            {"name": a.get("author", {}).get("display_name")}
            for a in work.get("authorships", [])
        ], ensure_ascii=False)
        concepts = json.dumps([
            {"name": c.get("display_name"), "score": c.get("score")}
            for c in work.get("concepts", [])[:10]
        ], ensure_ascii=False)

        updates.append((abstract, research_field, authors, concepts, pub_id))

    if not updates:
        logger.warning("⚠️ Aucune mise à jour à faire")
        cur.close()
        conn.close()
        return 0

    execute_batch(cur, """
        UPDATE publications 
        SET abstract = %s, research_field = %s, authors = %s, concepts = %s
        WHERE id = %s
    """, updates, page_size=50)

    conn.commit()
    logger.info(f"✅ {len(updates)} publications mises à jour")
    cur.close()
    conn.close()
    return len(updates)


if __name__ == "__main__":
    works = load_all_works()
    update_publications(works)