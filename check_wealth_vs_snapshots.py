"""
Check wealth_values vs snapshots for January 2026
"""
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

print("="*70)
print("WEALTH VALUES vs SNAPSHOTS COMPARISON - JANUARY 2026")
print("="*70)

# Check wealth_values by date
print("\n1. Raw Wealth Values - Daily Totals:")
print("-"*70)
query = """
SELECT 
    wv.value_date,
    SUM(CASE WHEN wc.is_liability THEN 0 ELSE wv.present_value END) as total_assets,
    SUM(CASE WHEN wc.is_liability THEN wv.present_value ELSE 0 END) as total_liabilities,
    COUNT(*) as record_count
FROM wealth_values wv
JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
WHERE wv.value_date >= '2026-01-01' AND wv.value_date < '2026-02-01'
GROUP BY wv.value_date
ORDER BY wv.value_date
"""
df_values = pd.read_sql(query, engine)
print(df_values.to_string(index=False))

# Check which dates have snapshots
print("\n\n2. Dates with Snapshots:")
print("-"*70)
query = """
SELECT 
    snapshot_date,
    other_assets_huf,
    total_liabilities_huf,
    net_wealth_huf
FROM total_wealth_snapshots
WHERE snapshot_date >= '2026-01-01' AND snapshot_date < '2026-02-01'
ORDER BY snapshot_date
"""
df_snapshots = pd.read_sql(query, engine)
print(df_snapshots.to_string(index=False))

# Check for dates with wealth_values but NO snapshots
print("\n\n3. Dates with wealth_values but NO snapshots:")
print("-"*70)
dates_with_values = set(df_values['value_date'].astype(str))
dates_with_snapshots = set(df_snapshots['snapshot_date'].astype(str))
dates_missing_snapshot = dates_with_values - dates_with_snapshots

if dates_missing_snapshot:
    print(f"⚠️ Found {len(dates_missing_snapshot)} dates:")
    for d in sorted(dates_missing_snapshot):
        val = df_values[df_values['value_date'].astype(str) == d].iloc[0]
        print(f"  {d}: {val['total_assets']:,.0f} assets, {val['total_liabilities']:,.0f} liabilities ({val['record_count']} records)")
else:
    print("✓ All dates have snapshots")

print("\n" + "="*70)
