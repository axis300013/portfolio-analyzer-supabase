# Backup Portfolio Analyzer Database from Supabase
# Creates a local backup file with timestamp

$ErrorActionPreference = "Stop"

Write-Host "💾 Portfolio Analyzer - Supabase Backup Tool" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "❌ ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "   Please create .env file with DATABASE_URL" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Load DATABASE_URL from .env
$databaseUrl = (Get-Content .env | Where-Object { $_ -match '^DATABASE_URL=' }) -replace 'DATABASE_URL=', ''

if (-not $databaseUrl) {
    Write-Host "❌ ERROR: DATABASE_URL not found in .env file!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create backups directory if it doesn't exist
$backupDir = "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "📁 Created backups directory" -ForegroundColor Green
}

# Generate backup filename with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFile = "$backupDir\portfolio_backup_$timestamp.sql"

Write-Host "🔍 Connecting to Supabase..." -ForegroundColor Yellow

try {
    # Use Python to create backup (works on any system)
    $backupScript = @"
import os
import subprocess
from urllib.parse import urlparse

# Parse connection string
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('❌ DATABASE_URL not found')
    exit(1)

parsed = urlparse(db_url)
host = parsed.hostname
port = parsed.port
user = parsed.username
password = parsed.password
database = parsed.path.lstrip('/')

print(f'📦 Creating backup...')
print(f'   Host: {host}')
print(f'   Database: {database}')

# Set password environment variable
os.environ['PGPASSWORD'] = password

# Run pg_dump
cmd = [
    'pg_dump',
    '-h', host,
    '-p', str(port),
    '-U', user,
    '-d', database,
    '--clean',
    '--if-exists',
    '--no-owner',
    '--no-privileges'
]

with open('$($backupFile -replace '\\', '/')', 'w', encoding='utf-8') as f:
    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f'❌ Backup failed: {result.stderr}')
        exit(1)

print('✅ Backup completed successfully!')
"@

    $env:DATABASE_URL = $databaseUrl
    $backupScript | python -
    
    if ($LASTEXITCODE -eq 0) {
        $fileSize = (Get-Item $backupFile).Length / 1KB
        Write-Host ""
        Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
        Write-Host "   File: $backupFile" -ForegroundColor White
        Write-Host "   Size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 To restore this backup:" -ForegroundColor Cyan
        Write-Host "   psql <CONNECTION_STRING> < $backupFile" -ForegroundColor White
        Write-Host ""
    } else {
        throw "Backup failed"
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Backup failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Ensure pg_dump is installed (PostgreSQL client tools)" -ForegroundColor White
    Write-Host "   2. Check your internet connection" -ForegroundColor White
    Write-Host "   3. Verify DATABASE_URL in .env is correct" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📊 Backup Statistics:" -ForegroundColor Cyan
$backupFiles = Get-ChildItem -Path $backupDir -Filter "*.sql" | Sort-Object LastWriteTime -Descending
Write-Host "   Total backups: $($backupFiles.Count)" -ForegroundColor White
Write-Host "   Total size: $([math]::Round(($backupFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 2)) MB" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
