# 🚀 How to Start Portfolio Analyzer Tomorrow

## TL;DR - Quickest Method

1. **Double-click:** `start_portfolio_analyzer.ps1` (or `.bat`)
2. **Wait:** 1 minute
3. **Open browser:** http://localhost:8501
4. **Done!** ✅

---

## Complete Step-by-Step Instructions

### Prerequisites (Already Installed ✅)

- Docker Desktop
- Python 3.13.9
- Virtual environment (`venv` folder)
- All dependencies installed
- Database configured

---

## Method 1: Automated Startup (Recommended) ⭐

### Step 1: Locate the Project Folder

Open File Explorer and navigate to:
```
C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer
```

### Step 2: Run the Startup Script

**Option A - PowerShell Script (Recommended):**
- Find file: `start_portfolio_analyzer.ps1`
- **Double-click** the file
- If Windows asks, click "Run" or "More info → Run anyway"

**Option B - Batch Script (Alternative):**
- Find file: `start_portfolio_analyzer.bat`
- **Double-click** the file

### Step 3: Watch the Startup Process

You'll see:
1. **Startup window** shows progress (5 steps)
2. **API Server window** opens (shows "Uvicorn running on http://0.0.0.0:8000")
3. **Streamlit UI window** opens (shows "You can now view your Streamlit app")

**Total wait time: ~1 minute**

### Step 4: Open the UI in Your Browser

The script will tell you to go to: **http://localhost:8501**

**Or just open your browser and type:** `localhost:8501`

### Step 5: Start Using!

You should see the **Portfolio & Wealth Analyzer** dashboard with 5 tabs.

---

## Method 2: Manual Startup (If Scripts Don't Work)

### Step 1: Start Docker Desktop

1. Click Windows Start button
2. Type "Docker Desktop"
3. Click to open
4. Wait for Docker icon in system tray to show "Running"
5. Wait 30 seconds

### Step 2: Start Database

Open PowerShell in project folder:

```powershell
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
docker start portfolio_db
```

Wait 5 seconds.

### Step 3: Start API Server

Open a **NEW PowerShell window**:

```powershell
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
.\venv\Scripts\Activate.ps1
python -m backend.app.main
```

**Keep this window open!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Start Streamlit UI

Open **ANOTHER NEW PowerShell window**:

```powershell
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
.\venv\Scripts\Activate.ps1
streamlit run ui\streamlit_app_wealth.py
```

**Keep this window open too!** You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 5: Open Browser

Go to: http://localhost:8501

---

## What You'll See in the UI

### Five Main Tabs:

#### 📊 Tab 1: Total Wealth Dashboard
- Complete wealth overview
- Portfolio value + Other assets - Liabilities
- Asset allocation pie chart
- Breakdown tables
- **"💾 Save This Snapshot" button** ← Click monthly!

#### 💼 Tab 2: Wealth Management
- Update values for 17 wealth items:
  - 8 Cash accounts
  - 4 Properties
  - 2 Pension funds
  - 3 Loans
- Add new wealth categories
- View current values by date

#### 📈 Tab 3: Wealth Trends
- Historical wealth charts
- Year-over-Year % changes
- Period comparisons
- Monthly progression

#### 📸 Tab 4: Portfolio Snapshot
- Security-by-security breakdown
- Individual instrument values
- Price sources

#### 🔧 Tab 5: Portfolio Management
- Add transactions (Buy/Sell/Adjust)
- Manual price overrides
- Add new instruments

### ⚡ Sidebar Features:

**🔄 Run Daily Update Button:**
- Click to fetch latest prices + FX rates
- Takes 20-30 seconds
- Use monthly (1st of each month)
- Safe to use anytime

---

## Monthly Workflow (1st of Each Month)

### Total Time: 15 minutes

#### 1. Start the System (1 minute)
```
Double-click: start_portfolio_analyzer.ps1
Wait for 2 windows to open
```

#### 2. Update Prices (30 seconds)
```
Open: http://localhost:8501
Click: "🔄 Run Daily Update" in sidebar
Wait: Success message appears
```

