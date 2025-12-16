"""Check portfolio data import"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) as count, 
               MIN(snapshot_date) as min_date, 
               MAX(snapshot_date) as max_date, 
               SUM(value_huf) as total 
        FROM portfolio_values_daily 
        WHERE snapshot_date >= '2024-07-01' AND snapshot_date <= '2025-11-01'
    """))
    
    row = result.fetchone()
    print(f"Portfolio records: {row[0]}")
    print(f"Date range: {row[1]} to {row[2]}")
    print(f"Total value: {row[3]:,}" if row[3] else "Total value: 0")
    
    if row[0] == 0:
        print("\n⚠️  NO PORTFOLIO DATA FOUND IN DATABASE!")
        print("This means 'long' category items were NOT imported.")
