"""
Check what data is being returned by the portfolio history endpoint
"""
import sys
sys.path.insert(0, '../..')
from backend.app.database import get_db
from backend.app import models
from datetime import date

def check_portfolio_detail():
    db = next(get_db())
    
    # Get recent portfolio values
    portfolio_id = 1
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 10)
    
    print(f"\n{'='*70}")
    print(f"Portfolio History Analysis (Portfolio {portfolio_id})")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"{'='*70}\n")
    
    # Get portfolio values
    portfolio_values = db.query(models.PortfolioValueDaily).filter(
        models.PortfolioValueDaily.portfolio_id == portfolio_id,
        models.PortfolioValueDaily.snapshot_date >= start_date,
        models.PortfolioValueDaily.snapshot_date <= end_date
    ).order_by(models.PortfolioValueDaily.snapshot_date).all()
    
    print(f"Total records found: {len(portfolio_values)}\n")
    
    if portfolio_values:
        # Get unique instruments
        instrument_ids = set(pv.instrument_id for pv in portfolio_values)
        instruments = {}
        
        for inst_id in instrument_ids:
            inst = db.query(models.Instrument).filter(models.Instrument.id == inst_id).first()
            if inst:
                instruments[inst_id] = {
                    'name': inst.name,
                    'type': inst.instrument_type,
                    'isin': inst.isin
                }
        
        print(f"Unique instruments: {len(instruments)}\n")
        print("Instrument Details:")
        print("-" * 70)
        for inst_id, info in instruments.items():
            count = sum(1 for pv in portfolio_values if pv.instrument_id == inst_id)
            print(f"  ID {inst_id}: {info['name']}")
            print(f"           Type: {info['type']}, ISIN: {info['isin']}")
            print(f"           Records: {count}")
            print()
        
        # Check for any NYESZ or TBSZ in the data
        print("\nSearching for NYESZ/TBSZ patterns...")
        print("-" * 70)
        nyesz_tbsz_found = False
        for inst_id, info in instruments.items():
            name_upper = info['name'].upper()
            if 'NYESZ' in name_upper or 'TBSZ' in name_upper:
                print(f"  FOUND: {info['name']}")
                nyesz_tbsz_found = True
        
        if not nyesz_tbsz_found:
            print("  No NYESZ or TBSZ patterns found in instrument names")
        
        # Sample data
        print("\n\nSample Records (first 5):")
        print("-" * 70)
        for pv in portfolio_values[:5]:
            inst = instruments.get(pv.instrument_id)
            if inst:
                print(f"  Date: {pv.snapshot_date}")
                print(f"    Instrument: {inst['name']}")
                print(f"    Type: {inst['type']}")
                print(f"    Quantity: {pv.quantity}, Price: {pv.price}")
                print(f"    Value (HUF): {pv.value_huf:,.0f}")
                print()
    
    db.close()
    print(f"{'='*70}\n")

if __name__ == "__main__":
    check_portfolio_detail()
