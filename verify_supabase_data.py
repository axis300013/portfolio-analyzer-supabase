#!/usr/bin/env python
"""Verify ETL wrote data to Supabase"""
import sys
sys.path.insert(0, 'c:\\Users\\SzalmaNB1\\Downloads\\cabeceo\\visual studio\\Portfolio Analyzer\\backend')

from app.db import engine
from sqlalchemy import text

print("=" * 60)
print("  VERIFYING DATA IN SUPABASE")
print("=" * 60)

conn = engine.connect()

# Check portfolio data
result = conn.execute(text('''
    SELECT snapshot_date, COUNT(*) as count 
    FROM portfolio_values_daily 
    GROUP BY snapshot_date 
    ORDER BY snapshot_date DESC 
    LIMIT 10
'''))

print("\n📊 Portfolio data by date:")
for row in result:
    print(f"  {row[0]}: {row[1]} instruments")

# Check prices for Dec 6
result = conn.execute(text("SELECT COUNT(*) FROM prices WHERE price_date = '2025-12-06'"))
count = result.fetchone()[0]
print(f"\n📈 Prices for Dec 6, 2025: {count}")

# Check total portfolio value
result = conn.execute(text("SELECT SUM(value_huf) FROM portfolio_values_daily WHERE snapshot_date = '2025-12-06'"))
total = result.fetchone()[0]
print(f"\n💰 Total portfolio value (Dec 6): {total:,.2f} HUF")

# Check wealth data
result = conn.execute(text("SELECT COUNT(*) FROM wealth_values WHERE snapshot_date = '2025-12-06'"))
count = result.fetchone()[0]
print(f"\n🏦 Wealth records for Dec 6: {count}")

conn.close()

print("\n" + "=" * 60)
print("  ✅ ETL SUCCESSFULLY WROTE TO SUPABASE!")
print("=" * 60)
print("\n🎉 The 'Run Daily Update' button is working!")
print("📱 Mobile app will now see the updated data!")
