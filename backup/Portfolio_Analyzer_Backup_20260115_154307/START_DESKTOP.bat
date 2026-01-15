@echo off
REM Portfolio Analyzer - Desktop App Launcher (Supabase REST API)
REM Only starts Streamlit UI - no backend server needed

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Portfolio Analyzer - Desktop App
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your Supabase connection.
    echo.
    pause
    exit /b 1
)

echo Found .env configuration
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate.bat
    echo Then: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Portfolio Analyzer Desktop App...
echo (Uses Supabase REST API - no backend server needed)
echo.
echo The app will open in your browser automatically.
echo Close this window to stop the app.
echo.

REM Start Streamlit (it will open browser automatically)
cd ui
python -m streamlit run streamlit_app_wealth.py --server.port 8501

echo.
echo App stopped.
pause
