"""
Modèle de prédiction de la demande de formation
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DemandPredictor:
    """Prédicteur de la demande de formation"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.metrics = {}
    
    def prepare_data(self, df: pd.DataFrame):
        """
        Préparer les données pour l'entraînement
        """
        logger.info("🔧 Préparation des données")
        
        # Features numériques
        numeric_features = [
            'publication_year', 'title_length', 'title_word_count',
            'citation_count', 'citation_per_year', 'journal_length'
        ]
        
        # Features catégorielles
        categorical_features = [
            'publication_type', 'language'
        ]
        
        # Filtrer les colonnes existantes
        numeric_features = [f for f in numeric_features if f in df.columns]
        categorical_features = [f for f in categorical_features if f in df.columns]
        
        # Créer X
        X = df[numeric_features].copy()
        
        # Encoder les catégorielles
        for col in categorical_features:
            le = LabelEncoder()
            X[col] = le.fit_transform(df[col].fillna('unknown'))
            self.label_encoders[col] = le
        
        # Target : citation_count (proxy de la demande)
        y = df['citation_count'].fillna(0)
        
        self.feature_columns = X.columns.tolist()
        
        logger.info(f"✅ X: {X.shape}, y: {y.shape}")
        logger.info(f"📋 Features: {self.feature_columns}")
        
        return X, y
    
    def train(self, X, y):
        """
        Entraîner plusieurs modèles et choisir le meilleur
        """
        logger.info("🚀 Entraînement des modèles")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scaler
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Modèles à tester
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        best_score = -float('inf')
        best_model = None
        best_name = None
        
        for name, model in models.items():
            logger.info(f"📊 Test: {name}")
            
            # Utiliser les données scalées pour Linear Regression
            if name == 'Linear Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Métriques
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"   - R²: {r2:.4f}")
            logger.info(f"   - RMSE: {rmse:.4f}")
            logger.info(f"   - MAE: {mae:.4f}")
            
            if r2 > best_score:
                best_score = r2
                best_model = model
                best_name = name
        
        self.model = best_model
        self.metrics = {
            'best_model': best_name,
            'r2_score': best_score,
            'rmse': rmse,
            'mae': mae
        }
        
        logger.info(f"✅ Meilleur modèle: {best_name} (R²={best_score:.4f})")
        
        return self.metrics
    
    def predict(self, X):
        """Prédire"""
        if self.model is None:
            raise ValueError("❌ Modèle non entraîné")
        return self.model.predict(X)
    
    def save(self, path: str):
        """Sauvegarder le modèle"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics
        }, path)
        logger.info(f"💾 Modèle sauvegardé: {path}")
    
    @classmethod
    def load(cls, path: str):
        """Charger le modèle"""
        data = joblib.load(path)
        predictor = cls()
        predictor.model = data['model']
        predictor.scaler = data['scaler']
        predictor.label_encoders = data['label_encoders']
        predictor.feature_columns = data['feature_columns']
        predictor.metrics = data['metrics']
        return predictor


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    # Charger les données
    df = pd.read_csv("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    
    # Préparer
    predictor = DemandPredictor()
    X, y = predictor.prepare_data(df)
    
    # Entraîner
    metrics = predictor.train(X, y)
    print(f"\n📊 Métriques: {metrics}")
    
    # Sauvegarder
    predictor.save("/opt/airflow/data-science/models/demand_predictor.pkl")