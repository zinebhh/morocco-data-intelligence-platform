"""
Script pour exécuter Spark avec Hudi
"""
import os
import subprocess
from pathlib import Path

def run_spark_hudi():
    """
    Lancer Spark avec les packages Hudi
    """
    # Version de Spark et Hudi
    spark_version = "3.5.3"
    scala_version = "2.12"
    hudi_version = "0.15.0"
    
    # Packages Hudi
    packages = [
        f"org.apache.hudi:hudi-spark{spark_version.split('.')[0]}.{spark_version.split('.')[1]}-bundle_{scala_version}:{hudi_version}",
        "org.apache.spark:spark-sql_2.12:3.5.3",
        "org.apache.spark:spark-hive_2.12:3.5.3"
    ]
    
    packages_str = ",".join(packages)
    
    # Commande Spark
    cmd = [
        "spark-submit",
        "--packages", packages_str,
        "--conf", "spark.sql.adaptive.enabled=true",
        "--conf", "spark.sql.adaptive.coalescePartitions.enabled=true",
        "spark/transformations/openalex_transformer.py"
    ]
    
    print(f"🚀 Lancement de Spark avec Hudi...")
    print(f"📦 Packages: {packages_str}")
    
    # Exécuter
    subprocess.run(cmd)

if __name__ == "__main__":
    # Vérifier si spark-submit est disponible
    try:
        subprocess.run(["spark-submit", "--version"], capture_output=True)
        run_spark_hudi()
    except FileNotFoundError:
        print("❌ spark-submit non trouvé. Installation de Spark nécessaire.")
        print("📥 Télécharger Spark: https://spark.apache.org/downloads.html")