# Portfolio Analyzer - Quick Reference

## � **Absolute Quickest Method to Start**

```
1. Double-click: start_portfolio_analyzer.ps1
2. Wait: 1 minute
3. Open browser: http://localhost:8501
4. Done!
```

---

## �📋 Recommended Workflow

### ⭐ **Monthly Update (1st of Each Month - 15 minutes)**

1. **Start System** (1 min)
   - Double-click `start_portfolio_analyzer.ps1` (or `.bat`)
   - Wait for 2 PowerShell windows to open

2. **Open UI** (5 sec)
   - Go to http://localhost:8501

3. **Update Prices** (20-30 sec)
   - Click "🔄 Run Daily Update" in sidebar
   - Wait for success message

4. **Update Wealth Values** (10 minutes)
   - Go to Tab 2 (Wealth Management)
   - Update values for:
     - 8 cash accounts
     - 4 properties
     - 2 pension funds
     - 3 loans
   - Click "Save Value" after each

5. **Save Snapshot** (10 sec)
   - Go to Tab 1 (Total Wealth Dashboard)
   - Click "💾 Save This Snapshot"

6. **Review Trends** (3 minutes)
   - Go to Tab 3 (Wealth Trends)
   - Select last 12 months
   - Click "Load Trends"
   - Check YoY % changes

7. **Close** (10 sec)
   - Close both PowerShell windows

### 🔍 **Ad-Hoc Check (Anytime - 2 minutes)**

1. Double-click `start_portfolio_analyzer.ps1`
2. Open http://localhost:8501
3. View Tab 1 for total wealth
4. Optional: Click "Run Daily Update" for fresh prices
5. Close when done

---

## 📋 Startup Files

### Created for You:

| File | Type | How to Use |
|------|------|------------|
| `start_portfolio_analyzer.ps1` | PowerShell | **Double-click** (Recommended) |
| `start_portfolio_analyzer.bat` | Batch | **Double-click** (Alternative) |

### What They Do:

1. ✅ Start Docker Desktop (if not running)
2. ✅ Start PostgreSQL database
3. ✅ Start API server (port 8000)
4. ✅ Start Streamlit UI (port 8501)
5. ✅ Open 2 PowerShell windows (keep them running)

---

### 1️⃣ Update Portfolio Data
```powershell
.\venv\Scripts\Activate.ps1; python update_daily.py
```
**What it does**: Fetches fresh FX rates + instrument prices + calculates portfolio values

---

### 2️⃣ Start Web UI
```powershell
.\venv\Scripts\Activate.ps1; streamlit run ui\streamlit_app_wealth.py
```
**Access at**: http://localhost:8501

---

### 3️⃣ Start API Server (Backend)
```powershell
.\venv\Scripts\Activate.ps1; python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
**API docs at**: http://localhost:8000/docs

---

## 🗂️ UI Tabs Overview

| Tab | Purpose | When to Use |
|-----|---------|-------------|
| 📊 **Total Wealth Dashboard** | See complete net worth | Monthly check-in |
| 💼 **Wealth Management** | Add/update values | Monthly updates |
| 📈 **Wealth Trends** | Historical charts + YoY% | Monthly review |
| 📸 **Portfolio Snapshot** | Securities detail | Deep dive analysis |
| 🔧 **Portfolio Management** | Transactions, manual prices | As needed |

---

## 🔄 UI Sidebar Features

### "🔄 Run Daily Update" Button:
- ✅ Fetches latest FX rates (6 currencies)
- ✅ Fetches latest instrument prices (9-10 instruments)
- ✅ Recalculates portfolio values
- ✅ Shows progress spinner
- ✅ Displays success/error messages
- ✅ Auto-refreshes UI when complete
- ⏱️ Takes 2-3 minutes
- 🔄 Safe to run anytime (idempotent)

---

## 📅 Monthly vs Daily Updates

### ✅ **RECOMMENDED: Monthly Updates**
- Run on 1st of each month
- Takes 15 minutes total
- Captures month-end snapshots for trends
- System fills any gaps automatically

### ⚠️ Daily Updates (Optional)
- Only if you actively trade
- Or need daily performance metrics
- Otherwise monthly is sufficient!

**See**: `MONTHLY_VS_DAILY_GUIDE.md` for full explanation

---

## 🚨 Troubleshooting

### Portfolio showing old data?
1. Open UI at http://localhost:8501
2. Click "🔄 Run Daily Update" in sidebar
3. Wait for completion

### UI won't load?
1. Check if Streamlit is running: look for port 8501
2. Restart: Close terminal → Run streamlit command again

### API not responding?
1. Check if backend is running: look for port 8000
2. Check Docker: `docker ps` (should see portfolio_db)

### Update button not working?
1. Check API server is running at port 8000
2. Check internet connection (for price APIs)
3. View error message in UI for details

---

## 📊 Key Metrics at a Glance

**Current Portfolio (as of 2025-12-03)**:
- Portfolio Value: 79.1M HUF
- Other Assets: 73.6M HUF
- Net Wealth: 152.9M HUF (~$466k USD)

---

## 🔗 Quick Links

- **Web UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Monthly Guide**: `MONTHLY_VS_DAILY_GUIDE.md`
- **Full Documentation**: `2nd instructions.md`

---

**Pro Tip**: The UI button is the easiest way to update! No command line needed. 🖱️
