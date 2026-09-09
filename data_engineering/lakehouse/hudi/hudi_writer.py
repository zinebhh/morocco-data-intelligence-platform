"""
Writer pour les tables Hudi
"""
import logging
from typing import Dict, Any, Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, md5, concat, when, current_timestamp

from .hudi_config import HudiConfig

logger = logging.getLogger(__name__)

class HudiWriter:
    """
    Classe pour écrire des données dans des tables Hudi
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self._ensure_hudi_availability()
    
    def _ensure_hudi_availability(self):
        """Vérifier que Hudi est disponible"""
        try:
            # Tester si Hudi est disponible
            from pyspark.sql import DataFrame
            test_df = self.spark.range(1)
            test_df.write.format("hudi").mode("overwrite").save("/tmp/test_hudi")
            logger.info("✅ Hudi est disponible")
        except Exception as e:
            logger.warning(f"⚠️ Hudi peut ne pas être disponible: {e}")
            logger.warning("⚠️ Assurez-vous d'avoir lancé Spark avec les packages Hudi")
    
    def write_university_data(
        self,
        df: DataFrame,
        config: Optional[HudiConfig] = None,
        mode: str = "upsert"
    ) -> DataFrame:
        """
        Écrire des données d'universités dans une table Hudi
        
        Args:
            df: DataFrame à écrire
            config: Configuration Hudi
            mode: Mode d'écriture (upsert, append, overwrite)
            
        Returns:
            DataFrame: Le DataFrame écrit
        """
        if config is None:
            config = HudiConfig(table_name="universities")
        
        logger.info(f"🚀 Écriture Hudi: {config.table_name}")
        logger.info(f"📁 Base path: {config.base_path}")
        logger.info(f"📋 Mode: {mode}")
        
        # Préparer le DataFrame pour Hudi
        hudi_df = self._prepare_university_df(df)
        
        # Ajouter des métadonnées
        hudi_df = hudi_df.withColumn("updated_at", current_timestamp())
        
        # Compter les lignes
        count = hudi_df.count()
        logger.info(f"📊 {count} lignes à écrire")
        
        if count == 0:
            logger.warning("⚠️ Aucune donnée à écrire")
            return df
        
        # Définir les options Hudi
        options = config.options.copy()
        options['hoodie.datasource.write.operation'] = mode
        options['hoodie.datasource.write.table.name'] = config.table_name
        
        # Chemin complet
        full_path = f"{config.base_path}/{config.table_name}"
        
        # Écrire
        try:
            hudi_df.write \
                .format("hudi") \
                .options(**options) \
                .mode("overwrite") \
                .save(full_path)
            
            logger.info(f"✅ Données écrites dans Hudi: {full_path}")
            
            # Vérifier
            result = self.spark.read.format("hudi").load(full_path)
            logger.info(f"📊 {result.count()} lignes dans la table Hudi")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur écriture Hudi: {e}")
            raise
    
    def _prepare_university_df(self, df: DataFrame) -> DataFrame:
        """
        Préparer un DataFrame pour une table Hudi universités
        """
        # Ajouter un ID unique si non présent
        if "id" not in df.columns:
            df = df.withColumn("id", md5(concat(col("university"), col("url"))))
        
        # Nettoyer les colonnes
        if "university" not in df.columns:
            df = df.withColumn("university", lit("unknown"))
        
        # Types appropriés
        if "publication_year" in df.columns:
            df = df.withColumn("publication_year", col("publication_year").cast("int"))
        
        return df
    
    def read_table(self, table_name: str, base_path: Optional[str] = None) -> DataFrame:
        """
        Lire une table Hudi
        
        Args:
            table_name: Nom de la table
            base_path: Chemin base (optionnel)
            
        Returns:
            DataFrame: Table Hudi
        """
        if base_path is None:
            base_path = "lakehouse/hudi"
        
        full_path = f"{base_path}/{table_name}"
        
        try:
            df = self.spark.read.format("hudi").load(full_path)
            logger.info(f"📖 {df.count()} lignes lues de {full_path}")
            return df
        except Exception as e:
            logger.error(f"❌ Erreur lecture: {e}")
            return self.spark.createDataFrame([], schema=None)
    
    def read_table_with_time_travel(
        self,
        table_name: str,
        timestamp: str,
        base_path: Optional[str] = None
    ) -> DataFrame:
        """
        Lire une table Hudi avec Time Travel
        
        Args:
            table_name: Nom de la table
            timestamp: Timestamp au format 'YYYYMMDDHHMMSS'
            base_path: Chemin base (optionnel)
            
        Returns:
            DataFrame: Table Hudi à un moment donné
        """
        if base_path is None:
            base_path = "lakehouse/hudi"
        
        full_path = f"{base_path}/{table_name}"
        
        try:
            df = self.spark.read \
                .format("hudi") \
                .option("hoodie.datasource.read.begin.instanttime", timestamp) \
                .load(full_path)
            
            logger.info(f"📖 Time travel: {table_name} à {timestamp}")
            return df
        except Exception as e:
            logger.error(f"❌ Erreur time travel: {e}")
            return self.spark.createDataFrame([], schema=None)

def create_hudi_table_from_parquet(
    spark: SparkSession,
    parquet_path: str,
    table_name: str,
    partition_columns: list = None
):
    """
    Créer une table Hudi à partir de données Parquet
    
    Args:
        spark: Session Spark
        parquet_path: Chemin des données Parquet
        table_name: Nom de la table Hudi
        partition_columns: Colonnes de partition
    """
    logger.info(f"🚀 Création table Hudi: {table_name}")
    logger.info(f"📁 Source: {parquet_path}")
    
    # Lire les données Parquet
    df = spark.read.parquet(parquet_path)
    
    if partition_columns is None:
        partition_columns = ["university"]
    
    # Configurer Hudi
    config = HudiConfig(table_name=table_name)
    config.options['hoodie.datasource.write.recordkey.field'] = 'id'
    config.options['hoodie.datasource.write.partitionpath.field'] = partition_columns[0]
    
    # Ajouter un ID
    if "id" not in df.columns:
        from pyspark.sql.functions import md5, concat, lit
        df = df.withColumn("id", md5(concat(col("university"), col("url"))))
    
    # Écrire
    writer = HudiWriter(spark)
    writer.write_university_data(df, config)
    
    return True