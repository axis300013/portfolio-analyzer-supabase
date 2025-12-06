from datetime import date
from .fetch_fx_mnb import run_fx_fetch
from .fetch_prices import run_price_fetch
from .calculate_values import run_calculate_values

def run_daily_etl():
    """Run complete daily ETL pipeline"""
    print(f"\n{'='*50}")
    print(f"Running Daily ETL - {date.today()}")
    print(f"{'='*50}\n")
    
    print("Step 1: Fetching FX rates from MNB...")
    run_fx_fetch()
    
    print("\nStep 2: Fetching instrument prices...")
    run_price_fetch()
    
    print("\nStep 3: Calculating portfolio values...")
    run_calculate_values()
    
    print(f"\n{'='*50}")
    print("ETL Complete!")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    run_daily_etl()
