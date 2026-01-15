# Mobile App Testing Instructions
**Date: 2025-12-11**
**Task 14: Final Mobile App Testing in Chrome**

---

## Prerequisites
✅ Backend running on `http://localhost:8000`
✅ Desktop app tested and working
✅ Mobile app launched in Chrome: `cd mobile; flutter run -d chrome`

---

## Test Plan Overview

### Phase 1: Basic Navigation & Authentication ✓
### Phase 2: Analytics Screen (PRIMARY FOCUS) 🎯
### Phase 3: Trends Screen (Year Labels)
### Phase 4: General Functionality

---

## PHASE 1: Basic Navigation & Authentication

### 1.1 App Launch
- [ ] App opens in Chrome without errors
- [ ] Login screen displays correctly
- [ ] Sign up / Login flow works (if needed)

### 1.2 Bottom Navigation
- [ ] All 5 tabs visible: Dashboard, Portfolio, Wealth, Trends, Analytics
- [ ] Tab switching works smoothly
- [ ] Selected tab highlighted in blue

---

## PHASE 2: Analytics Screen Testing 🎯

### 2.1 Compact UI Controls (Task 12)
**Location:** Top of Analytics screen

**Test: Single-Line Layout**
- [ ] Start Date picker visible (compact format with label "Start")
- [ ] End Date picker visible (compact format with label "End")
- [ ] Granularity dropdown visible (Daily/Monthly)
- [ ] Load Data button (icon-only refresh button)
- [ ] **ALL 4 controls fit in ONE horizontal row**

**Test: Date Pickers**
- [ ] Click Start Date → date picker opens
- [ ] Select date → updates display
- [ ] Click End Date → date picker opens
- [ ] Date format shows as "MM/dd/yyyy"

**Test: Granularity Dropdown**
- [ ] Click dropdown → opens with "Daily" and "Monthly" options
- [ ] Select "Monthly" → updates selection
- [ ] Select "Daily" → updates selection

**Test: Load Data Button**
- [ ] Click refresh icon button
- [ ] Loading spinner appears
- [ ] Data loads successfully

### 2.2 Compact Metric Cards (Task 12)
**Location:** Below controls, above tabs

**Test: Card Layout**
- [ ] 3 metric cards in horizontal row
- [ ] Card 1: "Points" with calendar icon (14px)
- [ ] Card 2: "Items" with briefcase icon (14px)
- [ ] Card 3: "Gran." with grid icon (14px)
- [ ] All cards have small padding (6px)
- [ ] Font sizes: Label 9px, Value 11px

### 2.3 Portfolio Details Tab

**Test: Main Table**
- [ ] Click "Portfolio Details" tab
- [ ] Table header: "Portfolio Detail by Instrument"
- [ ] Columns: Instrument name + multiple date columns
- [ ] Rows: All instruments (NYESZ, TBSZ, Erste Bond, etc.)
- [ ] Values formatted with thousand separators (e.g., "12,345,678")

**Test: Pinch-to-Zoom (Task 11) 🔍**
- [ ] **Pinch gesture**: Zoom in on table → table scales larger
- [ ] **Pinch out**: Zoom out → table scales smaller
- [ ] **Pan gesture**: Drag zoomed table → scrolls smoothly
- [ ] **Double-tap**: Quick zoom toggle (if supported)
- [ ] Table remains readable at all zoom levels

**Test: YoY Rolling Table**
- [ ] Scroll down to "📈 Summary Analytics for Portfolio - Rolling 12-Month % Change"
- [ ] Table shows instruments as rows, dates as columns
- [ ] Values show percentages (e.g., "5.2%", "-3.1%", "N/A")
- [ ] **Pinch-to-zoom works on this table too**

**Test: YoY Baseline Table**
- [ ] Scroll down to "📊 Summary Analytics YoY Portfolio - Year-over-Year by Instrument"
- [ ] Table shows instruments as rows, YEARS as columns (2024, 2025, etc.)
- [ ] Values show percentages vs prior December
- [ ] **Pinch-to-zoom works on this table too**