#### 3. Update Wealth Values (10 minutes)
```
Go to: Tab 2 (Wealth Management)

Update each category:
- Cash accounts (MKB, K&H, Wise, Revolut, etc.)
- Property values (Peterdy 29, Peterdy 25, etc.)
- Pension funds (Self Fund, Voluntary Fund)
- Loan balances

Click: "Save Value" after each entry
```

#### 4. Save Monthly Snapshot (10 seconds)
```
Go to: Tab 1 (Total Wealth Dashboard)
Review: Total wealth calculation
Click: "💾 Save This Snapshot"
```

#### 5. Review Performance (3 minutes)
```
Go to: Tab 3 (Wealth Trends)
Select: Date range (last 12 months)
Click: "Load Trends"
Review: YoY % change, monthly progression
```

#### 6. Close When Done (10 seconds)
```
Close: Both PowerShell windows (or press Ctrl+C in each)
Optional: Stop database (docker stop portfolio_db)
```

---

## Ad-Hoc Usage (Just Checking Portfolio)

### Total Time: 2-3 minutes

```
1. Double-click: start_portfolio_analyzer.ps1
2. Open browser: http://localhost:8501
3. View Tab 1: See current total wealth
4. Optional: Click "Run Daily Update" for fresh prices
5. Close windows when done
```

---

## How to Shut Down

### Quick Method:
1. **Close the 2 PowerShell windows** (API Server + Streamlit UI)
   - Just click the X
   - Or press Ctrl+C in each window

### Complete Shutdown:
```powershell
# Stop the database (optional - it can stay running)
docker stop portfolio_db

# Close Docker Desktop (optional)
Right-click Docker icon in system tray → Quit Docker Desktop
```

### Important Notes:
- ✅ **Your data is safe!** All data stored in Docker volumes
- ✅ **Data persists** when you close everything
- ✅ **Next startup** will show all your data
- ✅ **No data loss** from shutting down

---

## Troubleshooting Common Issues

### Issue: "Windows protected your PC" message

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. Or: Right-click script → "Run with PowerShell"

### Issue: "Docker is not running"

**Solution:**
```
1. Start → Type "Docker Desktop"
2. Click to open
3. Wait for "Docker Desktop is running" in system tray
4. Wait 30 seconds
5. Run startup script again
```

### Issue: "Port 8000 already in use"

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Run startup script again
```

### Issue: "Port 8501 already in use"

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8501

# Kill the process
taskkill /PID <PID> /F

# Run startup script again
```

### Issue: Browser shows "This site can't be reached"

**Solution:**
1. Wait 30 more seconds (services may still be starting)
2. Check PowerShell windows for errors
3. Look for:
   - API: "Application startup complete"
   - UI: "You can now view your Streamlit app"
4. Refresh browser (F5)

### Issue: "Module not found" errors

**Solution:**
```powershell
# Navigate to project folder
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Can't connect to database

**Solution:**
```powershell
# Check if database is running
docker ps

# If not listed, try starting it
docker start portfolio_db

