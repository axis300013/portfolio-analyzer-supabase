# Daily Portfolio Update Guide

## 🔄 Automatic Daily Updates

To keep your portfolio data fresh with the latest prices and FX rates, run this script **once per day** (preferably in the morning):

```powershell
.\venv\Scripts\Activate.ps1; python update_daily.py
```

### What This Does:

1. **📈 Fetches Latest FX Rates**
   - Sources: ExchangeRate-API (primary), Frankfurter API (backup), MNB (fallback)
   - Currencies: USD, EUR, GBP, CHF → HUF
   - Smart fallback system ensures you always have rates

2. **💰 Fetches Latest Instrument Prices**
   - **Equities**: Yahoo Finance API (Hungarian stocks: MOL, OTP, MTEL)
   - **Funds**: Erste Market web scraping + manual prices
   - **Bonds**: Erste Market + fixed par values for government bonds
   - **Fallback**: If unable to fetch new price, carries forward last known price

3. **🧮 Calculates Portfolio Values**
   - Updates `portfolio_values_daily` table with fresh valuations
   - Combines: Holdings × Prices × FX Rates = Value in HUF

### Success Criteria:

✅ **Expected Output:**
```
Step 1: Fetching FX rates from MNB...
✓ Stored 6 FX rates for 2025-12-03

Step 2: Fetching instrument prices...
✓ Fetched new price for [instrument names]
Summary: 9 fetched, 0 carried forward, 0 already exist, 1 failed
Total: 9/10 instruments have prices

Step 3: Calculating portfolio values...
✓ Calculated values for 9 holdings

✅ DAILY UPDATE COMPLETED SUCCESSFULLY!
```

### Troubleshooting:

❌ **"No price available"** 
- Common for illiquid instruments or outside market hours
- System automatically uses last known price
- For manual instruments, add price via UI: Management tab → Manual Prices

❌ **"Connection error"**
- Check internet connection
- APIs may be temporarily down → try again in 5 minutes
- System will use carried-forward prices automatically

❌ **"Database connection failed"**
- Ensure Docker container is running: `docker ps`
- Restart if needed: `docker restart portfolio_db`

## 📅 Recommended Schedule

### Daily Routine:
1. **Morning** (before market close): Run `update_daily.py`
2. **Check UI**: Open http://localhost:8501 to view fresh data
3. **Add Manual Values**: If any wealth items need updating (cash, properties)

### Weekly Maintenance:
- Review manual prices for any overrides needed
- Check fetch_logs for any persistent errors
- Verify FX rates are updating correctly

### Monthly Routine:
1. **Add Wealth Values** (Tab 2 in UI):
   - Update all cash account balances
   - Update property valuations
   - Update pension fund values
   - Add/update loan amounts
2. **Save Snapshot** (Tab 1 in UI):
   - Click "💾 Save This Snapshot" to preserve month-end data
3. **Review Trends** (Tab 3 in UI):
   - Check Year-over-Year changes
   - Analyze asset allocation shifts

## 🤖 Automation Options

### Windows Task Scheduler:
Create a scheduled task to run daily at 9 AM:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-File C:\path\to\Portfolio Analyzer\run_daily_update.bat"

$trigger = New-ScheduledTaskTrigger -Daily -At 9am

Register-ScheduledTask -TaskName "Portfolio Daily Update" `
    -Action $action -Trigger $trigger
```

### Batch File (`run_daily_update.bat`):
```batch
@echo off
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
call venv\Scripts\activate.bat
python update_daily.py
pause
```

### Python Scheduler (Alternative):
```python
# schedule_updates.py
import schedule
import time
from backend.app.etl.run_daily_etl import run_daily_etl

def job():
    print("Running daily portfolio update...")
    run_daily_etl()

# Run every day at 9:00 AM
schedule.every().day.at("09:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📊 Data Sources

| Asset Type | Primary Source | Backup Source | Update Frequency |
|------------|---------------|---------------|------------------|
| Hungarian Stocks | Yahoo Finance API | Manual prices | Real-time |
| Mutual Funds | Erste Market scraping | Last known price | Daily after close |
| Bonds | Erste Market / Fixed | Last known price | Daily |
| FX Rates | ExchangeRate-API | Frankfurter API, MNB | Daily |
| Cash/Property | Manual entry | N/A | Monthly |

## 🎯 Best Practices

1. ✅ **Run daily updates in the morning** before reviewing portfolio
2. ✅ **Keep Docker running** for database access
3. ✅ **Monitor logs** for any persistent fetch failures
4. ✅ **Update wealth values monthly** on the same day each month
5. ✅ **Save snapshots regularly** to preserve historical data for trends
6. ✅ **Check API health** if multiple days of carried-forward prices occur

## 📞 Support

If prices aren't updating:
1. Check if instrument is listed on supported exchanges
2. Verify ISIN code is correct in database
3. Add manual price override if needed via UI
4. Check `fetch_logs` table for error details

---

**Last Updated**: December 3, 2025
