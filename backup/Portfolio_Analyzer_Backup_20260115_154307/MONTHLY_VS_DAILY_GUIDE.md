# Monthly vs Daily Updates - Usage Guide

## 🎯 Recommended Workflow: **MONTHLY UPDATES**

You asked a great question! You **don't need to run daily updates every day**. Here's the optimal workflow:

---

## 📅 Monthly Routine (Recommended)

### **First of Each Month** (10-15 minutes):

1. **Update Portfolio Data** (via UI button):
   - Open UI at http://localhost:8501
   - Click **"🔄 Run Daily Update"** button in sidebar
   - Wait 2-3 minutes for prices and FX rates to refresh
   - System automatically fills in any missing days with carried-forward prices

2. **Update Wealth Values** (Tab 2: Wealth Management):
   - Update all cash account balances
   - Update property valuations (if changed)
   - Update pension fund values
   - Update loan balances

3. **Save Monthly Snapshot** (Tab 1: Total Wealth Dashboard):
   - Review the complete wealth calculation
   - Click **"💾 Save This Snapshot"**
   - This preserves month-end data for trend analysis

4. **Review Performance** (Tab 3: Wealth Trends):
   - Check Year-over-Year % changes
   - Analyze asset allocation shifts
   - Review monthly progression

---

## 🔍 Ad-Hoc Updates (As Needed)

**Anytime you want to check current portfolio value:**

### Option 1: Via UI (Easiest)
1. Open http://localhost:8501
2. Click **"🔄 Run Daily Update"** in sidebar
3. View refreshed data in dashboard

### Option 2: Via Command Line
```powershell
.\venv\Scripts\Activate.ps1; python update_daily.py
```

---

## 🤔 What Happens if You Skip Days/Weeks?

### **No Problem!** The system handles gaps automatically:

#### Example: You ran update on Dec 1, then next on Dec 31

**When you run update on Dec 31:**
- ✅ Fetches **fresh prices** for Dec 31 from APIs
- ✅ **NO gaps in your data** - Dec 31 will have real prices
- ⚠️ Days 2-30 won't have entries (but that's okay!)

**For viewing historical data:**
- The system uses "last known price" logic
- If you view Dec 15 in the UI, it will show Dec 1 prices
- Your Dec 31 data will be 100% fresh

**For monthly snapshots:**
- Each month-end snapshot has real prices from that day
- Trend analysis works perfectly with monthly data points
- YoY calculations work correctly

---

## 💡 Smart Price Handling

### How "Carried Forward" Prices Work:

**Scenario 1: Market is Open**
```
Run on Dec 31:
  → Fetches fresh prices from Yahoo Finance/Erste Market
  → Stores real prices dated Dec 31
  ✅ Result: Current market prices
```

**Scenario 2: Weekend/Holiday**
```
Run on Sunday Dec 7:
  → APIs return no new data (markets closed)
  → System copies last known price (Dec 6)
  → Tags as "carried forward"
  ✅ Result: Last valid market price
```

**Scenario 3: Skipped Weeks**
```
Last run: Dec 1
Next run: Dec 31
  → Fetches fresh prices for Dec 31
  → Days 2-30 have no entries
  → UI queries will use Dec 1 prices for any date before Dec 31
  ✅ Result: Dec 31 has current prices, older dates use Dec 1
```

---

## 📊 Monthly Workflow Benefits

### ✅ Advantages:
1. **Less Time**: 10-15 min/month vs 2-3 min/day × 30 days
2. **Accurate Month-End**: Always have real prices for month-end snapshots
3. **Clean Data**: One data point per month for trends
4. **No Maintenance**: Don't worry about weekends, holidays, or vacations
5. **Full History**: Saved snapshots preserve complete month-end states

### ⚠️ Trade-offs:
- Intra-month price changes not captured
- If you check UI mid-month, shows last month's prices
- Daily trends not available (but you get monthly trends)

---

## 🔄 When to Use Daily Updates

**Consider daily updates if you:**
- ✅ Actively trade and need daily valuation
- ✅ Want to track daily price movements
- ✅ Need daily performance metrics
- ✅ Have automated trading strategies

