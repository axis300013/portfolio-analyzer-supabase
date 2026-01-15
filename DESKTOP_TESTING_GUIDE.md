# Desktop App Testing Guide - 2025-12-10

## 🎯 **What's New**

### **1. Yearly Granularity**
- Dropdown now has 3 options: Daily, Monthly, **Yearly** (NEW)
- Shows last available month of each year (prefers December)

### **2. Six New YoY Analytics Tables**
All tables show Year-over-Year percentage changes:

**After "Portfolio Summary Over Time":**
1. ✨ **Summary Analytics** - Rolling 12-Month % Change
2. ✨ **Summary Analytics YoY** - Year-over-Year vs Prior December

**After "Portfolio Detail by Instrument":**
3. ✨ **Summary Analytics for Portfolio** - Rolling 12-Month % Change
4. ✨ **Summary Analytics YoY Portfolio** - Year-over-Year by Instrument

**After "Wealth Detail by Category":**
5. ✨ **Summary Analytics for Wealth** - Rolling 12-Month % Change
6. ✨ **Summary Analytics YoY Wealth** - Year-over-Year by Category

### **3. Fixed Price Logic**
- Automatic prices now correctly override old manual prices
- Erste Bond should show "Erste Market" source (not "manual")

---

## 📋 **Testing Checklist**

### **Step 1: Run Daily Update**
1. Open http://localhost:8501
2. Go to **Dashboard** tab
3. Click **"Run Daily Update"** button (top right)
4. Wait for completion (~30 seconds)

### **Step 2: Verify Erste Bond Price**
1. Still on Dashboard tab
2. Scroll to **"Holdings"** table
3. Find **"Erste Bond Dollar Corporate USD R01 VTA"**
4. Check **"Price Source"** column
5. ✅ Should show: **"Erste Market"** (not "manual (admin)")

### **Step 3: Test Analytics Tab - Daily Granularity**
1. Click **"Portfolio & Wealth Analyzer"** tab (left sidebar)
2. Set date range: **2024-01-01** to **2025-12-10**
3. Set Granularity: **Daily**
4. Click **"Load Data"** button

**Verify these tables appear (scroll down):**
- ✅ Portfolio Summary Over Time
- ✅ **Summary Analytics - Rolling 12-Month % Change** (NEW)
- ✅ **Summary Analytics YoY - Year-over-Year vs Prior December** (NEW)
- ✅ Portfolio Detail by Instrument
- ✅ **Summary Analytics for Portfolio - Rolling 12-Month % Change** (NEW)
- ✅ **Summary Analytics YoY Portfolio - Year-over-Year by Instrument** (NEW)
- ✅ Wealth Detail by Category
- ✅ **Summary Analytics for Wealth - Rolling 12-Month % Change** (NEW)
- ✅ **Summary Analytics YoY Wealth - Year-over-Year by Category** (NEW)

### **Step 4: Test Yearly Granularity**
1. Change Granularity to: **Yearly**
2. Click **"Load Data"** again
3. ✅ Verify tables show only yearly data columns (2015, 2016, 2017...2025)
4. ✅ Verify YoY analytics tables update correctly

### **Step 5: Test Monthly Granularity**
1. Change Granularity to: **Monthly**
2. Click **"Load Data"** again
3. ✅ Verify tables show monthly data (more columns than yearly)
4. ✅ Verify YoY analytics tables update correctly

---

## 🔍 **What to Look For**

### **YoY Analytics Tables Format**
- **Metrics in rows** (Portfolio Total, Cash, Property, etc.)
- **Dates/Years in columns**
- **Values show percentages** (e.g., "15.3%", "-2.1%")
- **"N/A"** for insufficient data

### **Expected Behavior**
- Rolling 12M: Compares each date to same month previous year
- YoY Baseline: Compares each year to prior year's December
- Negative percentages for decreases
- Positive percentages for increases

---

## ⚠️ **Known Issues**

1. **First year (2015)**: Will show "N/A" for YoY (no prior year)
2. **Incomplete years**: May show "N/A" if December data missing
3. **Jan-Jun 2024**: Data gap - will show "N/A"

---

## ✅ **Success Criteria**

- [ ] Erste Bond shows "Erste Market" source
- [ ] All 6 new analytics tables display
- [ ] Yearly granularity works
- [ ] YoY percentages calculated correctly
- [ ] No Python errors in console
- [ ] All tables responsive and formatted

---

## 🐛 **If You Find Errors**

1. Check browser console (F12)
2. Check Streamlit terminal for Python errors
3. Note which table/feature caused the error
4. Take screenshot if possible

---

**Test Duration**: ~5-10 minutes  
**Browser**: Chrome/Edge recommended  
**Date**: December 10, 2025
