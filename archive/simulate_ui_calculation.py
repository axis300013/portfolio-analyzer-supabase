"""
Simulate what the UI calculates for missing snapshot dates
"""
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

print("="*70)
print("SIMULATING UI CALCULATION FOR DATES WITHOUT SNAPSHOTS")
print("="*70)

# Get portfolio values for Jan 5, 11, 12
query = """
SELECT 
    snapshot_date,
    SUM(value_huf) as portfolio_value_huf
FROM portfolio_values_daily
WHERE snapshot_date IN ('2026-01-05', '2026-01-11', '2026-01-12')
GROUP BY snapshot_date
ORDER BY snapshot_date
"""
df_portfolio = pd.read_sql(query, engine)

# Get latest wealth values (what the UI would use for Jan 13 or later)
query = """
SELECT 
    wc.name,
    wv.present_value,
    wc.is_liability
FROM wealth_values wv
JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
WHERE wv.value_date = '2026-01-13'
ORDER BY wv.present_value DESC
"""
df_latest_wealth = pd.read_sql(query, engine)

latest_other_assets = df_latest_wealth[~df_latest_wealth['is_liability']]['present_value'].sum()

print(f"\n1. Portfolio values for missing snapshot dates:")
print("-"*70)
print(df_portfolio.to_string(index=False))

print(f"\n2. Latest other_assets (from Jan 13):")
print("-"*70)
print(f"Total other assets: {latest_other_assets:,.0f} HUF")
print("\nBreakdown:")
print(df_latest_wealth[~df_latest_wealth['is_liability']][['name', 'present_value']].to_string(index=False))

print(f"\n3. What the UI would calculate (portfolio + latest_other_assets):")
print("-"*70)
for idx, row in df_portfolio.iterrows():
    date = row['snapshot_date']
    portfolio = row['portfolio_value_huf']
    calculated_net_wealth = portfolio + latest_other_assets
    print(f"{date}: {portfolio:,.0f} (portfolio) + {latest_other_assets:,.0f} (other) = {calculated_net_wealth:,.0f} HUF")
    if calculated_net_wealth > 200_000_000:
        print(f"  ⚠️ OVER 200M!")

print("\n" + "="*70)