**For most wealth tracking purposes, monthly is sufficient!**

---

## 🎯 Your Optimal Setup

Based on your usage: **"Run monthly + ad-hoc for information"**

### 1. **Monthly Scheduled Task** (First of Month):

Create a reminder or calendar event:
```
📅 1st of Every Month, 9:00 AM
Task: Update Portfolio
1. Open http://localhost:8501
2. Click "Run Daily Update" button
3. Update wealth values (cash, property, etc.)
4. Save snapshot
5. Review trends
Duration: 15 minutes
```

### 2. **Ad-Hoc Checks** (Anytime):

**Just want to see current value?**
- Open UI → Click "Run Update" → View dashboard
- Takes 3 minutes total

**Quick command line check?**
```powershell
python update_daily.py
```

---

## 🛡️ Data Integrity Guarantees

### **You're Protected Against:**
1. ❌ **Missing days** → System fills gaps with last known prices
2. ❌ **API failures** → Multi-source fallback (Yahoo → Erste → carried forward)
3. ❌ **Weekends** → Automatically uses Friday's prices
4. ❌ **Stale data** → Update button always fetches fresh data
5. ❌ **Lost snapshots** → Manual saves preserve month-end states

### **What You Get:**
- ✅ Reliable month-end valuations
- ✅ Accurate YoY comparisons
- ✅ Clean monthly trend lines
- ✅ On-demand fresh data anytime

---

## 📱 UI Features Summary

### **Sidebar "Run Daily Update" Button:**
- Triggers full ETL pipeline (FX + Prices + Calculation)
- Shows progress spinner
- Displays success/error messages
- Shows update log in expandable section
- Auto-refreshes UI after completion
- Safe to use anytime - idempotent

### **Tab 1 "Refresh" Button:**
- Reloads current UI data from database
- Doesn't fetch new prices
- Use after running daily update to see fresh data

### **Tab 1 "Save Snapshot" Button:**
- Preserves current wealth state permanently
- Essential for month-end records
- Enables historical trend analysis

---

## 📈 Example Monthly Workflow

### **December 1st - Monthly Update Day:**

```
9:00 AM - Open UI
├─ Click "Run Daily Update" (sidebar)
│  └─ Wait 2-3 minutes
│  └─ ✅ Prices updated for Dec 1
│
├─ Go to Tab 2: Wealth Management
│  ├─ Update MKB account: 850,000 HUF
│  ├─ Update property value: 45,000,000 HUF
│  ├─ Update pension: 3,200,000 HUF
│  └─ Update loans: 25,000,000 HUF
│
├─ Go to Tab 1: Dashboard
│  ├─ Review total wealth: 155M HUF
│  └─ Click "Save This Snapshot"
│
└─ Go to Tab 3: Trends
   ├─ View Nov → Dec change: +2.1M HUF
   └─ Year-over-Year: +8.5%

Total time: 12 minutes
```

### **Mid-Month (Dec 15) - Quick Check:**

```
Option A: View Last Data (instant)
└─ Open UI → See Nov 30 prices (last update)

Option B: Get Fresh Data (3 minutes)
├─ Open UI
├─ Click "Run Daily Update"
└─ View current Dec 15 prices
```

---

## ✅ Bottom Line

### **Your Ideal Setup:**
1. 📅 **Monthly**: Run update first of each month (15 min)
2. 🔍 **Ad-hoc**: Click button in UI whenever curious (3 min)
3. 💾 **Save**: Month-end snapshots for trends
4. 📊 **View**: Check UI anytime - uses last update's data

### **You DON'T Need To:**
- ❌ Run daily updates every day
- ❌ Set up scheduled tasks
- ❌ Worry about missing days
- ❌ Manually fill price gaps

### **The UI Button Does Everything:**
- ✅ One click updates all data
- ✅ Safe to run anytime
- ✅ Shows progress and results
- ✅ Works monthly or more frequently

**Result**: Low maintenance, high accuracy, perfect for monthly wealth tracking! 🎉

---

**Last Updated**: December 3, 2025
