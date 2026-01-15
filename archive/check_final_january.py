from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

query = """
SELECT 
    snapshot_date, 
    net_wealth_huf, 
    pension_huf,
    portfolio_value_huf
FROM total_wealth_snapshots 
WHERE snapshot_date >= '2026-01-01' 
    AND snapshot_date < '2026-02-01' 
ORDER BY snapshot_date
"""

df = pd.read_sql(query, engine)
print("="*70)
print("FINAL JANUARY 2026 SNAPSHOTS")
print("="*70)
print(df.to_string(index=False))
print()
print(f"Min net_wealth: {df['net_wealth_huf'].min():,.0f} HUF")
print(f"Max net_wealth: {df['net_wealth_huf'].max():,.0f} HUF")
print(f"Average: {df['net_wealth_huf'].mean():,.0f} HUF")
print("="*70)
