# Morocco Data Intelligence Platform (EduData Morocco)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/zinebhh/morocco-data-intelligence-platform)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue)](https://www.docker.com/)

Plateforme Cloud-Native de Big Data & IA pour l'analyse des universités marocaines.

## 📋 Description

**EduData Morocco** est une plateforme intelligente de données universitaires marocaines capable de :
- Collecter des données depuis plusieurs sources hétérogènes (APIs, scraping, PDFs)
- Stocker dans un Data Lake / Lakehouse
- Transformer avec Apache Spark
- Orchestrer avec Apache Airflow
- Analyser via SQL et des outils de BI
- Entraîner des modèles de Machine Learning / IA
- Exposer les résultats via une API REST et une application web
- Déployer dans le Cloud avec une chaîne CI/CD complète

## 🎯 Objectifs Métier

- Centraliser les données universitaires marocaines
- Fournir des indicateurs et tableaux de bord
- Prédire la demande pour une formation
- Recommander des formations aux étudiants
- Détecter automatiquement les informations clés dans les documents
- Offrir un assistant conversationnel (RAG)

## 🏗️ Architecture

### Flux de données

\\\
Sources → Ingestion → Airflow → MinIO/S3 → Spark → Hudi → 
PostgreSQL (Analytics) + Elasticsearch (Search) + ML Models →
FastAPI → React Dashboard
\\\

### Stack Technologique

| Couche | Technologie |
|--------|-------------|
| **Data Lake** | MinIO / Amazon S3 |
| **Lakehouse** | Apache Hudi |
| **Orchestration** | Apache Airflow |
| **Processing** | Apache Spark (PySpark) |
| **Analytics** | PostgreSQL + Metabase |
| **Search** | Elasticsearch |
| **ML/IA** | scikit-learn, Transformers, LangChain |
| **Backend** | FastAPI (Python) |
| **Frontend** | React |
| **Monitoring** | Prometheus + Grafana |
| **CI/CD** | GitHub Actions |
| **Infrastructure** | Docker, Terraform |

## 📦 Versions du Projet

| Version | Contenu | Statut |
|---------|---------|--------|
| **V1** | Data Engineering (Ingestion, Airflow, Spark, Hudi) | 🚧 En cours |
| **V2** | Analytics (SQL, Metabase, KPIs) | 📋 Planifié |
| **V3** | Data Science (ML, Prédiction, Clustering) | 📋 Planifié |
| **V4** | IA & NLP (Classification, Extraction, RAG) | 📋 Planifié |
| **V5** | Software Engineering (FastAPI, React, Auth) | 📋 Planifié |
| **V6** | Big Data (Optimisation, Performance) | 📋 Planifié |
| **V7** | Cloud (AWS, S3, Database) | 📋 Planifié |
| **V8** | DevOps (CI/CD, Monitoring, Terraform) | 📋 Planifié |

## 🚀 Installation

### Prérequis

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- Git

### Démarrage rapide

\\\ash
# Cloner le projet
git clone https://github.com/zinebhh/morocco-data-intelligence-platform.git
cd morocco-data-intelligence-platform

# Démarrer les services Docker
docker-compose up -d

# Installer les dépendances Python
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations
\\\

### Services disponibles

| Service | URL | Description |
|---------|-----|-------------|
| MinIO | http://localhost:9001 | Data Lake Console |
| PostgreSQL | localhost:5432 | Data Warehouse |
| Elasticsearch | http://localhost:9200 | Moteur de recherche |
| Metabase | http://localhost:3000 | BI Dashboards |
| Airflow | http://localhost:8080 | Orchestration |

## 📁 Structure du Projet

\\\
morocco-data-intelligence-platform/
├── data-engineering/     # V1 - Pipelines ETL
├── airflow/              # V1 - Orchestration DAGs
├── spark/                # V1 - Jobs Spark
├── lakehouse/            # V1 - Hudi & Schemas
├── analytics/            # V2 - SQL & BI
├── data-science/         # V3 - ML Models
├── nlp/                  # V4 - NLP Processing
├── ai/                   # V4 - RAG Assistant
├── backend/              # V5 - FastAPI
├── frontend/             # V5 - React
├── elasticsearch/        # V5 - Search Config
├── infrastructure/       # V7-8 - Cloud & DevOps
├── monitoring/           # V8 - Prometheus & Grafana
└── tests/                # Tests unitaires & intégration
\\\

## 📊 Sources de Données

- **OpenAlex API** : Publications scientifiques
- **Crossref API** : Métadonnées des publications
- **Scraping** : Sites web universitaires marocains
- **PDFs** : Documents universitaires (programmes, règlements)

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez le [guide de contribution](docs/guides/contributing.md).

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**Zineb Hamouchi** - [GitHub](https://github.com/zinebhh)

## 🙏 Remerciements

- Master Big Data & Cloud Computing (BD2C)
- Université [à compléter]

---

*Construit avec ❤️ au Maroc*
