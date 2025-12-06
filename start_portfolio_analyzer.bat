@echo off
REM Portfolio Analyzer - Automated Startup Script (Batch Version)
REM This script starts all components needed to run the Portfolio Analyzer

color 0B
echo.
echo ========================================
echo   Portfolio Analyzer - Startup Script
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Start Docker Desktop
echo [1/5] Checking Docker Desktop...
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>NUL | find /I /N "Docker Desktop.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo   --^> Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo   --^> Waiting 30 seconds for Docker to start...
    timeout /t 30 /nobreak >nul
) else (
    echo   --^> Docker Desktop is already running
)
echo.

REM Step 2: Start PostgreSQL Database
echo [2/5] Starting PostgreSQL Database...
docker start portfolio_db >nul 2>&1
if errorlevel 1 (
    echo   --^> PostgreSQL may already be running or failed to start
) else (
    echo   --^> PostgreSQL started successfully
    timeout /t 5 /nobreak >nul
)
echo.

REM Step 3: Check ports
echo [3/5] Checking if ports are available...
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   --^> Port 8000 is available
) else (
    echo   --^> Port 8000 already in use ^(API may be running^)
)

netstat -ano | findstr ":8501 " | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   --^> Port 8501 is available
) else (
    echo   --^> Port 8501 already in use ^(UI may be running^)
)
echo.

REM Step 4: Start API Server
echo [4/5] Starting API Server...
start "Portfolio API Server" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && echo ======================================== && echo   Portfolio Analyzer - API Server && echo ======================================== && echo. && echo Starting API server on port 8000... && echo. && python -m backend.app.main"
echo   --^> API Server window opened
echo   --^> Waiting 10 seconds for API to start...
timeout /t 10 /nobreak >nul
echo.

REM Step 5: Start Streamlit UI
echo [5/5] Starting Streamlit UI...
start "Portfolio Streamlit UI" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && echo ======================================== && echo   Portfolio Analyzer - Web UI && echo ======================================== && echo. && echo Starting Streamlit UI on port 8501... && echo. && streamlit run ui\streamlit_app_wealth.py"
echo   --^> Streamlit UI window opened
echo   --^> Waiting for UI to start...
timeout /t 5 /nobreak >nul
echo.

REM Final message
color 0A
echo ========================================
echo   Portfolio Analyzer Started!
echo ========================================
echo.
echo Access URLs:
echo.
echo   Main UI:    http://localhost:8501
echo               ^(Wealth ^& Portfolio Dashboard^)
echo.
echo   API Docs:   http://localhost:8000/docs
echo               ^(Interactive API Documentation^)
echo.
echo   API Server: http://localhost:8000
echo               ^(REST API Endpoints^)
echo.
echo ========================================
echo.
echo Tips:
echo   - Bookmark http://localhost:8501 for quick access!
echo   - Use 'Run Daily Update' button in UI sidebar
echo   - Keep the 2 command windows open while using
echo   - Close the windows when done ^(Ctrl+C or close^)
echo.
echo Monthly Workflow:
echo   1. Click 'Run Daily Update' in sidebar ^(30 sec^)
echo   2. Go to Tab 2, update wealth values ^(10 min^)
echo   3. Go to Tab 1, click 'Save This Snapshot'
echo   4. Go to Tab 3, review trends and YoY %%
echo.
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
