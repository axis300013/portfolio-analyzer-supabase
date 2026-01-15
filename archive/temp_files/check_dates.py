"""Check dates in Supabase database"""
from backend.app.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.database_url)
conn = engine.connect()

print("=" * 60)
print("CHECKING DATES IN SUPABASE")
print("=" * 60)

# Check portfolio_values_daily
result = conn.execute(text("""
    SELECT DISTINCT snapshot_date 
    FROM portfolio_values_daily 
    ORDER BY snapshot_date DESC 
    LIMIT 5
"""))
print("\nRecent portfolio_values_daily dates:")
for row in result:
    print(f"  {row[0]}")

# Check prices
result = conn.execute(text("""
    SELECT DISTINCT price_date 
    FROM prices 
    ORDER BY price_date DESC 
    LIMIT 5
"""))
print("\nRecent prices dates:")
for row in result:
    print(f"  {row[0]}")

# Check fx_rates
result = conn.execute(text("""
    SELECT DISTINCT rate_date 
    FROM fx_rates 
    ORDER BY rate_date DESC 
    LIMIT 5
"""))
print("\nRecent fx_rates dates:")
for row in result:
    print(f"  {row[0]}")

# Check if Dec 7 data exists
result = conn.execute(text("""
    SELECT 
        (SELECT COUNT(*) FROM portfolio_values_daily WHERE snapshot_date = '2025-12-07') as portfolio_count,
        (SELECT COUNT(*) FROM prices WHERE price_date = '2025-12-07') as prices_count,
        (SELECT COUNT(*) FROM fx_rates WHERE rate_date = '2025-12-07') as fx_count
"""))
row = result.fetchone()
print("\n" + "=" * 60)
print("DATA FOR DECEMBER 7, 2025:")
print("=" * 60)
print(f"Portfolio values: {row[0]} records")
print(f"Prices: {row[1]} records")
print(f"FX rates: {row[2]} records")

# Check Dec 6 for comparison
result = conn.execute(text("""
    SELECT 
        (SELECT COUNT(*) FROM portfolio_values_daily WHERE snapshot_date = '2025-12-06') as portfolio_count,
        (SELECT COUNT(*) FROM prices WHERE price_date = '2025-12-06') as prices_count,
        (SELECT COUNT(*) FROM fx_rates WHERE rate_date = '2025-12-06') as fx_count
"""))
row = result.fetchone()
print("\nDATA FOR DECEMBER 6, 2025 (for comparison):")
print("=" * 60)
print(f"Portfolio values: {row[0]} records")
print(f"Prices: {row[1]} records")
print(f"FX rates: {row[2]} records")

# Check if Dec 7 values are same as Dec 6
result = conn.execute(text("""
    SELECT 
        d6.instrument_id,
        i.name,
        d6.value_huf as dec_6_value,
        d7.value_huf as dec_7_value,
        d6.price as dec_6_price,
        d7.price as dec_7_price
    FROM portfolio_values_daily d6
    JOIN portfolio_values_daily d7 ON d6.instrument_id = d7.instrument_id
    JOIN instruments i ON d6.instrument_id = i.id
    WHERE d6.snapshot_date = '2025-12-06'
    AND d7.snapshot_date = '2025-12-07'
    ORDER BY i.name
"""))
print("\n" + "=" * 60)
print("COMPARISON: Dec 6 vs Dec 7 VALUES")
print("=" * 60)
rows = result.fetchall()
if rows:
    print(f"{'Instrument':<30} {'Dec 6 Price':<15} {'Dec 7 Price':<15} {'Same?'}")
    print("-" * 80)
    for row in rows:
        same = "✓ SAME" if float(row[4]) == float(row[5]) else "✗ DIFFERENT"
        print(f"{row[1]:<30} {float(row[4]):>12,.4f}   {float(row[5]):>12,.4f}   {same}")
else:
    print("No Dec 7 data found!")

conn.close()
print("\n" + "=" * 60)
