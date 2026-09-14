# test_dags.ps1
Write-Host "🧪 TEST DES DAGS 04-07" -ForegroundColor Cyan
Write-Host "=" * 60

# Attendre que DAG 04 finisse
Write-Host "`n⏳ Attente de la fin du DAG 04..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

Write-Host "`n📊 État DAG 04 (Spark):" -ForegroundColor Yellow
docker exec edudata-airflow-webserver airflow dags list-runs -d 04_spark_transformation

# DAG 05
Write-Host "`n🚀 DAG 05 (Hudi)..." -ForegroundColor Cyan
docker exec edudata-airflow-webserver airflow dags unpause 05_hudi_lakehouse
docker exec edudata-airflow-webserver airflow dags trigger 05_hudi_lakehouse
Start-Sleep -Seconds 30
docker exec edudata-airflow-webserver airflow dags list-runs -d 05_hudi_lakehouse

# DAG 06
Write-Host "`n🚀 DAG 06 (PostgreSQL)..." -ForegroundColor Cyan
docker exec edudata-airflow-webserver airflow dags unpause 06_export_postgres
docker exec edudata-airflow-webserver airflow dags trigger 06_export_postgres
Start-Sleep -Seconds 60
docker exec edudata-airflow-webserver airflow dags list-runs -d 06_export_postgres

# Vérifier PostgreSQL
Write-Host "`n📊 Vérification PostgreSQL:" -ForegroundColor Yellow
docker exec edudata-postgres psql -U airflow -d analytics -c "SELECT COUNT(*) FROM publications;" 2>$null

# DAG 07
Write-Host "`n🚀 DAG 07 (Elasticsearch)..." -ForegroundColor Cyan
docker exec edudata-airflow-webserver airflow dags unpause 07_index_elasticsearch
docker exec edudata-airflow-webserver airflow dags trigger 07_index_elasticsearch
Start-Sleep -Seconds 60
docker exec edudata-airflow-webserver airflow dags list-runs -d 07_index_elasticsearch

# Vérifier Elasticsearch
Write-Host "`n📊 Vérification Elasticsearch:" -ForegroundColor Yellow
curl http://localhost:9200/publications/_count

Write-Host "`n" + "=" * 60
Write-Host "✅ TESTS TERMINÉS" -ForegroundColor Green