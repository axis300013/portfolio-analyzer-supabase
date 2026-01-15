"""
Daily Portfolio Update Script

Run this script once per day to:
1. Fetch latest FX rates from multiple sources (ExchangeRate-API, Frankfurter, MNB)
2. Fetch latest instrument prices (Yahoo Finance, Erste Market, web scraping)
3. Calculate portfolio values with fresh data

Usage:
    python update_daily.py

Or with the virtual environment:
    .\\venv\\Scripts\\Activate.ps1; python update_daily.py
"""
from backend.app.etl.run_daily_etl import run_daily_etl

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  📊 PORTFOLIO ANALYZER - DAILY UPDATE")
    print("="*60)
    print("\nThis script will:")
    print("  1. ✓ Fetch latest FX rates")
    print("  2. ✓ Fetch latest instrument prices") 
    print("  3. ✓ Calculate portfolio values")
    print("\n" + "="*60 + "\n")
    
    try:
        run_daily_etl()
        
        print("\n" + "="*60)
        print("  ✅ DAILY UPDATE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYour portfolio data is now up to date.")
        print("You can view it in the UI at: http://localhost:8501")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("  ❌ ERROR DURING UPDATE")
        print("="*60)
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("  - Docker container is running")
        print("  - Database is accessible")
        print("  - Internet connection is available")
        print("\n")
        raise
