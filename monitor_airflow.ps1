# monitor_airflow.ps1
Write-Host "📊 MONITORING AIRFLOW" -ForegroundColor Cyan
Write-Host "=" * 50

# Voir les conteneurs
Write-Host "`n📦 Conteneurs:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Voir les DAGs
Write-Host "`n📋 DAGs:" -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags list

# Voir les runs récents
Write-Host "`n🔄 Derniers runs:" -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags list-runs -d hello_world -c 5

# Voir les logs récents
Write-Host "`n📝 Logs récents:" -ForegroundColor Yellow
docker logs edudata-airflow-webserver --tail 20 | findstr -i "dag\|error"

Write-Host "`n✅ Monitoring terminé" -ForegroundColor Green