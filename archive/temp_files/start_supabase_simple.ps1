# Portfolio Analyzer - Supabase Edition Launcher
# Simple and reliable startup script

$ErrorActionPreference = "Stop"

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host " Portfolio Analyzer - Supabase" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your Supabase connection." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Found .env configuration" -ForegroundColor Green

# Test database connection
Write-Host "`nTesting Supabase connection..." -ForegroundColor Yellow

$testResult = python -c @"
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
try:
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
"@

if ($testResult -ne 'OK') {
    Write-Host "ERROR: Cannot connect to Supabase!" -ForegroundColor Red
    Write-Host "Details: $testResult" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Connected to Supabase successfully!" -ForegroundColor Green

# Start API server
Write-Host "`nStarting FastAPI backend..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$PWD\backend'
Write-Host 'API Server on http://localhost:8000' -ForegroundColor Cyan
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@ -WindowStyle Minimized

Start-Sleep -Seconds 3

# Start Streamlit UI
Write-Host "Starting Streamlit UI..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$PWD\ui'
Write-Host 'Streamlit UI on http://localhost:8501' -ForegroundColor Cyan
streamlit run streamlit_app_wealth.py --server.port 8501 --server.headless true
"@ -WindowStyle Minimized

Start-Sleep -Seconds 5

# Wait for services
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            break
        }
    } catch {
        # Still waiting
    }
    Start-Sleep -Seconds 1
    $attempt++
}

# Open browser
Write-Host "`nOpening browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:8501"

Write-Host "`n================================" -ForegroundColor Green
Write-Host " Portfolio Analyzer is Running!" -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Green

Write-Host "UI:  http://localhost:8501" -ForegroundColor White
Write-Host "API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "DB:  Supabase Cloud`n" -ForegroundColor White

Write-Host "Press Ctrl+C to stop, or close this window." -ForegroundColor Yellow

# Keep running
while ($true) {
    Start-Sleep -Seconds 60
}
