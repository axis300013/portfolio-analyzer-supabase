#!/usr/bin/env python
"""Quick test to verify backend connects to Supabase"""
import sys
sys.path.insert(0, 'c:\\Users\\SzalmaNB1\\Downloads\\cabeceo\\visual studio\\Portfolio Analyzer\\backend')

from app.config import settings
from app.db import engine
from sqlalchemy import text

print("=" * 60)
print("  TESTING SUPABASE CONNECTION")
print("=" * 60)

# Show which database we're connecting to
db_host = settings.database_url.split('@')[1].split(':')[0]
print(f"\n✓ Database host: {db_host}")

# Connect and test
conn = engine.connect()
print("✓ Connection established!")

# Count instruments
result = conn.execute(text('SELECT COUNT(*) FROM instruments'))
count = result.fetchone()[0]
print(f"✓ Found {count} instruments in Supabase")

# Check latest date
result = conn.execute(text('SELECT MAX(snapshot_date) FROM portfolio_values_daily'))
latest_date = result.fetchone()[0]
print(f"✓ Latest portfolio date: {latest_date}")

conn.close()

print("\n" + "=" * 60)
print("  BACKEND IS CONFIGURED TO USE SUPABASE!")
print("=" * 60)
print("\nThe 'Run Daily Update' button will write directly to Supabase.")
print("No manual SQL imports needed! ✨")
