@echo off
REM Portfolio Analyzer - Portable Launcher for Supabase
REM This batch file can be distributed and runs the application

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Portfolio Analyzer - Supabase
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

echo Testing Supabase connection...

python -c "import os; from dotenv import load_dotenv; from sqlalchemy import create_engine, text; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); conn.execute(text('SELECT 1')); print('Connected to Supabase!')" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot connect to Supabase!
    echo Check your .env file and internet connection.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting FastAPI backend...
start "Portfolio Analyzer - API" /MIN cmd /c "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 >nul

echo Starting Streamlit UI...
start "Portfolio Analyzer - UI" /MIN cmd /c "cd ui && python -m streamlit run streamlit_app_wealth.py --server.port 8501 --server.headless true"

echo.
echo Waiting for services to start...
timeout /t 8 >nul

echo Opening browser...
start http://localhost:8501

echo.
echo ========================================
echo   Portfolio Analyzer is Running!
echo ========================================
echo.
echo   UI:  http://localhost:8501
echo   API: http://localhost:8000/docs
echo   DB:  Supabase Cloud
echo.
echo Close minimized windows to stop services.
echo.
pause