### 2.4 Wealth Details Tab

**Test: Main Table**
- [ ] Click "Wealth Details" tab
- [ ] Table header: "Wealth Detail by Category"
- [ ] Columns: Category + multiple date columns
- [ ] Rows: All categories (Cash, Property, Pension, Other Assets, Loans)
- [ ] Values formatted correctly
- [ ] **Pinch-to-zoom works**

**Test: YoY Rolling Table**
- [ ] Scroll to "📈 Summary Analytics for Wealth - Rolling 12-Month % Change"
- [ ] Categories as rows, dates as columns
- [ ] Percentage values displayed
- [ ] **Pinch-to-zoom works**

**Test: YoY Baseline Table**
- [ ] Scroll to "📊 Summary Analytics YoY Wealth - Year-over-Year by Category"
- [ ] Categories as rows, years as columns
- [ ] Percentage values displayed
- [ ] **Pinch-to-zoom works**

### 2.5 Combined Summary Tab

**Test: Main Table**
- [ ] Click "Combined Summary" tab
- [ ] Table header: "Portfolio Summary Over Time"
- [ ] Rows: Portfolio Total, Cash, Property, Pension, Other Assets, Loans, Net Wealth
- [ ] Columns: Multiple dates
- [ ] Values formatted correctly
- [ ] **Pinch-to-zoom works**

**Test: YoY Rolling Table**
- [ ] Scroll to "📈 Summary Analytics - Rolling 12-Month % Change"
- [ ] All 7 metrics as rows (Portfolio Total through Net Wealth)
- [ ] Dates as columns
- [ ] Percentage values displayed
- [ ] **Pinch-to-zoom works**

**Test: YoY Baseline Table**
- [ ] Scroll to "📊 Summary Analytics YoY - Year-over-Year vs Prior December"
- [ ] All 7 metrics as rows
- [ ] Years as columns
- [ ] Percentage values displayed
- [ ] **Pinch-to-zoom works**

### 2.6 Data Accuracy Cross-Check
**Compare Mobile vs Desktop**

- [ ] Load same date range in Desktop app (Streamlit)
- [ ] Navigate to "Summary Analytics" in Desktop
- [ ] Compare Portfolio Total values → **Must match**
- [ ] Compare Net Wealth values → **Must match**
- [ ] Compare YoY percentages → **Must match**
- [ ] Any discrepancies? Document below:

---

## PHASE 3: Trends Screen Testing

### 3.1 Portfolio Value Chart (Task 10)
**Location:** Trends tab, top chart

**Test: Year Labels - Vertical Text**
- [ ] Navigate to Trends tab
- [ ] Portfolio Value Trend chart displays
- [ ] X-axis labels show **vertical text** (rotated -90°)
- [ ] **Year change points** show format: "2024\nDec" (year above month)
- [ ] Other months show format: "Jan", "Feb", etc. (month only)
- [ ] Text size: 9px, readable when rotated
- [ ] Text centered below data point

**Test: Year Detection Logic**
- [ ] First data point always shows year+month
- [ ] When year changes (e.g., Dec 2024 → Jan 2025):
  - [ ] January label shows "2025\nJan"
  - [ ] February label shows "Feb" (no year)
- [ ] Within same year: Only month shown

**Test: Long Date Ranges**
- [ ] If date range > 20 points:
  - [ ] Interval spacing increases (not every point labeled)
  - [ ] Year labels still appear at year boundaries

### 3.2 Net Wealth Chart (Task 10)
**Location:** Trends tab, bottom chart

**Test: Year Labels - Same Format**
- [ ] Net Wealth chart displays
- [ ] X-axis labels show **vertical text**
- [ ] Year change points: "2024\nDec"
- [ ] Other months: "Jan", "Feb", etc.
- [ ] Same logic as Portfolio chart above

**Test: Visual Consistency**
- [ ] Both charts have identical label styling
- [ ] Both charts have identical rotation (-90°)
- [ ] Both charts use same font size (9px)

---

## PHASE 4: General Functionality

