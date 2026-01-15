#!/usr/bin/env python
"""Check and fix sequence values in Supabase"""
import sys
sys.path.insert(0, 'c:\\Users\\SzalmaNB1\\Downloads\\cabeceo\\visual studio\\Portfolio Analyzer\\backend')

from app.db import engine
from sqlalchemy import text

print("=" * 60)
print("  CHECKING SUPABASE SEQUENCES")
print("=" * 60)

conn = engine.connect()

# Check fx_rates
result = conn.execute(text('SELECT MAX(id) FROM fx_rates'))
max_id = result.fetchone()[0]
result = conn.execute(text('SELECT last_value FROM fx_rates_id_seq'))
seq_val = result.fetchone()[0]

print(f"\nfx_rates:")
print(f"  Max ID: {max_id}")
print(f"  Sequence: {seq_val}")

if seq_val <= max_id:
    print(f"  ⚠️  PROBLEM: Sequence needs to be {max_id + 1}")
    # Fix it
    conn.execute(text(f"SELECT setval('fx_rates_id_seq', {max_id + 1})"))
    conn.commit()
    print(f"  ✅ FIXED: Sequence set to {max_id + 1}")
else:
    print(f"  ✅ OK")

# Check portfolio_values_daily
result = conn.execute(text('SELECT MAX(id) FROM portfolio_values_daily'))
max_id = result.fetchone()[0]
result = conn.execute(text('SELECT last_value FROM portfolio_values_daily_id_seq'))
seq_val = result.fetchone()[0]

print(f"\nportfolio_values_daily:")
print(f"  Max ID: {max_id}")
print(f"  Sequence: {seq_val}")

if seq_val <= max_id:
    print(f"  ⚠️  PROBLEM: Sequence needs to be {max_id + 1}")
    # Fix it
    conn.execute(text(f"SELECT setval('portfolio_values_daily_id_seq', {max_id + 1})"))
    conn.commit()
    print(f"  ✅ FIXED: Sequence set to {max_id + 1}")
else:
    print(f"  ✅ OK")

# Check prices
result = conn.execute(text('SELECT MAX(id) FROM prices'))
max_id = result.fetchone()[0]
result = conn.execute(text('SELECT last_value FROM prices_id_seq'))
seq_val = result.fetchone()[0]

print(f"\nprices:")
print(f"  Max ID: {max_id}")
print(f"  Sequence: {seq_val}")

if seq_val <= max_id:
    print(f"  ⚠️  PROBLEM: Sequence needs to be {max_id + 1}")
    conn.execute(text(f"SELECT setval('prices_id_seq', {max_id + 1})"))
    conn.commit()
    print(f"  ✅ FIXED: Sequence set to {max_id + 1}")
else:
    print(f"  ✅ OK")

# Check wealth_values
result = conn.execute(text('SELECT MAX(id) FROM wealth_values'))
max_id = result.fetchone()[0]
result = conn.execute(text('SELECT last_value FROM wealth_values_id_seq'))
seq_val = result.fetchone()[0]

print(f"\nwealth_values:")
print(f"  Max ID: {max_id}")
print(f"  Sequence: {seq_val}")

if seq_val <= max_id:
    print(f"  ⚠️  PROBLEM: Sequence needs to be {max_id + 1}")
    conn.execute(text(f"SELECT setval('wealth_values_id_seq', {max_id + 1})"))
    conn.commit()
    print(f"  ✅ FIXED: Sequence set to {max_id + 1}")
else:
    print(f"  ✅ OK")

# Check total_wealth_snapshots
result = conn.execute(text('SELECT MAX(id) FROM total_wealth_snapshots'))
max_id = result.fetchone()[0]
result = conn.execute(text('SELECT last_value FROM total_wealth_snapshots_id_seq'))
seq_val = result.fetchone()[0]

print(f"\ntotal_wealth_snapshots:")
print(f"  Max ID: {max_id}")
print(f"  Sequence: {seq_val}")

if seq_val <= max_id:
    print(f"  ⚠️  PROBLEM: Sequence needs to be {max_id + 1}")
    conn.execute(text(f"SELECT setval('total_wealth_snapshots_id_seq', {max_id + 1})"))
    conn.commit()
    print(f"  ✅ FIXED: Sequence set to {max_id + 1}")
else:
    print(f"  ✅ OK")

conn.close()

print("\n" + "=" * 60)
print("  ALL SEQUENCES CHECKED AND FIXED!")
print("=" * 60)
