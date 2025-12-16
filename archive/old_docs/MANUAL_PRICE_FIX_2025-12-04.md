# ✅ Manual Price Override Fix - December 4, 2025

## Problem

Manual price overrides were not being used in portfolio calculations. When you set a manual price for "2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR", it wasn't reflected in the dashboard.

## Root Cause

The calculation engine (`calculate_values.py`) was only looking at the `prices` table and ignoring the `manual_prices` table where overrides are stored.

## Solution

Updated the price lookup logic to use a **3-tier priority system**:

### Priority Order (Highest to Lowest):
1. **Manual Price Overrides** ⭐ (from `manual_prices` table)
2. **API Prices** (from `prices` table where source != 'test')
3. **Test Data** (fallback from `prices` table)

## Files Modified

### 1. `backend/app/etl/calculate_values.py`
**Function:** `get_latest_price()`

**Changes:**
- Added import for `ManualPrice` model
- Added manual price override check as first priority
- Restructured logic to check manual prices → API prices → test data

**New Logic:**
```python
def get_latest_price(instrument_id, price_date, db):
    # 1. Check manual override FIRST (highest priority)
    manual_price = query ManualPrice table
    if manual_price exists:
        return manual_price.price
    
    # 2. Check API prices (real data)
    api_price = query Price table (non-test)
    if api_price exists:
        return api_price.price
    
    # 3. Fallback to test data
    test_price = query Price table (any)
    return test_price.price if exists
```

### 2. `backend/app/main.py`
**Endpoint:** `GET /portfolio/{portfolio_id}/snapshot`

**Changes:**
- Updated price source detection to check `ManualPrice` table first
- Shows "manual (username)" as price source when manual override is used
- Falls back to regular price source detection if not manual

**Result:**
Now when you view portfolio details, manual prices show as:
- Price Source: `"manual (admin)"` or `"manual (user)"`

## How It Works Now

### When Portfolio Values Are Calculated:

1. **You set manual override:**
   ```
   Instrument: 2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR
   Date: 2025-12-04
   Price: 10150.00 HUF
   Reason: "Year-end valuation"
   ```

2. **System runs calculation** (via "Run Daily Update" or ETL):
   - Finds your manual override in `manual_prices` table
   - Uses 10150.00 HUF (ignores any API prices)
   - Calculates: quantity × 10150.00 × FX rate
   - Stores result in `portfolio_values_daily` table

3. **Dashboard displays:**
   - Tab 1: Shows updated portfolio value with manual price
   - Tab 4: Shows price source as "manual (admin)"
   - All wealth calculations include the override

## How to Use

### Step 1: Set Manual Override
1. Go to **Tab 5 → Price Overrides** sub-tab
2. Select instrument (e.g., "2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR")
3. Enter override date (e.g., today)
4. Enter price (e.g., 10150.00)
5. Select currency (HUF)
6. Enter reason (e.g., "Bond valuation update")
7. Click "💾 Set Price Override"

### Step 2: Recalculate Portfolio Values
**Option A: Via UI (Recommended)**
- Click **"🔄 Run Daily Update"** button in sidebar
- Wait 30 seconds for completion

**Option B: Via Terminal**
```powershell
.\venv\Scripts\Activate.ps1
python -m backend.app.etl.calculate_values
```

### Step 3: Verify
1. Go to **Tab 1 (Total Wealth Dashboard)**
2. Scroll to "Securities Portfolio Details" section
3. Find your instrument
4. Check:
   - Price shows your manual override value
   - Price Source shows "manual (your-username)"
   - Value calculated with your override

## Testing

### What to Test:
1. **Set a manual override** for any instrument
2. **Run Daily Update** from sidebar
3. **Check Tab 1** - portfolio details show manual price
4. **Check Tab 4** - snapshot shows "manual" as source
5. **Change the override** to a different price
6. **Run Daily Update** again
7. **Verify** new price is used

### Expected Behavior:
✅ Manual price overrides API prices  
✅ Manual price overrides test data  
✅ Price source shows "manual (username)"  
✅ Portfolio value reflects manual price  
✅ Wealth totals include manual price  

## Priority System Summary

| Priority | Source | Table | Use Case |
|----------|--------|-------|----------|
| **1st** | Manual Override | `manual_prices` | User-set prices for bonds, funds, or corrections |
| **2nd** | API Data | `prices` (non-test) | Yahoo Finance, Erste Market scraping |
| **3rd** | Test Data | `prices` (test) | Fallback for development/testing |

## When to Use Manual Overrides

### Good Use Cases:
✅ **Hungarian government bonds** - No API, need manual entry  
✅ **Illiquid funds** - Stale API data, you have better info  
✅ **Correction needed** - API price is wrong  
✅ **Month-end valuations** - Official statements different from API  

### Not Needed:
❌ **Liquid stocks** (MOL, OTP) - API prices are accurate  
❌ **Major ETFs** - API prices update frequently  
❌ **Daily tracking** - Only set for month-end if needed  

## Troubleshooting

### Manual price not showing?
1. **Check override was saved:**
   - Tab 5 → Price Overrides → Click "🔄 Load Overrides"
   - Your override should appear in list

2. **Recalculate portfolio values:**
   - Click "🔄 Run Daily Update" in sidebar
   - Wait for "✅ Daily update completed!"

3. **Check date logic:**
   - Override date must be ≤ portfolio snapshot date
   - If viewing Dec 4, override must be Dec 4 or earlier

4. **Verify instrument:**
   - Make sure you overrode the correct instrument
   - Check ISIN matches

### Price source still shows API?
- This means either:
  - Calculation hasn't run yet (click "Run Daily Update")
  - Override date is in the future
  - Override is for a different instrument

## Next Steps

1. **Restart API server** to load the changes:
   ```powershell
   # Stop current API process
   Get-Process -Name python | Where-Object {$_.Path -like "*Portfolio Analyzer*"} | Stop-Process -Force
   
   # Start fresh
   .\venv\Scripts\Activate.ps1
   python -m backend.app.main
   ```

2. **Test the fix:**
   - Set manual price override for bond
   - Run daily update
   - Check dashboard shows manual price

3. **Use as needed:**
   - Set manual overrides for bonds monthly
   - Let API handle stocks automatically
   - Best of both worlds!

---

**Status:** ✅ Fixed and Ready to Use  
**Impact:** Manual price overrides now work correctly  
**Testing Required:** Yes - restart API, set override, run update, verify  
**Files Changed:** 2 (calculate_values.py, main.py)  
**Lines Added:** ~30 lines  

🎉 **Your bond prices will now calculate correctly with manual overrides!** 🎉
