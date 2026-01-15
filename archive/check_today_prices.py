"""Check if today's prices are in Supabase"""
from datetime import date
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

today = date.today()
print(f"\n📅 Today's date: {today}")
print("="*50)

# Check prices table
print("\n🔍 Checking prices table...")
prices_response = supabase.table('prices')\
    .select('*')\
    .eq('price_date', str(today))\
    .execute()

if prices_response.data:
    print(f"✅ Found {len(prices_response.data)} prices for today ({today})")
    for price in prices_response.data:
        print(f"   - Instrument ID {price['instrument_id']}: {price['price']} {price['currency']} (Source: {price['source']})")
else:
    print(f"❌ No prices found for today ({today})")
    print("\n   Checking most recent prices...")
    latest_response = supabase.table('prices')\
        .select('price_date')\
        .order('price_date', desc=True)\
        .limit(5)\
        .execute()
    
    if latest_response.data:
        print("   Most recent price dates:")
        unique_dates = sorted(set(p['price_date'] for p in latest_response.data), reverse=True)
        for pd in unique_dates[:5]:
            count_response = supabase.table('prices')\
                .select('*', count='exact')\
                .eq('price_date', pd)\
                .execute()
            print(f"   - {pd}: {count_response.count} prices")

# Check portfolio_values_daily table
print("\n🔍 Checking portfolio_values_daily table...")
portfolio_response = supabase.table('portfolio_values_daily')\
    .select('*')\
    .eq('snapshot_date', str(today))\
    .execute()

if portfolio_response.data:
    print(f"✅ Found {len(portfolio_response.data)} portfolio values for today ({today})")
    total_value = sum(float(p['value_huf']) for p in portfolio_response.data)
    print(f"   Total portfolio value: {total_value:,.0f} HUF")
else:
    print(f"❌ No portfolio values found for today ({today})")
    print("\n   Checking most recent portfolio values...")
    latest_pf_response = supabase.table('portfolio_values_daily')\
        .select('snapshot_date')\
        .order('snapshot_date', desc=True)\
        .limit(5)\
        .execute()
    
    if latest_pf_response.data:
        print("   Most recent portfolio dates:")
        unique_dates = sorted(set(p['snapshot_date'] for p in latest_pf_response.data), reverse=True)
        for pd in unique_dates[:5]:
            count_response = supabase.table('portfolio_values_daily')\
                .select('value_huf')\
                .eq('snapshot_date', pd)\
                .execute()
            total = sum(float(p['value_huf']) for p in count_response.data)
            print(f"   - {pd}: {len(count_response.data)} instruments, {total:,.0f} HUF")

print("\n" + "="*50)
