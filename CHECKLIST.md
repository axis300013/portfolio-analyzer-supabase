# Portfolio Analyzer - Quick Reference Checklist

## 📋 Setup Checklist

### Prerequisites
- [ ] Python 3.10+ installed
- [ ] Docker Desktop installed and running
- [ ] PowerShell available

### Initial Setup (One-Time)
```powershell
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
```

- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate venv: `venv\Scripts\Activate.ps1`
- [ ] Install packages: `pip install -r requirements.txt`
- [ ] Start database: `docker-compose up -d`
- [ ] Wait 15 seconds: `timeout /t 15`
- [ ] Create schema: `Get-Content sql\create_tables.sql | docker exec -i portfolio_db psql -U portfolio_user -d portfolio_db`
- [ ] Import data: `python -m backend.app.import_initial_data`
- [ ] Run ETL: `python -m backend.app.etl.run_daily_etl`

### Daily Startup
- [ ] Start Docker: `docker-compose up -d`
- [ ] Activate venv: `venv\Scripts\Activate.ps1`
- [ ] **Terminal 1**: Start API: `python -m backend.app.main`
- [ ] **Terminal 2**: Start UI: `streamlit run ui\streamlit_app.py`

### URLs
- [ ] API: http://localhost:8000
- [ ] API Docs: http://localhost:8000/docs
- [ ] UI: http://localhost:8501

---

## 🔧 Common Commands

### ETL Operations
```powershell
# Fetch FX rates
python -m backend.app.etl.fetch_fx_mnb

# Fetch prices (template)
python -m backend.app.etl.fetch_prices

# Calculate portfolio values
python -m backend.app.etl.calculate_values

# Run complete ETL pipeline
python -m backend.app.etl.run_daily_etl

# Or use batch file
.\run_etl.bat
```

### Database Operations
```powershell
# Check Docker containers
docker ps

# View database logs
docker logs portfolio_db

# Connect to database
docker exec -it portfolio_db psql -U portfolio_user -d portfolio_db

# Stop database
docker-compose down

# Restart database
docker-compose restart
```

### Data Management
```powershell
# Import initial data
python -m backend.app.import_initial_data

# Check database connection
python -c "from backend.app.db import engine; print('✓ Connected!' if engine.connect() else '✗ Failed')"
```

---

## 📁 File Structure Reference

```
Portfolio Analyzer/
├── backend/app/
│   ├── etl/
│   │   ├── fetch_fx_mnb.py      # ← Fetch FX rates from MNB
│   │   ├── fetch_prices.py      # ← Price fetcher (customize here)
│   │   ├── calculate_values.py  # ← Calculate portfolio values
│   │   └── run_daily_etl.py     # ← Complete ETL pipeline
│   ├── config.py                 # ← Configuration settings
│   ├── db.py                     # ← Database connection
│   ├── models.py                 # ← Data models
│   ├── crud.py                   # ← Database queries
│   ├── main.py                   # ← API endpoints
│   └── import_initial_data.py    # ← CSV import
├── data/
│   └── initial_holdings.csv      # ← Your holdings (edit here)
├── sql/
│   └── create_tables.sql         # ← Database schema
├── ui/
│   └── streamlit_app.py          # ← UI (customize here)
├── .env                          # ← Environment variables
├── docker-compose.yml            # ← PostgreSQL config
├── requirements.txt              # ← Python packages
└── run_etl.bat                   # ← ETL batch script
```

---

## 🔍 Troubleshooting Quick Fixes

### Python Issues
```powershell
# Module not found
pip install -r requirements.txt

# Wrong Python version
python --version  # Should be 3.10+
```

### Docker Issues
```powershell
# Container not running
docker-compose up -d

# Port conflict
docker-compose down
docker-compose up -d

# Reset database
docker-compose down -v
docker-compose up -d
```

### Port Issues
```powershell
# Check port 8000
netstat -ano | findstr :8000

# Check port 8501
netstat -ano | findstr :8501

# Kill process (replace PID)
taskkill /PID XXXX /F
```

### Data Issues
```powershell
# Re-import data
python -m backend.app.import_initial_data

# Re-run ETL
python -m backend.app.etl.run_daily_etl
```

---

## 📊 Your Portfolio

### Holdings (9 instruments):
1. ✅ AT0000605332 - Erste Bond Dollar Corporate USD
2. ✅ HU0000727268 - ERSTE ESG STOCK COST AVERAGING
3. ✅ HU0000073507 - MAGYAR TELEKOM
4. ✅ HU0000153937 - MOL
5. ✅ HU0000061726 - OTP
6. ✅ HU0000403522 - 2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR
7. ✅ HU0000712211 - MBH AMBÍCIÓ ABSZOLÚT HOZAMÚ
8. ✅ HU0000705058 - MBH INGATLANPIACI ABSZOLÚT HOZAMÚ
9. ✅ HU0000712351 - MBH USA RÉSZVÉNY ALAP

---

## 🎯 Testing Checklist

### After Setup:
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:8501
- [ ] API returns portfolio data
- [ ] UI displays holdings table
- [ ] Summary shows total value
- [ ] No error messages in terminals

### ETL Verification:
- [ ] FX rates fetched from MNB
- [ ] At least EUR, USD rates stored
- [ ] Portfolio values calculated
- [ ] Data visible in API responses

---

## 💡 Next Actions

### Immediate:
- [ ] Test all API endpoints in /docs
- [ ] View portfolio in UI
- [ ] Run ETL manually once

### Short-term:
- [ ] Implement real price fetchers
- [ ] Add more holdings to CSV
- [ ] Schedule ETL with Task Scheduler

### Long-term:
- [ ] Add charts to UI
- [ ] Implement authentication
- [ ] Add historical analysis
- [ ] Deploy to cloud

---

## 📞 Quick Reference URLs

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Streamlit UI | http://localhost:8501 | Portfolio dashboard |
| PostgreSQL | localhost:5432 | Database (internal) |

---

## 🚀 One-Command Quick Start

**After initial setup, start everything with:**

```powershell
# Terminal 1
docker-compose up -d; venv\Scripts\Activate.ps1; python -m backend.app.main

# Terminal 2 (new window)
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"; venv\Scripts\Activate.ps1; streamlit run ui\streamlit_app.py
```

---

## ✅ Success Indicators

You'll know everything is working when:
- ✅ Both terminals show running servers (no errors)
- ✅ http://localhost:8000/docs loads successfully
- ✅ http://localhost:8501 displays the UI
- ✅ Clicking "Load Portfolio" shows your 9 holdings
- ✅ "Get Summary" displays metrics

---

**Last Updated**: December 2, 2025  
**Version**: 1.0
