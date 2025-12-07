"""Test if Yahoo Finance API is returning fresh prices"""
import requests
from datetime import date

print("=" * 60)
print(f"TESTING YAHOO FINANCE API - {date.today()}")
print("=" * 60)

# Test OTP stock (Hungarian)
ticker = "OTP.BD"
url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print(f"\nTesting: {ticker}")
print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            
            # Get meta info
            if 'meta' in result:
                meta = result['meta']
                print(f"\nMarket Data:")
                print(f"  Regular Market Price: {meta.get('regularMarketPrice', 'N/A')}")
                print(f"  Previous Close: {meta.get('previousClose', 'N/A')}")
                print(f"  Market Time: {meta.get('regularMarketTime', 'N/A')}")
                print(f"  Currency: {meta.get('currency', 'N/A')}")
                print(f"  Exchange: {meta.get('exchangeName', 'N/A')}")
                print(f"  Trading Period: {meta.get('currentTradingPeriod', 'N/A')}")
                
                # Check if market is open
                market_state = meta.get('marketState', 'UNKNOWN')
                print(f"\n  Market State: {market_state}")
                
                if market_state == 'CLOSED' or market_state == 'PRE':
                    print("  ⚠️  Market is currently CLOSED")
                    print("  → Prices will match last trading day")
                elif market_state == 'REGULAR':
                    print("  ✅ Market is currently OPEN")
                    print("  → Prices are live and updating")
                else:
                    print(f"  ℹ️  Market state: {market_state}")
            
            # Get timestamp info
            if 'timestamp' in result and result['timestamp']:
                from datetime import datetime
                last_timestamp = result['timestamp'][-1] if isinstance(result['timestamp'], list) else result['timestamp']
                last_date = datetime.fromtimestamp(last_timestamp)
                print(f"\n  Last Data Point: {last_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Today: {date.today()}")
                
                if last_date.date() < date.today():
                    print(f"  ⚠️  Last data is from {last_date.strftime('%Y-%m-%d')} (not today)")
                    print("  → This explains why prices match yesterday!")
                else:
                    print("  ✅ Data is from today")
        else:
            print("  ❌ No data in response")
    else:
        print(f"  ❌ Failed: {response.status_code}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("If 'Last Data Point' is from yesterday (Dec 6),")
print("then the API is correctly returning stale prices")
print("because markets are closed today (Saturday).")
print("\nThis is EXPECTED behavior, not a bug!")
print("=" * 60)
