"""
Vérifier que Hudi fonctionne
"""
from pyspark.sql import SparkSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_hudi():
    """Vérifier l'installation de Hudi"""
    
    # Créer session Spark avec Hudi
    spark = SparkSession.builder \
        .appName("CheckHudi") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
        .getOrCreate()
    
    logger.info("✅ Session Spark créée")
    
    # Créer un DataFrame test
    from pyspark.sql import Row
    test_data = [
        Row(id="1", name="Université Hassan II", city="Casablanca"),
        Row(id="2", name="Université Mohammed V", city="Rabat")
    ]
    df = spark.createDataFrame(test_data)
    logger.info(f"📊 DataFrame test: {df.count()} lignes")
    
    # Écrire dans Hudi
    try:
        df.write.format("hudi") \
            .option("hoodie.table.name", "test_table") \
            .option("hoodie.datasource.write.recordkey.field", "id") \
            .option("hoodie.datasource.write.partitionpath.field", "city") \
            .mode("overwrite") \
            .save("lakehouse/hudi/test_table")
        
        logger.info("✅ Écriture Hudi réussie!")
        
        # Lire
        read_df = spark.read.format("hudi").load("lakehouse/hudi/test_table")
        logger.info(f"📖 Lecture Hudi: {read_df.count()} lignes")
        read_df.show()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur Hudi: {e}")
        logger.error("Assurez-vous d'avoir lancé Spark avec les packages Hudi")
        logger.error("Exemple: spark-submit --packages org.apache.hudi:hudi-spark3.5-bundle_2.12:0.15.0")
        return False

if __name__ == "__main__":
    check_hudi()