# Morocco Data Intelligence Platform (EduData Morocco)

## 📋 Description
Plateforme Cloud-Native de Big Data & IA pour l'analyse des universités marocaines.

## 🏗️ Architecture
SOURCES
│
┌──────────────┼──────────────┐
▼ ▼ ▼
UNIVERSITY OPENALEX PDFs
WEBSITES API
│ │ │
└──────────────┼──────────────┘
│
▼
AIRFLOW DAG
│
┌──────────────┼──────────────┐
▼ ▼ ▼
scrape collect extract
validate map process
upload validate clean
│ │ │
└──────────────┼──────────────┘
│
▼
MINIO
(raw-data)
│
▼
SPARK TRANSFORMATION
│
▼
HUDI LAKEHOUSE
│
▼
POSTGRES / ELASTICSEARCH
│
▼
API / DASHBOARD / BI

text

## 📦 Services

| Service | URL | Login |
|---------|-----|-------|
| Airflow | http://localhost:8080 | admin/admin |
| MinIO | http://localhost:9001 | minioadmin/minioadmin |
| PostgreSQL | localhost:5432 | airflow/airflow |

## 🚀 Démarrer le projet

```powershell
# Démarrer tous les services
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Voir les logs
docker logs edudata-airflow-webserver -f

# Arrêter les services
docker-compose -f infrastructure/docker/docker-compose.yml down
