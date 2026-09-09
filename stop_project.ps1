# stop_project.ps1
Write-Host "🛑 ARRÊT DU PROJET EDUDATA MOROCCO" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "`n🔄 Arrêt des services..." -ForegroundColor Yellow
docker-compose -f infrastructure/docker/docker-compose.yml down

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services arrêtés avec succès!" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de l'arrêt des services" -ForegroundColor Red
}

Write-Host "`n✅ PROJET ARRÊTÉ" -ForegroundColor Cyan