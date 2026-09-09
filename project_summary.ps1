# project_summary.ps1
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "📊 MOROCCO DATA INTELLIGENCE PLATFORM" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`n📦 SERVICES EN COURS:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n📋 DAGS AIRFLOW:" -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags list

Write-Host "`n🔄 DERNIERS RUNS:" -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags list-runs -d openalex_complete -c 3
docker exec edudata-airflow-webserver airflow dags list-runs -d hudi_full_pipeline -c 3

Write-Host "`n💾 ESPACE DISQUE:" -ForegroundColor Yellow
docker system df

Write-Host "`n🔗 URLS D'ACCÈS:" -ForegroundColor Green
Write-Host "   Airflow: http://localhost:8080 (admin/admin)" -ForegroundColor Cyan
Write-Host "   MinIO:   http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor Cyan
Write-Host "   PostgreSQL: localhost:5432 (airflow/airflow)" -ForegroundColor Cyan

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ PROJET OPÉRATIONNEL" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan