"""Check history2.csv import results"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Portfolio data before 2024-07-01
    result = conn.execute(text("""
        SELECT MIN(snapshot_date), MAX(snapshot_date), COUNT(*)
        FROM portfolio_values_daily
        WHERE snapshot_date < '2024-07-01'
    """))
    row = result.fetchone()
    print(f"Pre-2024-07 portfolio records: {row[2]}")
    if row[0]:
        print(f"Date range: {row[0]} to {row[1]}")
    
    # Wealth data before 2024-07-01
    result = conn.execute(text("""
        SELECT MIN(value_date), MAX(value_date), COUNT(*)
        FROM wealth_values
        WHERE value_date < '2024-07-01' AND note LIKE '%history2.csv%'
    """))
    row = result.fetchone()
    print(f"\nPre-2024-07 wealth records: {row[2]}")
    if row[0]:
        print(f"Date range: {row[0]} to {row[1]}")
