"""
Find missing pension fund data in January 2026
"""
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

print("="*70)
print("CHECKING PENSION FUND DATA - JANUARY 2026")
print("="*70)

# Get all pension categories
query = """
SELECT id, name, category_type
FROM wealth_categories
WHERE category_type = 'pension'
ORDER BY name
"""
df_pension_cats = pd.read_sql(query, engine)
print("\nPension fund categories:")
print(df_pension_cats.to_string(index=False))

# Check pension values for each day in January
query = """
SELECT 
    wv.value_date,
    wc.name as category_name,
    wv.present_value
FROM wealth_values wv
JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
WHERE wc.category_type = 'pension'
    AND wv.value_date >= '2026-01-01' 
    AND wv.value_date < '2026-02-01'
ORDER BY wv.value_date, wc.name
"""
df_pension_values = pd.read_sql(query, engine)

# Pivot to see which funds have values on which dates
pivot = df_pension_values.pivot(index='value_date', columns='category_name', values='present_value')
print("\n\nPension fund values by date:")
print(pivot.to_string())

# Find dates with missing values
print("\n\n" + "="*70)
print("MISSING VALUES ANALYSIS")
print("="*70)

for pension_name in pivot.columns:
    missing_dates = pivot[pivot[pension_name].isna()].index.tolist()
    if missing_dates:
        print(f"\n⚠️  {pension_name} is MISSING on:")
        for date in missing_dates:
            print(f"    - {date}")
        
        # Find last available value before the gap
        available_dates = pivot[pivot[pension_name].notna()].index.tolist()
        if available_dates:
            last_date = max([d for d in available_dates if d < min(missing_dates)])
            last_value = pivot.loc[last_date, pension_name]
            print(f"    Last known value: {last_value:,.0f} HUF (from {last_date})")

# Check daily totals
print("\n\n" + "="*70)
print("DAILY PENSION TOTALS")
print("="*70)
daily_totals = df_pension_values.groupby('value_date')['present_value'].sum()
print(daily_totals.to_string())

print("\n" + "="*70)
