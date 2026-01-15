# Portfolio Analyzer - Automated Startup Script
# This script starts all components needed to run the Portfolio Analyzer

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Portfolio Analyzer - Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Step 1: Check if Docker Desktop is running
Write-Host "[1/5] Checking Docker Desktop..." -ForegroundColor Yellow

$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "  -> Docker Desktop not running. Starting..." -ForegroundColor Yellow
    
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "  -> Waiting 30 seconds for Docker to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    } else {
        Write-Host "  -> ERROR: Docker Desktop not found at $dockerPath" -ForegroundColor Red
        Write-Host "  -> Please install Docker Desktop or update the path in this script" -ForegroundColor Red
        Write-Host ""
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
} else {
    Write-Host "  -> Docker Desktop is already running" -ForegroundColor Green
}

Write-Host ""

# Step 2: Start PostgreSQL Database
Write-Host "[2/5] Starting PostgreSQL Database..." -ForegroundColor Yellow

$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> ERROR: Docker is not ready yet. Waiting 10 more seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

docker start portfolio_db 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> PostgreSQL started successfully" -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    # Try to check if it's already running
    $dbStatus = docker ps --filter "name=portfolio_db" --format "{{.Status}}" 2>$null
    if ($dbStatus -match "Up") {
        Write-Host "  -> PostgreSQL is already running" -ForegroundColor Green
    } else {
        Write-Host "  -> WARNING: Could not start PostgreSQL (may need to create container first)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 3: Check if ports are available
Write-Host "[3/5] Checking if ports are available..." -ForegroundColor Yellow

$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$port8501 = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  -> Port 8000 already in use (API may already be running)" -ForegroundColor Yellow
} else {
    Write-Host "  -> Port 8000 is available" -ForegroundColor Green
}

if ($port8501) {
    Write-Host "  -> Port 8501 already in use (UI may already be running)" -ForegroundColor Yellow
} else {
    Write-Host "  -> Port 8501 is available" -ForegroundColor Green
}

Write-Host ""

# Step 4: Start API Server
Write-Host "[4/5] Starting API Server..." -ForegroundColor Yellow

if (-not $port8000) {
    $apiScript = @"
Set-Location '$ScriptDir'
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  Portfolio Analyzer - API Server' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting API server on port 8000...' -ForegroundColor Yellow
Write-Host ''
.\venv\Scripts\Activate.ps1
python -m backend.app.main
"@

    $apiScriptPath = Join-Path $ScriptDir "_temp_start_api.ps1"
    $apiScript | Out-File -FilePath $apiScriptPath -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $apiScriptPath
    Write-Host "  -> API Server window opened" -ForegroundColor Green
    Write-Host "  -> Waiting 10 seconds for API to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
} else {
    Write-Host "  -> Skipping API Server start (already running)" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Start Streamlit UI
Write-Host "[5/5] Starting Streamlit UI..." -ForegroundColor Yellow

if (-not $port8501) {
    $uiScript = @"
Set-Location '$ScriptDir'
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  Portfolio Analyzer - Web UI' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting Streamlit UI on port 8501...' -ForegroundColor Yellow
Write-Host ''
.\venv\Scripts\Activate.ps1
streamlit run ui\streamlit_app_wealth.py
"@

    $uiScriptPath = Join-Path $ScriptDir "_temp_start_ui.ps1"
    $uiScript | Out-File -FilePath $uiScriptPath -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $uiScriptPath
    Write-Host "  -> Streamlit UI window opened" -ForegroundColor Green
    Write-Host "  -> Waiting for UI to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "  -> Skipping UI start (already running)" -ForegroundColor Yellow
}

Write-Host ""

# Final message
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Portfolio Analyzer Started!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Main UI:    " -NoNewline
Write-Host "http://localhost:8501" -ForegroundColor Green
Write-Host "              (Wealth & Portfolio Dashboard)" -ForegroundColor Gray
Write-Host ""
Write-Host "  API Docs:   " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Green
Write-Host "              (Interactive API Documentation)" -ForegroundColor Gray
Write-Host ""
Write-Host "  API Server: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "              (REST API Endpoints)" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  - Bookmark http://localhost:8501 for quick access!" -ForegroundColor Cyan
Write-Host "  - Use 'Run Daily Update' button in UI sidebar to refresh data" -ForegroundColor Cyan
Write-Host "  - Keep the 2 PowerShell windows open while using the app" -ForegroundColor Cyan
Write-Host "  - Close the windows when done (Ctrl+C or just close)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monthly Workflow:" -ForegroundColor Yellow
Write-Host "  1. Click 'Run Daily Update' in sidebar (30 sec)" -ForegroundColor White
Write-Host "  2. Go to Tab 2, update wealth values (10 min)" -ForegroundColor White
Write-Host "  3. Go to Tab 1, click 'Save This Snapshot' (10 sec)" -ForegroundColor White
Write-Host "  4. Go to Tab 3, review trends and YoY %" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
