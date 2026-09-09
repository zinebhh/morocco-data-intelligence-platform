# run_hudi_pipeline.ps1
Write-Host "🚀 DÉMARRAGE PIPELINE HUDI" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. Démarrer Spark avec Hudi
Write-Host "`n📦 Démarrage Spark avec Hudi..." -ForegroundColor Yellow

# 2. Lancer le job
Write-Host "`n🚀 Lancement du job Hudi..." -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags unpause hudi_full_pipeline
docker exec edudata-airflow-webserver airflow dags trigger hudi_full_pipeline

Write-Host "`n📊 Vérification..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
docker exec edudata-airflow-webserver airflow dags list-runs -d hudi_full_pipeline

Write-Host "`n✅ Pipeline Hudi démarré" -ForegroundColor Green