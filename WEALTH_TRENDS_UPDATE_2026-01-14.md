# Wealth Trends Dashboard - Graph Reordering & Auto-Scaling Update
**Date**: 2026-01-14  
**File**: `ui/streamlit_app_wealth.py`

---

## Changes Implemented

### 1. Graph Reordering
The Wealth Trends tab now displays graphs in this order:

**Graph 1: Net Wealth Over Time** (Combined View - shown FIRST)
- Green line chart showing total net wealth progression
- Includes all assets (portfolio + cash + property + pensions) minus liabilities
- Best for seeing overall wealth trend

**Graph 2: Portfolio Value Trend** (shown SECOND)
- Blue line chart showing only investment portfolio value
- Focuses on securities performance only
- Useful for comparing portfolio growth separately from other assets

**Graph 3: Wealth Details - Breakdown by Category** (NEW - shown THIRD)
- Stacked area chart showing detailed breakdown:
  - Portfolio (blue)
  - Cash (green)
  - Property (orange)
  - Pension (purple)
  - Liabilities/Loans shown as dashed red line
- Only displays on days when wealth snapshots are saved
- Provides granular view of wealth composition

**Graph 4: All Wealth Components Over Time** (Stacked View - shown LAST)
- Combined stacked area chart showing Portfolio vs Other Assets
- Shows how total wealth is split between investments and other assets
- Useful for understanding allocation proportions

---

## Auto-Scaling Enhancement

### Problem Solved
Previously, graphs used fixed y-axis ranges. When values were in the 200+ million range with small monthly changes, the visual trend was nearly invisible.

### Solution Implemented
Added `get_y_range()` helper function that:
- Calculates minimum and maximum values in the dataset
- Adds 5% margin above and below for breathing room
- Applies dynamic range to each graph's y-axis
- Formula: `range = [min - (0.05 × range), max + (0.05 × range)]`

### Applied To All Graphs
1. **Net Wealth Chart**: Scales to net wealth min/max
2. **Portfolio Value Chart**: Scales to portfolio min/max
3. **Wealth Details Chart**: Scales to total wealth components min/max
4. **Stacked Components Chart**: Scales to combined portfolio+other assets min/max

---

## Code Changes Summary

### New Helper Function
```python
def get_y_range(values):
    """Calculate y-axis range with 5% margin above and below min/max"""
    min_val = values.min()
    max_val = values.max()
    margin = (max_val - min_val) * 0.05
    return [min_val - margin, max_val + margin]
```

### Y-Axis Configuration
Each graph now uses:
```python
yaxis=dict(range=[calculated_min, calculated_max])
```

Instead of the old auto-scaling that didn't account for data range.

---

## Graph Details

### Graph 1: Net Wealth Over Time
- **Color**: Green (#2E7D32)
- **Type**: Line + Markers with data point labels
- **Labels**: Values shown in M (millions) or K (thousands)
- **Scaling**: Dynamic based on net wealth range
- **Height**: 400px

### Graph 2: Portfolio Value Trend
- **Color**: Blue (#1976D2)
- **Type**: Line + Markers with data point labels
- **Labels**: Values shown in M (millions) or K (thousands)
- **Scaling**: Dynamic based on portfolio value range
- **Height**: 400px

### Graph 3: Wealth Details
- **Type**: Stacked area chart with multiple components
- **Components**:
  - Portfolio: #1976D2 (blue)
  - Cash: #388E3C (green)
  - Property: #F57C00 (orange)
  - Pension: #7B1FA2 (purple)
  - Liabilities: #D32F2F (red dashed line)
- **Scaling**: Dynamic based on total wealth range
- **Display**: Only when snapshot data available
- **Height**: 400px

### Graph 4: Stacked Components
- **Components**:
  - Portfolio: rgba(25, 118, 210, 0.7) (blue)
  - Other Assets: rgba(56, 142, 60, 0.7) (green)
- **Scaling**: Dynamic based on combined total range
- **Height**: 400px

---

## User Experience Improvements

1. **Better Trend Visibility**: Small changes in large values are now visible
2. **Logical Flow**: Primary metric (Net Wealth) shown first
3. **Granular Details**: New breakdown chart shows exact composition
4. **Flexible Aggregation**: Granularity selector (Daily/Monthly/Yearly) applies to all graphs

---

## Testing Recommendations

1. Open Wealth Trends tab in desktop app
2. Verify graphs appear in order: 1, 2, 3, 4
3. Check that graphs scale appropriately to show trends
4. Select Daily/Monthly/Yearly granularity and verify all graphs update
5. Verify wealth detail graph (Graph 3) shows breakdown of: Portfolio, Cash, Property, Pension
6. Verify liabilities show as red dashed line (if applicable)

---

## Backwards Compatibility

- No database changes required
- No API changes required
- Fully compatible with existing data
- Works with all granularity levels (Daily, Monthly, Yearly)

