# run_all.ps1
Write-Host "🚀 LANCEMENT COMPLET DU PROJET" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. Démarrer tous les services
Write-Host "`n📦 Démarrage des services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`n⏳ Attente du démarrage (90 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

# 2. Vérifier
Write-Host "`n📊 Conteneurs:" -ForegroundColor Yellow
docker ps

# 3. Créer les variables Airflow
Write-Host "`n🔧 Création des variables Airflow..." -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow variables set scrape_university_name "Université Hassan II" 2>$null
docker exec edudata-airflow-webserver airflow variables set scrape_university_url "https://www.univh2c.ma/" 2>$null
docker exec edudata-airflow-webserver airflow variables set scrape_max_pages "5" 2>$null
docker exec edudata-airflow-webserver airflow variables set openalex_search "Morocco university" 2>$null
docker exec edudata-airflow-webserver airflow variables set openalex_per_page "100" 2>$null
docker exec edudata-airflow-webserver airflow variables set openalex_year "2024" 2>$null

# 4. Activer les DAGs
Write-Host "`n🔄 Activation des DAGs..." -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags unpause 01_scrape_universities 2>$null
docker exec edudata-airflow-webserver airflow dags unpause 02_openalex_ingestion 2>$null
docker exec edudata-airflow-webserver airflow dags unpause 03_university_pipeline 2>$null

# 5. Déclencher les DAGs
Write-Host "`n▶️ Déclenchement des DAGs..." -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags trigger 01_scrape_universities 2>$null
docker exec edudata-airflow-webserver airflow dags trigger 02_openalex_ingestion 2>$null

# 6. Afficher les URLs
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ PROJET DÉMARRÉ" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "📊 Airflow:       http://localhost:8080 (admin/admin)" -ForegroundColor Cyan
Write-Host "📦 MinIO:         http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor Cyan
Write-Host "📈 Metabase:      http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔍 Elasticsearch: http://localhost:9200" -ForegroundColor Cyan
Write-Host "📊 Kibana:        http://localhost:5601" -ForegroundColor Cyan
Write-Host "⚡ Spark:         http://localhost:8081" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan