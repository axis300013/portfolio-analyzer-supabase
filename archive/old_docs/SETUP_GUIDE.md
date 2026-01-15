# Portfolio Analyzer - Setup Guide

## 🚀 Quick Start Guide

This guide will walk you through setting up and running the Portfolio Analyzer application.

---

## Step 1: Install Prerequisites

### Required Software

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation: Open PowerShell and run `python --version`

2. **Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Verify installation: Run `docker --version`

---

## Step 2: Setup Virtual Environment

Open PowerShell and navigate to your project directory:

```powershell
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again
```

You should see `(venv)` at the beginning of your prompt.

---

## Step 3: Install Python Dependencies

```powershell
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- PostgreSQL driver
- Pandas (data processing)
- Streamlit (UI framework)
- And more...

⏱️ **This may take 2-5 minutes**

---

## Step 4: Start PostgreSQL Database

```powershell
# Start Docker container
docker-compose up -d

# Wait 15 seconds for PostgreSQL to initialize
timeout /t 15

# Verify container is running
docker ps
```

You should see `portfolio_db` in the list of running containers.

---

## Step 5: Create Database Schema

```powershell
# Create all tables in PostgreSQL
Get-Content sql\create_tables.sql | docker exec -i portfolio_db psql -U portfolio_user -d portfolio_db
```

This creates 8 tables:
- instruments
- portfolios
- holdings
- prices
- fx_rates
- portfolio_values_daily
- data_sources
- fetch_logs

---

## Step 6: Import Initial Data

```powershell
# Import your 9 holdings from CSV
python -m backend.app.import_initial_data
```

Expected output:
```
✓ Imported 9 holdings into portfolio 'My Portfolio'
```

---

## Step 7: Run Initial ETL

This fetches FX rates from MNB and prepares the data:

```powershell
python -m backend.app.etl.run_daily_etl
```

Expected output:
```
==================================================
Running Daily ETL - 2025-12-02
==================================================

Step 1: Fetching FX rates from MNB...
✓ Stored XX FX rates for 2025-12-02

Step 2: Fetching instrument prices...
✗ Failed to fetch price for [instruments]
(This is expected - price fetching is a template)

Step 3: Calculating portfolio values...
(Will calculate once prices are available)

==================================================
ETL Complete!
==================================================
```

---

## Step 8: Start the API Server

**Keep this terminal window open!**

```powershell
python -m backend.app.main
```

Expected output:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **API is now running!**

Test it by opening: http://localhost:8000/docs

---

## Step 9: Start the Streamlit UI

**Open a NEW PowerShell window** and run:

```powershell
# Navigate to project
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"

# Activate virtual environment
venv\Scripts\Activate.ps1

# Start Streamlit
streamlit run ui\streamlit_app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

✅ **UI is now running!**

Your browser should automatically open to http://localhost:8501

---

## Step 10: Use the Application

### In the Streamlit UI:

1. **Portfolio ID**: Keep as `1` (your default portfolio)
2. **Snapshot Date**: Select today's date
3. Click **"🔄 Load Portfolio"** button
   - You should see your 9 holdings in a table
4. Click **"📈 Get Summary"** button
   - View total portfolio value and instrument count

### In the API Docs (http://localhost:8000/docs):

1. Try the **GET /portfolio/1/snapshot** endpoint
2. Try the **GET /portfolio/1/summary** endpoint

---

## Daily Operations

### Starting the Application

Every time you want to use the app:

```powershell
# 1. Start database (if not running)
docker-compose up -d

# 2. Activate virtual environment
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
venv\Scripts\Activate.ps1

# 3. Start API (Terminal 1)
python -m backend.app.main

# 4. Start UI (Terminal 2 - NEW window)
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
venv\Scripts\Activate.ps1
streamlit run ui\streamlit_app.py
```

### Running Daily ETL

```powershell
# Manually run ETL
python -m backend.app.etl.run_daily_etl

# Or double-click the batch file
run_etl.bat
```

### Stopping the Application

```powershell
# Stop API: Press Ctrl+C in API terminal
# Stop UI: Press Ctrl+C in UI terminal

# Stop database (optional)
docker-compose down
```

---

## Troubleshooting

### ❌ "Python is not recognized"
**Solution**: 
- Reinstall Python and check "Add Python to PATH"
- Or add Python to PATH manually: Search "Environment Variables" in Windows

### ❌ "Docker is not running"
**Solution**: 
- Open Docker Desktop application
- Wait for it to fully start (whale icon in system tray)

### ❌ "Cannot activate virtual environment"
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
**Solution**:
```powershell
# Make sure venv is activated (you see (venv) in prompt)
venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt
```

### ❌ "Connection refused to database"
**Solution**:
```powershell
# Check if container is running
docker ps

# Restart container
docker-compose down
docker-compose up -d

# Wait 15 seconds
timeout /t 15
```

### ❌ "Port 8000 is already in use"
**Solution**:
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill the process (replace XXXX with PID)
taskkill /PID XXXX /F
```

### ❌ "No data in UI / 404 error"
**Solution**:
1. Make sure API is running (http://localhost:8000)
2. Import data: `python -m backend.app.import_initial_data`
3. Run ETL: `python -m backend.app.etl.run_daily_etl`

---

## Verification Checklist

After setup, verify everything works:

- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Docker container running (`docker ps` shows `portfolio_db`)
- [ ] Database tables created (no errors in Step 5)
- [ ] 9 holdings imported (success message in Step 6)
- [ ] FX rates fetched (success message in Step 7)
- [ ] API running on http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Streamlit UI running on http://localhost:8501
- [ ] Can load portfolio in UI
- [ ] Can see portfolio summary in UI

---

## Next Steps

### 1. Implement Price Fetchers

Currently, price fetching is a template. To add real prices:

Edit `backend/app/etl/fetch_prices.py`:
- Add Budapest Stock Exchange API integration
- Add fund price scraping
- Add bond pricing logic

### 2. Add More Holdings

Edit `data/initial_holdings.csv` and add more rows, then:
```powershell
python -m backend.app.import_initial_data
```

### 3. Schedule Daily ETL

**Windows Task Scheduler**:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily at 8 AM
4. Action: Start a program
5. Program: `C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\run_etl.bat`

### 4. Explore the API

Visit http://localhost:8000/docs to see all available endpoints:
- Get portfolio snapshot
- Get portfolio summary
- Filter by date

### 5. Customize the UI

Edit `ui/streamlit_app.py` to add:
- Charts and visualizations
- Historical performance
- Export to Excel
- Dark mode

---

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review error messages carefully
3. Verify all prerequisites are installed
4. Make sure all commands were run in order

---

## Summary of Commands

```powershell
# Setup (one-time)
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker-compose up -d
timeout /t 15
Get-Content sql\create_tables.sql | docker exec -i portfolio_db psql -U portfolio_user -d portfolio_db
python -m backend.app.import_initial_data
python -m backend.app.etl.run_daily_etl

# Daily use
docker-compose up -d
venv\Scripts\Activate.ps1
python -m backend.app.main  # Terminal 1
streamlit run ui\streamlit_app.py  # Terminal 2

# Shutdown
# Ctrl+C in both terminals
docker-compose down
```

---

**🎉 Congratulations! Your Portfolio Analyzer is now set up and running!**

Visit http://localhost:8501 to start tracking your portfolio!
