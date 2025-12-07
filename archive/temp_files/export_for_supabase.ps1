# Export Current PostgreSQL Database for Supabase Migration
# Run this BEFORE switching to Supabase

$ErrorActionPreference = "Stop"

Write-Host "📤 Portfolio Analyzer - Database Export Tool" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will export your current PostgreSQL database" -ForegroundColor Yellow
Write-Host "so you can import it into Supabase." -ForegroundColor Yellow
Write-Host ""

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if container exists
$containerExists = docker ps -a --format "{{.Names}}" | Select-String -Pattern "portfolio_db"

if (-not $containerExists) {
    Write-Host "❌ ERROR: portfolio_db container not found!" -ForegroundColor Red
    Write-Host "   Make sure your database container is running." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found portfolio_db container" -ForegroundColor Green
Write-Host ""

# Create exports directory
$exportDir = "exports"
if (-not (Test-Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir | Out-Null
    Write-Host "📁 Created exports directory" -ForegroundColor Green
}

# Generate export filename
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$exportFile = "$exportDir\portfolio_export_for_supabase_$timestamp.sql"

Write-Host "📦 Exporting database..." -ForegroundColor Yellow
Write-Host "   Container: portfolio_db" -ForegroundColor White
Write-Host "   Database: portfolio_db" -ForegroundColor White
Write-Host "   User: portfolio_user" -ForegroundColor White
Write-Host ""

try {
    # Export database
    docker exec -t portfolio_db pg_dump -U portfolio_user -d portfolio_db --clean --if-exists --no-owner --no-privileges > $exportFile
    
    if ($LASTEXITCODE -eq 0) {
        $fileSize = (Get-Item $exportFile).Length / 1KB
        Write-Host "✅ Export completed successfully!" -ForegroundColor Green
        Write-Host "   File: $exportFile" -ForegroundColor White
        Write-Host "   Size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor White
        Write-Host ""
        
        # Clean up the export file (remove problematic lines)
        Write-Host "🔧 Cleaning export file for Supabase..." -ForegroundColor Yellow
        
        $content = Get-Content $exportFile -Raw
        
        # Remove lines that Supabase doesn't need
        $content = $content -replace '(?m)^DROP DATABASE.*$', ''
        $content = $content -replace '(?m)^CREATE DATABASE.*$', ''
        $content = $content -replace '(?m)^\\connect.*$', ''
        $content = $content -replace '(?m)^ALTER DATABASE.*$', ''
        $content = $content -replace '(?m)^SET default_tablespace.*$', ''
        $content = $content -replace '(?m)^SET default_table_access_method.*$', ''
        
        # Save cleaned version
        $cleanFile = $exportFile -replace '\.sql$', '_cleaned.sql'
        $content | Set-Content -Path $cleanFile -NoNewline
        
        Write-Host "✅ Created cleaned version: $cleanFile" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║                                                            ║" -ForegroundColor Cyan
        Write-Host "║              📋 NEXT STEPS FOR SUPABASE                   ║" -ForegroundColor Cyan
        Write-Host "║                                                            ║" -ForegroundColor Cyan
        Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1️⃣  Create Supabase account at: https://supabase.com" -ForegroundColor White
        Write-Host "2️⃣  Create a new project" -ForegroundColor White
        Write-Host "3️⃣  Go to SQL Editor in Supabase dashboard" -ForegroundColor White
        Write-Host "4️⃣  Open the cleaned file: $cleanFile" -ForegroundColor White
        Write-Host "5️⃣  Copy and paste the SQL into Supabase SQL Editor" -ForegroundColor White
        Write-Host "6️⃣  Click 'Run' to import your data" -ForegroundColor White
        Write-Host "7️⃣  Copy your Supabase connection string" -ForegroundColor White
        Write-Host "8️⃣  Create .env file with DATABASE_URL" -ForegroundColor White
        Write-Host "9️⃣  Run: start_portfolio_supabase.ps1" -ForegroundColor White
        Write-Host ""
        Write-Host "📚 See SUPABASE_SETUP_GUIDE.md for detailed instructions!" -ForegroundColor Cyan
        Write-Host ""
        
    } else {
        throw "Export failed with exit code: $LASTEXITCODE"
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Export failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Check if Docker container is running: docker ps" -ForegroundColor White
    Write-Host "   2. Check container logs: docker logs portfolio_db" -ForegroundColor White
    Write-Host "   3. Verify database credentials" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📊 Export Summary:" -ForegroundColor Cyan
$exportFiles = Get-ChildItem -Path $exportDir -Filter "*.sql" | Sort-Object LastWriteTime -Descending
Write-Host "   Total exports: $($exportFiles.Count)" -ForegroundColor White
if ($exportFiles.Count -gt 0) {
    Write-Host "   Latest: $($exportFiles[0].Name)" -ForegroundColor White
}
Write-Host ""

Read-Host "Press Enter to exit"
