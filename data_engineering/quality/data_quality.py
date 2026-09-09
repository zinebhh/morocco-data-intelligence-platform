"""
Data Quality - Validation des données
"""
import logging
from typing import Dict, Any, List
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum, when, isnan, isnull

logger = logging.getLogger(__name__)

class DataQualityChecker:
    """Vérificateur de qualité des données"""
    
    def __init__(self, df: DataFrame):
        self.df = df
        self.results = {}
    
    def check_not_null(self, column: str) -> Dict[str, Any]:
        """Vérifier qu'une colonne n'a pas de valeurs nulles"""
        null_count = self.df.filter(col(column).isNull()).count()
        total_count = self.df.count()
        null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
        
        result = {
            "column": column,
            "null_count": null_count,
            "total_count": total_count,
            "null_percentage": null_percentage,
            "passed": null_count == 0
        }
        self.results[f"not_null_{column}"] = result
        return result
    
    def check_unique(self, column: str) -> Dict[str, Any]:
        """Vérifier qu'une colonne a des valeurs uniques"""
        distinct_count = self.df.select(column).distinct().count()
        total_count = self.df.count()
        duplicate_count = total_count - distinct_count
        
        result = {
            "column": column,
            "distinct_count": distinct_count,
            "total_count": total_count,
            "duplicate_count": duplicate_count,
            "passed": duplicate_count == 0
        }
        self.results[f"unique_{column}"] = result
        return result
    
    def check_min_length(self, column: str, min_length: int) -> Dict[str, Any]:
        """Vérifier la longueur minimale d'une colonne texte"""
        short_count = self.df.filter(length(col(column)) < min_length).count()
        total_count = self.df.count()
        
        result = {
            "column": column,
            "min_length": min_length,
            "short_count": short_count,
            "total_count": total_count,
            "passed": short_count == 0
        }
        self.results[f"min_length_{column}"] = result
        return result
    
    def check_value_range(self, column: str, min_val: float = None, max_val: float = None) -> Dict[str, Any]:
        """Vérifier qu'une colonne numérique est dans une plage"""
        conditions = []
        if min_val is not None:
            conditions.append(col(column) < min_val)
        if max_val is not None:
            conditions.append(col(column) > max_val)
        
        if conditions:
            from pyspark.sql.functions import col, lit
            condition = conditions[0]
            for cond in conditions[1:]:
                condition = condition | cond
            
            out_of_range = self.df.filter(condition).count()
            total_count = self.df.count()
            
            result = {
                "column": column,
                "min_val": min_val,
                "max_val": max_val,
                "out_of_range": out_of_range,
                "total_count": total_count,
                "passed": out_of_range == 0
            }
            self.results[f"range_{column}"] = result
            return result
        
        return {"passed": True}
    
    def run_all_checks(self, checks: List[Dict]) -> Dict[str, Any]:
        """
        Exécuter toutes les vérifications
        
        Args:
            checks: Liste de vérifications à effectuer
                Exemple: [
                    {"type": "not_null", "column": "title"},
                    {"type": "min_length", "column": "content", "min_length": 50},
                    {"type": "unique", "column": "url"}
                ]
        """
        for check in checks:
            check_type = check.pop("type")
            if check_type == "not_null":
                self.check_not_null(**check)
            elif check_type == "min_length":
                self.check_min_length(**check)
            elif check_type == "unique":
                self.check_unique(**check)
            elif check_type == "range":
                self.check_value_range(**check)
        
        # Résumé
        all_passed = all(r.get("passed", False) for r in self.results.values())
        
        return {
            "checks": self.results,
            "all_passed": all_passed,
            "failed_checks": [k for k, v in self.results.items() if not v.get("passed", False)]
        }
    
    def print_report(self):
        """Afficher un rapport de qualité"""
        logger.info("=" * 60)
        logger.info("📊 RAPPORT DE QUALITÉ DES DONNÉES")
        logger.info("=" * 60)
        
        for check_name, result in self.results.items():
            passed = "✅" if result.get("passed") else "❌"
            logger.info(f"{passed} {check_name}: {result}")
        
        logger.info("=" * 60)