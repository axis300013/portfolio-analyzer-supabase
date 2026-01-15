@echo off
REM Portfolio Analyzer - Daily Update Runner (REST API - No Port 5432 Required)
REM This runs the ETL process using Supabase REST API (HTTPS only)

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Portfolio Analyzer - Daily Update
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your Supabase connection.
    echo See .env.example for template.
    echo.
    pause
    exit /b 1
)

echo Found .env configuration
echo.

REM Test Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.13 or later.
    echo.
    pause
    exit /b 1
)

echo Testing Supabase REST API connection...

python -c "import sys; import os; from dotenv import load_dotenv; from supabase import create_client; load_dotenv(); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY')); client.table('instruments').select('id').limit(1).execute(); print('Connected to Supabase via REST API!'); sys.exit(0)" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot connect to Supabase!
    echo Check your .env file ^(SUPABASE_URL, SUPABASE_ANON_KEY^) and internet connection.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Running Daily ETL via REST API...
echo ========================================
echo.

call .venv\Scripts\activate.bat
python update_daily_rest_api.py

echo.
echo ========================================
echo   Daily Update Complete!
echo ========================================
echo.
echo To view your data:
echo   - Open Mobile App: https://portfolio-analyzer-mobile.web.app
echo   - Or run Desktop UI ^(requires port 5432^): START_PORTABLE.bat
echo.
pause
