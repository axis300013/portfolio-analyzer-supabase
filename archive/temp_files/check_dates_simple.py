"""Check dates in Supabase database - simple version"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = "https://hrlzrirsvifxsnccxvsa.supabase.co"
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

print("=" * 60)
print("CHECKING DATES IN SUPABASE")
print("=" * 60)

# Check portfolio_values_daily
result = supabase.table("portfolio_values_daily")\
    .select("snapshot_date")\
    .order("snapshot_date", desc=True)\
    .limit(10)\
    .execute()

print("\nRecent portfolio_values_daily dates:")
seen_dates = set()
for row in result.data:
    date_val = row['snapshot_date']
    if date_val not in seen_dates:
        print(f"  {date_val}")
        seen_dates.add(date_val)

# Check prices
result = supabase.table("prices")\
    .select("price_date")\
    .order("price_date", desc=True)\
    .limit(10)\
    .execute()

print("\nRecent prices dates:")
seen_dates = set()
for row in result.data:
    date_val = row['price_date']
    if date_val not in seen_dates:
        print(f"  {date_val}")
        seen_dates.add(date_val)

# Check fx_rates
result = supabase.table("fx_rates")\
    .select("rate_date")\
    .order("rate_date", desc=True)\
    .limit(10)\
    .execute()

print("\nRecent fx_rates dates:")
seen_dates = set()
for row in result.data:
    date_val = row['rate_date']
    if date_val not in seen_dates:
        print(f"  {date_val}")
        seen_dates.add(date_val)

# Count Dec 7 data
dec7_portfolio = supabase.table("portfolio_values_daily")\
    .select("*", count="exact")\
    .eq("snapshot_date", "2025-12-07")\
    .execute()

dec7_prices = supabase.table("prices")\
    .select("*", count="exact")\
    .eq("price_date", "2025-12-07")\
    .execute()

dec7_fx = supabase.table("fx_rates")\
    .select("*", count="exact")\
    .eq("rate_date", "2025-12-07")\
    .execute()

print("\n" + "=" * 60)
print("DATA FOR DECEMBER 7, 2025:")
print("=" * 60)
print(f"Portfolio values: {dec7_portfolio.count} records")
print(f"Prices: {dec7_prices.count} records")
print(f"FX rates: {dec7_fx.count} records")

# Count Dec 6 data
dec6_portfolio = supabase.table("portfolio_values_daily")\
    .select("*", count="exact")\
    .eq("snapshot_date", "2025-12-06")\
    .execute()

dec6_prices = supabase.table("prices")\
    .select("*", count="exact")\
    .eq("price_date", "2025-12-06")\
    .execute()

dec6_fx = supabase.table("fx_rates")\
    .select("*", count="exact")\
    .eq("rate_date", "2025-12-06")\
    .execute()

print("\nDATA FOR DECEMBER 6, 2025 (for comparison):")
print("=" * 60)
print(f"Portfolio values: {dec6_portfolio.count} records")
print(f"Prices: {dec6_prices.count} records")
print(f"FX rates: {dec6_fx.count} records")

# Get Dec 7 portfolio values
if dec7_portfolio.count > 0:
    dec7_data = supabase.table("portfolio_values_daily")\
        .select("instrument_id, price, value_huf, instruments(name)")\
        .eq("snapshot_date", "2025-12-07")\
        .execute()
    
    dec6_data = supabase.table("portfolio_values_daily")\
        .select("instrument_id, price, value_huf, instruments(name)")\
        .eq("snapshot_date", "2025-12-06")\
        .execute()
    
    print("\n" + "=" * 60)
    print("COMPARISON: Dec 6 vs Dec 7 PRICES")
    print("=" * 60)
    
    # Create lookup for Dec 6 data
    dec6_lookup = {item['instrument_id']: item for item in dec6_data.data}
    
    print(f"{'Instrument':<30} {'Dec 6 Price':<15} {'Dec 7 Price':<15} {'Status'}")
    print("-" * 80)
    
    for item7 in dec7_data.data:
        inst_id = item7['instrument_id']
        name = item7['instruments']['name']
        price7 = float(item7['price'])
        
        if inst_id in dec6_lookup:
            item6 = dec6_lookup[inst_id]
            price6 = float(item6['price'])
            status = "✓ SAME" if price6 == price7 else f"✗ CHANGED ({price6:.4f} → {price7:.4f})"
            print(f"{name:<30} {price6:>12,.4f}   {price7:>12,.4f}   {status}")
else:
    print("\n⚠️  NO DECEMBER 7 DATA FOUND!")

print("\n" + "=" * 60)
