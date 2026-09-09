# backup_data.ps1
Write-Host "💾 BACKUP DES DONNÉES" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup_dir = "backups/$timestamp"
New-Item -Path $backup_dir -ItemType Directory -Force

Write-Host "📁 Backup dans: $backup_dir"

# Backup PostgreSQL
Write-Host "🐘 Backup PostgreSQL..." -ForegroundColor Yellow
docker exec edudata-postgres pg_dump -U airflow airflow > "$backup_dir/airflow.sql"

# Backup MinIO
Write-Host "📦 Backup MinIO..." -ForegroundColor Yellow
docker exec edudata-minio mc cp -r minio/raw-data/ "$backup_dir/minio/"

# Backup des DAGs
Write-Host "📋 Backup des DAGs..." -ForegroundColor Yellow
Copy-Item -Path "airflow/dags/*" -Destination "$backup_dir/dags/" -Recurse

Write-Host "`n✅ Backup terminé dans: $backup_dir" -ForegroundColor Green