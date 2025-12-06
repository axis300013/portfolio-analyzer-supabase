"""
Test script to check which instruments can be scraped from Erste Market
"""
from fetch_erste_market import fetch_erste_market_price
import logging

logging.basicConfig(level=logging.INFO)

# All instruments from initial_holdings.csv
instruments = [
    ("AT0000605332", "Erste Bond Dollar Corporate USD R01 VTA", "bond"),
    ("HU0000727268", "ERSTE ESG STOCK COST AVERAGING EUR ALAPOK ALAPJA", "fund"),
    ("HU0000073507", "MAGYAR TELEKOM", "equity"),
    ("HU0000153937", "MOL", "equity"),
    ("HU0000061726", "OTP", "equity"),
    ("HU0000403522", "2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR", "bond"),
    ("HU0000712211", "MBH AMBÍCIÓ ABSZOLÚT HOZAMÚ SZÁRMAZTATOTT ALAP", "fund"),
    ("HU0000705058", "MBH INGATLANPIACI ABSZOLÚT HOZAMÚ SZÁRMAZTATOTT ALAP", "fund"),
    ("HU0000712351", "MBH USA RÉSZVÉNY ALAP HUF SOROZAT", "fund"),
]

print("\n" + "="*80)
print("ERSTE MARKET SCRAPING TEST - ALL INSTRUMENTS")
print("="*80 + "\n")

available_count = 0
unavailable_count = 0

available_list = []
unavailable_list = []

for isin, name, instrument_type in instruments:
    if instrument_type == 'equity':
        print(f"⊘ {name} ({isin})")
        print(f"   Type: {instrument_type.upper()} - Uses Yahoo Finance API (not Erste Market)")
        print()
        continue
        
    print(f"Testing: {name} ({isin})")
    price, currency, date = fetch_erste_market_price(isin)
    
    if price:
        print(f"✓ AVAILABLE on Erste Market")
        print(f"   Price: {price} {currency}")
        print(f"   Date: {date}")
        available_count += 1
        available_list.append((name, isin, price, currency, date))
    else:
        print(f"✗ NOT AVAILABLE on Erste Market")
        unavailable_count += 1
        unavailable_list.append((name, isin))
    print()

print("="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal Non-Equity Instruments: {available_count + unavailable_count}")
print(f"Available on Erste Market: {available_count} ({available_count/(available_count+unavailable_count)*100:.0f}%)")
print(f"Not Available: {unavailable_count} ({unavailable_count/(available_count+unavailable_count)*100:.0f}%)")

if available_list:
    print("\n" + "-"*80)
    print("SUCCESSFULLY SCRAPED:")
    print("-"*80)
    for name, isin, price, currency, date in available_list:
        print(f"  • {name}")
        print(f"    ISIN: {isin}")
        print(f"    Price: {price} {currency} (as of {date})")
        print()

if unavailable_list:
    print("-"*80)
    print("NOT AVAILABLE (Will use carry-forward strategy):")
    print("-"*80)
    for name, isin in unavailable_list:
        print(f"  • {name} ({isin})")
    print()

print("="*80)
print("RECOMMENDATION")
print("="*80)
print("""
For instruments NOT available on Erste Market, you can:
1. Manually update prices in the database
2. Scrape from issuer websites (requires custom scrapers)
3. Use BAMOSZ API (requires paid subscription for Hungarian funds)
4. Use carry-forward strategy (current implementation)
""")
