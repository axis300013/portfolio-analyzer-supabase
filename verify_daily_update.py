"""
Test script to verify daily updates are working correctly

Run this after running update_daily.py to confirm:
1. Prices were fetched for today
2. FX rates were fetched for today
3. Portfolio values were calculated for today

Usage:
    python verify_daily_update.py
"""
from datetime import date
from backend.app.db import SessionLocal
from backend.app.models import Price, FxRate, PortfolioValueDaily
from sqlalchemy import func

def verify_daily_update():
    """Verify that today's data is in the database"""
    db = SessionLocal()
    today = date.today()
    
    print("\n" + "="*60)
    print(f"  🔍 VERIFYING DAILY UPDATE FOR {today}")
    print("="*60 + "\n")
    
    try:
        # Check prices
        price_count = db.query(Price).filter(Price.price_date == today).count()
        print(f"1. Prices for today: {price_count} instruments")
        
        if price_count > 0:
            print("   ✅ PASS - Prices were fetched")
            
            # Show sample prices
            sample_prices = db.query(Price).filter(Price.price_date == today).limit(3).all()
            for p in sample_prices:
                print(f"      - {p.instrument.name}: {p.price} {p.currency} ({p.source})")
        else:
            print("   ❌ FAIL - No prices for today! Run update_daily.py")
        
        print()
        
        # Check FX rates
        fx_count = db.query(FxRate).filter(FxRate.rate_date == today).count()
        print(f"2. FX rates for today: {fx_count} currency pairs")
        
        if fx_count >= 4:  # USD, EUR, GBP, CHF minimum
            print("   ✅ PASS - FX rates were fetched")
            
            # Show sample rates
            sample_rates = db.query(FxRate).filter(
                FxRate.rate_date == today,
                FxRate.target_currency == 'HUF'
            ).limit(4).all()
            for r in sample_rates:
                print(f"      - {r.base_currency}/HUF: {r.rate:.2f} ({r.source})")
        else:
            print(f"   ⚠️  WARNING - Only {fx_count} FX rates found. Expected at least 4.")
        
        print()
        
        # Check portfolio values
        value_count = db.query(PortfolioValueDaily).filter(
            PortfolioValueDaily.snapshot_date == today
        ).count()
        print(f"3. Portfolio positions valued: {value_count} holdings")
        
        if value_count > 0:
            print("   ✅ PASS - Portfolio values were calculated")
            
            # Calculate total value
            total_value = db.query(
                func.sum(PortfolioValueDaily.value_huf)
            ).filter(
                PortfolioValueDaily.snapshot_date == today
            ).scalar()
            
            print(f"      - Total Portfolio Value: {total_value:,.2f} HUF")
        else:
            print("   ❌ FAIL - No portfolio values for today! Run update_daily.py")
        
        print("\n" + "="*60)
        
        # Overall assessment
        if price_count > 0 and fx_count >= 4 and value_count > 0:
            print("  ✅ ALL CHECKS PASSED - Data is up to date!")
        else:
            print("  ⚠️  SOME CHECKS FAILED - Run update_daily.py")
        
        print("="*60 + "\n")
        
        # Return status for automation
        return price_count > 0 and fx_count >= 4 and value_count > 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_daily_update()
    exit(0 if success else 1)
