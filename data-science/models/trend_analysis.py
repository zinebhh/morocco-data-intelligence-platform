"""
Analyse des tendances de recherche
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyseur de tendances"""
    
    def __init__(self):
        self.trends = {}
    
    def analyze_yearly_trends(self, df: pd.DataFrame):
        """Analyser les tendances par année"""
        logger.info("📈 Analyse des tendances par année")
        
        # Grouper par année
        yearly = df.groupby('publication_year').agg({
            'id': 'count',
            'citation_count': ['sum', 'mean']
        }).reset_index()
        
        yearly.columns = ['year', 'publications', 'total_citations', 'avg_citations']
        yearly = yearly[yearly['year'] >= 2020]
        
        # Régression linéaire
        X = yearly['year'].values.reshape(-1, 1)
        y = yearly['publications'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Prédiction
        y_pred = model.predict(X)
        
        # Tendance
        slope = model.coef_[0]
        trend_direction = "📈 Croissante" if slope > 0 else "📉 Décroissante"
        
        self.trends['yearly'] = {
            'slope': slope,
            'direction': trend_direction,
            'r2': model.score(X, y),
            'data': yearly.to_dict('records')
        }
        
        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(yearly['year'], yearly['publications'], 'bo-', label='Réel')
        plt.plot(yearly['year'], y_pred, 'r--', label='Tendance')
        plt.xlabel('Année')
        plt.ylabel('Nombre de publications')
        plt.title(f'Tendance des publications ({trend_direction})')
        plt.legend()
        plt.grid(True)
        plt.savefig('/opt/airflow/data-science/evaluation/trend_yearly.png')
        plt.show()
        
        logger.info(f"✅ Tendance: {trend_direction} (slope={slope:.2f})")
        
        return self.trends['yearly']
    
    def analyze_type_trends(self, df: pd.DataFrame):
        """Analyser les tendances par type"""
        logger.info("📈 Analyse des tendances par type")
        
        type_trends = df.groupby(['publication_type', 'publication_year']).size().reset_index(name='count')
        
        self.trends['type'] = type_trends.to_dict('records')
        
        # Plot
        pivot = type_trends.pivot(index='publication_year', columns='publication_type', values='count').fillna(0)
        
        plt.figure(figsize=(12, 6))
        for col in pivot.columns:
            plt.plot(pivot.index, pivot[col], marker='o', label=col)
        
        plt.xlabel('Année')
        plt.ylabel('Nombre de publications')
        plt.title('Tendances par type de publication')
        plt.legend()
        plt.grid(True)
        plt.savefig('/opt/airflow/data-science/evaluation/trend_by_type.png')
        plt.show()
        
        return self.trends['type']
    
    def analyze_keyword_trends(self, df: pd.DataFrame):
        """Analyser les tendances des mots-clés"""
        logger.info("📈 Analyse des tendances des mots-clés")
        
        keywords = {
            'AI/ML': r'ai|artificial intelligence|machine learning|deep learning',
            'Morocco': r'morocco|moroccan',
            'University': r'university|université',
            'COVID': r'covid|pandemic',
            'Climate': r'climate|environment'
        }
        
        results = {}
        for keyword, pattern in keywords.items():
            df_keyword = df[df['title'].str.lower().str.contains(pattern, regex=True, na=False)]
            yearly = df_keyword.groupby('publication_year').size()
            results[keyword] = yearly.to_dict()
        
        self.trends['keywords'] = results
        
        # Plot
        plt.figure(figsize=(12, 6))
        for keyword, data in results.items():
            years = sorted(data.keys())
            counts = [data[y] for y in years]
            plt.plot(years, counts, marker='o', label=keyword)
        
        plt.xlabel('Année')
        plt.ylabel('Nombre de publications')
        plt.title('Tendances des mots-clés')
        plt.legend()
        plt.grid(True)
        plt.savefig('/opt/airflow/data-science/evaluation/trend_keywords.png')
        plt.show()
        
        return self.trends['keywords']


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    df = pd.read_csv("/opt/airflow/data_engineering/transformations/output/openalex_transformed.csv")
    
    analyzer = TrendAnalyzer()
    analyzer.analyze_yearly_trends(df)
    analyzer.analyze_type_trends(df)
    analyzer.analyze_keyword_trends(df)