# If still fails, check Docker Desktop is running
```

### Issue: Old data showing in UI

**Solution:**
1. Click "🔄 Run Daily Update" in sidebar
2. Wait for success message
3. Refresh browser page (F5)

### Issue: Startup script does nothing

**Solution:**
1. Try the .bat file instead of .ps1
2. Or use manual startup method (Method 2)
3. Check if Python/Docker are installed correctly

---

## URLs Reference

### Main URLs (Bookmark These!)

| URL | Purpose |
|-----|---------|
| **http://localhost:8501** | Main UI - Wealth & Portfolio Dashboard |
| **http://localhost:8000/docs** | Interactive API Documentation |
| **http://localhost:8000** | API Server Base URL |

### Access After Startup:

Once you see both PowerShell windows showing "running" or "complete":
- Open browser
- Go to http://localhost:8501
- Bookmark this page!

---

## Files Reference

### Startup Files (in project folder)

| File | Purpose | How to Use |
|------|---------|------------|
| `start_portfolio_analyzer.ps1` | PowerShell startup script | Double-click |
| `start_portfolio_analyzer.bat` | Batch startup script | Double-click |
| `HOW_TO_START_TOMORROW.md` | This guide | Read for instructions |

### Documentation Files

| File | Content |
|------|---------|
| `2nd instructions.md` | Complete system documentation |
| `STARTUP_GUIDE.md` | Detailed startup procedures |
| `QUICK_REFERENCE.md` | Command cheat sheet |
| `MONTHLY_VS_DAILY_GUIDE.md` | Monthly workflow best practices |
| `COMPLETE_VERIFICATION.md` | ETL dependency verification |

---

## What Happens When You Skip Days/Weeks?

### No Problem! The system handles gaps automatically:

**Example Scenario:**
```
Dec 1:  Run update → ✅ Fresh prices stored
Dec 2-30: (you don't run anything - skip 29 days)
Dec 31: Run update → ✅ Fresh prices fetched from APIs
```

**What happens:**
- ✅ Dec 31 data is 100% fresh from live APIs
- ✅ Dec 1 data was fresh when you ran it
- ⚠️ Days 2-30 have no database entries
- ✅ If you view Dec 15 in UI, it shows Dec 1 prices
- ✅ Your month-end snapshots are always accurate

**This is PERFECT for monthly wealth tracking!**

---

## Why Monthly Updates Are Sufficient

### For Wealth Tracking (Not Day Trading):

✅ **Advantages:**
- Track net worth trends month-over-month
- See Year-over-Year % changes
- Understand asset allocation shifts
- Less time commitment (15 min/month vs 90 min/month)
- Clean data points for trend analysis
- No daily market noise

✅ **What You Get:**
- Accurate month-end valuations
- Historical snapshots preserved
- Trend analysis with YoY %
- Complete wealth picture monthly

⚠️ **What You Don't Get:**
- Daily price movements
- Intra-month fluctuations
- Day-to-day volatility tracking

**For most people tracking wealth (not actively trading), monthly is ideal!**

---

## Quick Command Reference

### If Scripts Don't Work:

```powershell
# Navigate to project
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"

# Start database
docker start portfolio_db

# Terminal 1 - API Server
.\venv\Scripts\Activate.ps1
python -m backend.app.main

# Terminal 2 - UI (open new window)
.\venv\Scripts\Activate.ps1
streamlit run ui\streamlit_app_wealth.py
```

### Check Status:

```powershell
# Check if Docker is running
docker ps

# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Check Docker Desktop
tasklist | findstr "Docker Desktop"
```

---

## First Time Tomorrow Checklist

Before you close tonight:

- [ ] Know where project folder is located
- [ ] Bookmark http://localhost:8501
- [ ] Understand monthly workflow (not daily)
- [ ] Know which script to double-click
- [ ] Have this guide available
- [ ] Tested startup script at least once

**You're ready for tomorrow!** ✅

---

## Summary

### To Start Tomorrow Morning:

```
1. Double-click: start_portfolio_analyzer.ps1
2. Wait: 1 minute (2 windows will open)
3. Open browser: http://localhost:8501
4. Done! Start using the dashboard
```

### Monthly Routine (1st of Month):

```
1. Start system (1 min)
2. Click "Run Daily Update" (30 sec)
3. Update wealth values in Tab 2 (10 min)
4. Save snapshot in Tab 1 (10 sec)
5. Review trends in Tab 3 (3 min)
6. Close windows when done
```

### When You're Finished:

```
1. Close both PowerShell windows
2. Optional: Stop database (docker stop portfolio_db)
3. Your data is safe - stored in Docker volumes
```

---

**You now have everything you need to use the Portfolio Analyzer independently!** 🎉

**Questions?** Refer to:
- `2nd instructions.md` for complete documentation
- `TROUBLESHOOTING.md` for common issues
- `QUICK_REFERENCE.md` for command cheat sheet

**Good luck with your wealth tracking!** 💰📊
