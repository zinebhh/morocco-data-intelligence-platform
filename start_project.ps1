# start_project.ps1 - Script de démarrage du projet
Write-Host "🚀 DÉMARRAGE DU PROJET EDUDATA MOROCCO" -ForegroundColor Cyan
Write-Host "=" * 60

# Vérifier Docker
Write-Host "`n🐳 Vérification de Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker n'est pas installé. Veuillez installer Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker OK" -ForegroundColor Green

# Démarrer les services
Write-Host "`n🔄 Démarrage des services..." -ForegroundColor Yellow
docker-compose -f infrastructure/docker/docker-compose.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services démarrés avec succès!" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du démarrage des services" -ForegroundColor Red
    exit 1
}

# Attendre que les services soient prêts
Write-Host "`n⏳ Attente du démarrage des services..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Afficher les URLs
Write-Host "`n📊 SERVICES DISPONIBLES:" -ForegroundColor Cyan
Write-Host "   Airflow:     http://localhost:8080 (admin/admin)" -ForegroundColor Green
Write-Host "   MinIO:       http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor Green
Write-Host "   Metabase:    http://localhost:3000" -ForegroundColor Green
Write-Host "   PostgreSQL:  localhost:5432 (airflow/airflow)" -ForegroundColor Green
Write-Host "   Elasticsearch: http://localhost:9200" -ForegroundColor Green
Write-Host "   Prometheus:  http://localhost:9090" -ForegroundColor Green
Write-Host "   Grafana:     http://localhost:3001 (admin/admin)" -ForegroundColor Green

Write-Host "`n" + "=" * 60
Write-Host "✅ PROJET DÉMARRÉ AVEC SUCCÈS!" -ForegroundColor Cyan
Write-Host "📝 Pour arrêter: docker-compose -f infrastructure/docker/docker-compose.yml down" -ForegroundColor Yellow