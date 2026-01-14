"""
Check wealth data for January 2026 to find erroneous values over 200M HUF
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

print("="*70)
print("CHECKING JANUARY 2026 WEALTH DATA")
print("="*70)

# Check total wealth snapshots
print("\n1. Total Wealth Snapshots - January 2026:")
print("-"*70)
query = """
SELECT 
    snapshot_date,
    net_wealth_huf,
    portfolio_value_huf,
    other_assets_huf,
    total_liabilities_huf,
    cash_huf,
    property_huf,
    pension_huf,
    other_huf
FROM total_wealth_snapshots
WHERE snapshot_date >= '2026-01-01' AND snapshot_date < '2026-02-01'
ORDER BY snapshot_date
"""
df_snapshots = pd.read_sql(query, engine)
print(df_snapshots.to_string(index=False))
print(f"\nMax net_wealth_huf: {df_snapshots['net_wealth_huf'].max():,.0f} HUF")
print(f"Average net_wealth_huf: {df_snapshots['net_wealth_huf'].mean():,.0f} HUF")

# Find dates with values over 200M
high_values = df_snapshots[df_snapshots['net_wealth_huf'] > 200000000]
if not high_values.empty:
    print(f"\n⚠️ FOUND {len(high_values)} dates with wealth > 200M HUF:")
    print(high_values.to_string(index=False))

# Check individual wealth values for those dates
print("\n\n2. Detailed Wealth Values for High-Value Dates:")
print("-"*70)
for date in high_values['snapshot_date'].values:
    print(f"\n📅 Date: {date}")
    query = """
    SELECT 
        wc.name as category,
        wv.present_value,
        wv.note,
        wv.created_at
    FROM wealth_values wv
    JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
    WHERE wv.value_date = :date
    ORDER BY wv.present_value DESC
    """
    df_details = pd.read_sql(query, engine, params={'date': str(date)})
    print(df_details.to_string(index=False))
    print(f"   Total from wealth_values: {df_details['present_value'].sum():,.0f} HUF")

# Check for duplicate entries
print("\n\n3. Checking for Duplicate Wealth Entries:")
print("-"*70)
query = """
SELECT 
    wv.value_date,
    wc.name as category,
    COUNT(*) as count,
    STRING_AGG(CAST(wv.present_value AS TEXT), ', ') as values
FROM wealth_values wv
JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
WHERE wv.value_date >= '2026-01-01' AND wv.value_date < '2026-02-01'
GROUP BY wv.value_date, wc.name
HAVING COUNT(*) > 1
ORDER BY wv.value_date, wc.name
"""
df_dupes = pd.read_sql(query, engine)
if not df_dupes.empty:
    print("⚠️ FOUND DUPLICATE ENTRIES:")
    print(df_dupes.to_string(index=False))
else:
    print("✓ No duplicate entries found")

# Check portfolio values for January
print("\n\n4. Portfolio Values - January 2026:")
print("-"*70)
query = """
SELECT 
    p.name as portfolio_name,
    pv.date as value_date,
    pv.total_value_huf,
    pv.total_cost_huf,
    pv.profit_loss_huf
FROM portfolio_values_daily pv
JOIN portfolios p ON pv.portfolio_id = p.id
WHERE pv.date >= '2026-01-01' AND pv.date < '2026-02-01'
ORDER BY pv.date
"""
df_portfolio = pd.read_sql(query, engine)
print(df_portfolio.to_string(index=False))

print("\n" + "="*70)
print("END OF ANALYSIS")
print("="*70)
