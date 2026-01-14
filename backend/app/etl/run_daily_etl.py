from datetime import date
from .fetch_fx_mnb import run_fx_fetch
from .fetch_prices import run_price_fetch
from .calculate_values import run_calculate_values
from .fetch_wealth_automated import run_wealth_fetch
from .copy_wealth_values import run_copy_wealth
from ..db import SessionLocal
from .. import wealth_crud

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
    
    print("\nStep 4: Copying static wealth values from previous day...")
    run_copy_wealth()
    
    print("\nStep 5: Fetching automated wealth values...")
    run_wealth_fetch()
    
    print("\nStep 6: Creating total wealth snapshot...")
    try:
        db = SessionLocal()
        today = date.today()
        
        # Calculate total wealth
        wealth_data = wealth_crud.calculate_total_wealth(db, today, portfolio_id=1)
        
        # Save snapshot (will update if exists)
        snapshot = wealth_crud.save_total_wealth_snapshot(
            db=db,
            snapshot_date=today,
            portfolio_value_huf=wealth_data['portfolio_value_huf'],
            other_assets_huf=wealth_data['other_assets_huf'],
            total_liabilities_huf=wealth_data['total_liabilities_huf'],
            cash_huf=wealth_data['breakdown'].get('cash', 0.0),
            property_huf=wealth_data['breakdown'].get('property', 0.0),
            pension_huf=wealth_data['breakdown'].get('pension', 0.0),
            other_huf=wealth_data['breakdown'].get('other', 0.0)
        )
        
        print(f"✅ Snapshot saved: {today} - Net Wealth: {snapshot.net_wealth_huf:,.0f} HUF")
    except Exception as e:
        print(f"❌ Error creating snapshot: {e}")
    finally:
        db.close()
    
    print(f"\n{'='*50}")
    print("ETL Complete!")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    run_daily_etl()
