# Portfolio Analyzer - Supabase Edition
# One-click launcher - No Docker needed!

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       💰 Portfolio & Wealth Analyzer - Supabase         ║
║              Cloud-Connected Edition                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"@

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-ColorOutput Red "❌ ERROR: .env file not found!"
    Write-ColorOutput Yellow "`n📋 Please create a .env file with your Supabase connection details."
    Write-ColorOutput Yellow "   Template available in .env.example"
    Write-ColorOutput Yellow "`nSteps:"
    Write-ColorOutput Yellow "   1. Copy .env.example to .env"
    Write-ColorOutput Yellow "   2. Add your Supabase connection string"
    Write-ColorOutput Yellow "   3. Run this script again"
    Write-ColorOutput Yellow "`nSee SUPABASE_SETUP_GUIDE.md for detailed instructions.`n"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorOutput Green "✅ Found .env configuration file"

# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
        if ($key -eq "DATABASE_URL") {
            # Mask password in output
            $maskedUrl = $value -replace ':[^@]+@', ':****@'
            Write-ColorOutput Cyan "🔗 Database: $maskedUrl"
        }
    }
}

# Test database connection
Write-ColorOutput Yellow "`n🔍 Testing Supabase connection..."
try {
    $testScript = @"
import os
from sqlalchemy import create_engine, text
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Connected to Supabase successfully!')
        exit(0)
except Exception as e:
    print(f'❌ Connection failed: {str(e)}')
    exit(1)
"@
    
    $testScript | python -
    if ($LASTEXITCODE -ne 0) {
        throw "Database connection test failed"
    }
} catch {
    Write-ColorOutput Red "`n❌ ERROR: Cannot connect to Supabase database!"
    Write-ColorOutput Yellow "`nTroubleshooting:"
    Write-ColorOutput Yellow "   1. Check your DATABASE_URL in .env file"
    Write-ColorOutput Yellow "   2. Verify your internet connection"
    Write-ColorOutput Yellow "   3. Confirm Supabase project is active"
    Write-ColorOutput Yellow "   4. Check password is correct"
    Write-ColorOutput Yellow "`nSee SUPABASE_SETUP_GUIDE.md for help.`n"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python processes are already running
$apiProcess = Get-Process | Where-Object { $_.ProcessName -match "python" -and $_.CommandLine -match "uvicorn" }
$uiProcess = Get-Process | Where-Object { $_.ProcessName -match "python" -and $_.CommandLine -match "streamlit" }

if ($apiProcess) {
    Write-ColorOutput Yellow "⚠️  API server already running (PID: $($apiProcess.Id))"
} else {
    Write-ColorOutput Cyan "`n🚀 Starting FastAPI Backend..."
    
    # Start API in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
        cd '$PWD\backend'
        Write-Host '🔧 Starting API Server on http://localhost:8000' -ForegroundColor Cyan
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@ -WindowStyle Minimized
    
    Write-ColorOutput Green "✅ API server starting..."
    Start-Sleep -Seconds 3
}

if ($uiProcess) {
    Write-ColorOutput Yellow "⚠️  UI already running (PID: $($uiProcess.Id))"
} else {
    Write-ColorOutput Cyan "`n🎨 Starting Streamlit UI..."
    
    # Start UI in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
        cd '$PWD\ui'
        Write-Host '🌐 Starting Streamlit UI on http://localhost:8501' -ForegroundColor Cyan
        python -m streamlit run streamlit_app_wealth.py --server.port 8501 --server.headless true
"@ -WindowStyle Minimized
    
    Write-ColorOutput Green "✅ UI server starting..."
    Start-Sleep -Seconds 5
}

# Wait for services to be ready
Write-ColorOutput Yellow "`n⏳ Waiting for services to be ready..."

$maxAttempts = 30
$attempt = 0
$apiReady = $false
$uiReady = $false

while ($attempt -lt $maxAttempts) {
    try {
        if (-not $apiReady) {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $apiReady = $true
                Write-ColorOutput Green "✅ API Ready!"
            }
        }
        
        if (-not $uiReady) {
            $response = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $uiReady = $true
                Write-ColorOutput Green "✅ UI Ready!"
            }
        }
        
        if ($apiReady -and $uiReady) {
            break
        }
    } catch {
        # Still waiting...
    }
    
    Start-Sleep -Seconds 1
    $attempt++
}

if (-not ($apiReady -and $uiReady)) {
    Write-ColorOutput Red "`n⚠️  Services took longer than expected to start"
    Write-ColorOutput Yellow "    Check the terminal windows for errors"
}

# Open browser
Write-ColorOutput Cyan "`n🌐 Opening Portfolio Analyzer in your browser..."
Start-Sleep -Seconds 2
Start-Process "http://localhost:8501"

Write-ColorOutput Green @"

╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              ✅ Portfolio Analyzer is Running!           ║
║                                                          ║
║  📊 UI:  http://localhost:8501                          ║
║  🔧 API: http://localhost:8000/docs                     ║
║  💾 DB:  Supabase Cloud (Connected)                     ║
║                                                          ║
║  ℹ️  Access from any device on your network!            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

"@

Write-ColorOutput Yellow "📝 Tips:"
Write-ColorOutput White "   • UI will open automatically in your browser"
Write-ColorOutput White "   • API docs available at: http://localhost:8000/docs"
Write-ColorOutput White "   • Data is stored securely in Supabase cloud"
Write-ColorOutput White "   • Close terminal windows to stop services"
Write-ColorOutput White "   • Your data syncs automatically!`n"

Write-ColorOutput Cyan "Press Enter to open API documentation, or Ctrl+C to continue..."
$null = Read-Host
Start-Process "http://localhost:8000/docs"

Write-ColorOutput Green "`n✨ Portfolio Analyzer is ready to use!"
Write-ColorOutput Yellow "   Close this window or press Ctrl+C when done.`n"

# Keep script running
while ($true) {
    Start-Sleep -Seconds 60
    
    # Check if services are still running
    $apiRunning = Get-Process | Where-Object { $_.ProcessName -match "python" -and $_.CommandLine -match "uvicorn" }
    $uiRunning = Get-Process | Where-Object { $_.ProcessName -match "python" -and $_.CommandLine -match "streamlit" }
    
    if (-not $apiRunning -or -not $uiRunning) {
        Write-ColorOutput Red "`n⚠️  One or more services stopped!"
        Write-ColorOutput Yellow "   Restart the launcher to continue.`n"
        break
    }
}