### 4.1 Dashboard Tab
- [ ] Dashboard loads without errors
- [ ] Today's date picker works
- [ ] Total Net Wealth displays
- [ ] Breakdown cards show correct values

### 4.2 Portfolio Tab
- [ ] Portfolio data loads
- [ ] Instrument list displays
- [ ] Add/Edit/Delete operations work (if applicable)

### 4.3 Wealth Tab
- [ ] Wealth categories load
- [ ] Category values display correctly
- [ ] Add/Edit/Delete operations work (if applicable)

### 4.4 Performance
- [ ] No console errors in browser DevTools (F12)
- [ ] Tables load within 2-3 seconds
- [ ] Zoom interactions are smooth (no lag)
- [ ] Navigation between tabs is instant

---

## PHASE 5: Edge Cases & Error Handling

### 5.1 Empty Data Scenarios
- [ ] Select date range with no data
- [ ] Verify appropriate "No data available" message displays
- [ ] No crash or error screen

### 5.2 Mobile Responsiveness
- [ ] Zoom browser to 75% → UI still usable
- [ ] Zoom browser to 125% → UI still readable
- [ ] Resize browser window → controls reflow appropriately

### 5.3 Granularity Testing
**Test: Monthly Granularity**
- [ ] Set date range: 2024-01-01 to 2025-12-31
- [ ] Select "Monthly" granularity
- [ ] Click "Load Data"
- [ ] Verify: Only end-of-month dates shown in tables
- [ ] Verify: YoY calculations still correct

**Test: Daily Granularity**
- [ ] Set date range: 2025-11-01 to 2025-12-10
- [ ] Select "Daily" granularity
- [ ] Click "Load Data"
- [ ] Verify: All daily dates shown in tables

---

## ISSUES LOG

### Critical Issues 🔴
*(App crashes, data corruption, functionality broken)*

1. **Issue:** 
   - **Steps to reproduce:**
   - **Expected:**
   - **Actual:**
   - **Screenshot/Error:**

### Major Issues 🟡
*(Features not working as intended, poor UX)*

1. **Issue:**
   - **Details:**

### Minor Issues 🟢
*(Cosmetic, small improvements)*

1. **Issue:**
   - **Details:**

---

## FINAL CHECKLIST

### All Tasks Complete?
- [ ] Task 1-8: Desktop features (tested previously ✅)
- [ ] Task 9: Mobile analytics tables (6 YoY tables) ✅
- [ ] Task 10: Year labels on Trends graphs ✅
- [ ] Task 11: Pinch-to-zoom on all 9 tables ✅
- [ ] Task 12: Compact UI controls & metric cards ✅
- [ ] Task 13: Desktop testing ✅
- [ ] Task 14: **Mobile testing (THIS TEST)** 🎯

### Sign-Off
- **Tester Name:** _____________________
- **Date:** 2025-12-11
- **Test Status:** [ ] PASS  [ ] FAIL  [ ] CONDITIONAL PASS
- **Notes:**

---

## ACCEPTANCE CRITERIA

### Must Pass:
✅ All 9 tables support pinch-to-zoom  
✅ UI controls fit in one line (compact layout)  
✅ Year labels display vertically on Trends charts  
✅ All 6 YoY analytics tables display data correctly  
✅ Data matches desktop app values  
✅ No critical browser console errors  

### Success Metrics:
- 0 critical issues (🔴)
- ≤ 2 major issues (🟡)
- Any minor issues (🟢) documented for future improvement

---

## POST-TEST ACTIONS

### If PASS:
1. Update `2nd instructions.md` with "✅ Task 14: Mobile testing complete"
2. Update `todos 1210.md` - mark all tasks complete
3. Commit changes to Git with message: "feat: Mobile analytics UI complete - all tasks done"
4. Celebrate! 🎉

### If FAIL:
1. Document all issues in ISSUES LOG above
2. Prioritize critical (🔴) and major (🟡) issues
3. Create bug fix tasks
4. Retest after fixes

---

**End of Test Instructions**
