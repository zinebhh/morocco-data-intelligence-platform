"""
Clustering des universités par profil
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import joblib
import logging

logger = logging.getLogger(__name__)


class UniversityClusterer:
    """Clustering des universités"""
    
    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters
        self.model = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.metrics = {}
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Préparer les features de clustering"""
        logger.info("🔧 Préparation des features")
        
        # Grouper par journal (comme proxy d'université)
        features = df.groupby('journal').agg({
            'citation_count': ['mean', 'sum', 'count'],
            'publication_year': ['mean', 'min', 'max'],
            'is_open_access': 'mean',
            'title_length': 'mean'
        }).reset_index()
        
        # Aplatir les colonnes
        features.columns = ['_'.join(col).strip('_') for col in features.columns]
        
        # Supprimer les NaN
        features = features.dropna()
        
        logger.info(f"📊 Features: {features.shape}")
        
        return features
    
    def find_optimal_clusters(self, X: np.ndarray, max_k: int = 10):
        """Trouver le nombre optimal de clusters"""
        logger.info("🔍 Recherche du nombre optimal de clusters")
        
        inertias = []
        silhouette_scores = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, labels))
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].plot(range(2, max_k + 1), inertias, 'bo-')
        axes[0].set_xlabel('Nombre de clusters')
        axes[0].set_ylabel('Inertie')
        axes[0].set_title('Méthode Elbow')
        axes[0].grid(True)
        
        axes[1].plot(range(2, max_k + 1), silhouette_scores, 'ro-')
        axes[1].set_xlabel('Nombre de clusters')
        axes[1].set_ylabel('Silhouette Score')
        axes[1].set_title('Silhouette Score')
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig('/opt/airflow/data-science/evaluation/clustering_analysis.png')
        plt.show()
        
        # Meilleur k
        best_k = range(2, max_k + 1)[np.argmax(silhouette_scores)]
        logger.info(f"✅ Meilleur k: {best_k}")
        
        return best_k
    
    def train(self, X: pd.DataFrame):
        """Entraîner le clustering"""
        logger.info(f"🚀 Entraînement du clustering (k={self.n_clusters})")
        
        # Scaler
        X_scaled = self.scaler.fit_transform(X.select_dtypes(include=[np.number]))
        
        # KMeans
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        labels = self.model.fit_predict(X_scaled)
        
        # Métriques
        silhouette = silhouette_score(X_scaled, labels)
        inertia = self.model.inertia_
        
        self.metrics = {
            'n_clusters': self.n_clusters,
            'silhouette_score': silhouette,
            'inertia': inertia
        }
        
        logger.info(f"✅ Silhouette Score: {silhouette:.4f}")
        logger.info(f"✅ Inertie: {inertia:.4f}")
        
        # PCA pour visualisation
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Plot
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis', alpha=0.6)
        plt.colorbar(scatter, label='Cluster')
        plt.xlabel('PCA 1')
        plt.ylabel('PCA 2')
        plt.title(f'Clustering des universités (k={self.n_clusters})')
        plt.savefig('/opt/airflow/data-science/evaluation/clustering_visualization.png')
        plt.show()
        
        return labels, self.metrics
    
    def save(self, path: str):
        """Sauvegarder"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'pca': self.pca,
            'metrics': self.metrics
        }, path)
        logger.info(f"💾 Modèle sauvegardé: {path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    df = pd.read_csv("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    
    clusterer = UniversityClusterer(n_clusters=3)
    features = clusterer.prepare_features(df)
    
    if len(features) > 10:
        labels, metrics = clusterer.train(features)
        print(f"\n📊 Métriques: {metrics}")
        clusterer.save("/opt/airflow/data-science/models/university_clusterer.pkl")
    else:
        print("⚠️ Pas assez de données pour le clustering")