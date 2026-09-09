"""
Script complet pour exécuter tout le pipeline
"""
import sys
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def run_full_pipeline():
    """Exécuter le pipeline complet"""
    logger.info("🚀 DÉMARRAGE DU PIPELINE COMPLET")
    logger.info("=" * 60)
    
    # 1. Ingestion OpenAlex
    from data_engineering.ingestion.api_collectors.openalex_pipeline import run_pipeline
    results = run_pipeline(
        search_query="Morocco university",
        per_page=100,
        max_results=500,
        save_local=True,
        upload_minio=True
    )
    logger.info(f"✅ Ingestion terminée: {len(results)} publications")
    
    # 2. Transformation Spark (optionnel, nécessite Spark)
    try:
        from spark.transformations.openalex_transformer import create_spark_session, transform_openalex_data
        spark = create_spark_session()
        transform_openalex_data(
            spark,
            "data_engineering/ingestion/raw/*.json",
            "data_engineering/transformations/openalex_transformed"
        )
        logger.info("✅ Transformation Spark terminée")
    except Exception as e:
        logger.warning(f"⚠️ Transformation Spark ignorée: {e}")
    
    logger.info("=" * 60)
    logger.info("✅ PIPELINE COMPLET TERMINÉ")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_full_pipeline()