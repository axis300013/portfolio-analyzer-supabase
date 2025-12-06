# Portfolio Analyzer - Windows Installer Creator
# Creates a self-installing package

$ErrorActionPreference = "Stop"

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host " Creating Windows Installer" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check if Inno Setup is installed (for creating installers)
$innoSetup = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $innoSetup)) {
    Write-Host "Inno Setup not found. Creating portable ZIP package instead..." -ForegroundColor Yellow
    
    # Create dist directory
    $distDir = "dist\PortfolioAnalyzer_Portable"
    if (Test-Path $distDir) {
        Remove-Item $distDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $distDir -Force | Out-Null
    
    Write-Host "`nCopying files..." -ForegroundColor Yellow
    
    # Copy essential files
    Copy-Item "backend" -Destination "$distDir\backend" -Recurse -Force
    Copy-Item "ui" -Destination "$distDir\ui" -Recurse -Force
    Copy-Item ".env.example" -Destination "$distDir\.env.example" -Force
    Copy-Item "START_PORTABLE.bat" -Destination "$distDir\START_PORTABLE.bat" -Force
    Copy-Item "PORTABLE_README.md" -Destination "$distDir\README.md" -Force
    Copy-Item "QUICK_START_SUPABASE.md" -Destination "$distDir\QUICK_START.md" -Force
    
    # Copy user's .env if exists (commented out for security)
    # Copy-Item ".env" -Destination "$distDir\.env" -Force
    
    Write-Host "`n✅ Files copied to: $distDir" -ForegroundColor Green
    
    # Create installer script
    $installerScript = @"
@echo off
echo ================================================
echo   Portfolio Analyzer - One-Time Setup
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed!
    echo.
    echo Please install Python 3.13 from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt --quiet
cd ..

echo Installing UI dependencies...
cd ui
pip install -r requirements.txt --quiet
cd ..

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo IMPORTANT: Create your .env file
echo   1. Copy .env.example to .env
echo   2. Add your Supabase connection string
echo.
echo Then double-click: START_PORTABLE.bat
echo.
pause
"@
    
    $installerScript | Set-Content -Path "$distDir\INSTALL.bat" -Encoding ASCII
    
    Write-Host "`nCreating ZIP package..." -ForegroundColor Yellow
    
    $zipFile = "dist\PortfolioAnalyzer_Portable.zip"
    if (Test-Path $zipFile) {
        Remove-Item $zipFile -Force
    }
    
    Compress-Archive -Path $distDir -DestinationPath $zipFile -Force
    
    $zipSize = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)
    
    Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║         ✅ PORTABLE PACKAGE CREATED!                   ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📦 Package: $zipFile" -ForegroundColor Cyan
    Write-Host "   Size: $zipSize MB" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 To install on another PC:" -ForegroundColor Yellow
    Write-Host "   1. Extract the ZIP file" -ForegroundColor White
    Write-Host "   2. Double-click INSTALL.bat (one-time setup)" -ForegroundColor White
    Write-Host "   3. Create .env file with Supabase connection" -ForegroundColor White
    Write-Host "   4. Double-click START_PORTABLE.bat to run" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Requirements on target PC:" -ForegroundColor Yellow
    Write-Host "   • Python 3.13+ (auto-installs dependencies)" -ForegroundColor White
    Write-Host "   • Internet connection (for Supabase)" -ForegroundColor White
    Write-Host ""
    
    # Open dist folder
    explorer "dist"
    
} else {
    Write-Host "Inno Setup found. Creating full installer..." -ForegroundColor Green
    Write-Host "This feature requires additional setup." -ForegroundColor Yellow
}

Write-Host "`n✨ Done!" -ForegroundColor Green
pause
