import pandas as pd
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import Instrument, Portfolio, Holding
from datetime import datetime

def import_initial_data(csv_path: str = "data/initial_holdings.csv"):
    db = SessionLocal()
    try:
        # Create default portfolio
        portfolio = Portfolio(name="My Portfolio", owner="Default", currency="HUF")
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            # Create or get instrument
            instrument = db.query(Instrument).filter(Instrument.isin == row['isin']).first()
            if not instrument:
                instrument = Instrument(
                    isin=row['isin'],
                    name=row['name'],
                    currency=row['currency'],
                    instrument_type=row['instrument_type']
                )
                db.add(instrument)
                db.commit()
                db.refresh(instrument)
            
            # Create holding
            holding = Holding(
                portfolio_id=portfolio.id,
                instrument_id=instrument.id,
                quantity=row['quantity']
            )
            db.add(holding)
        
        db.commit()
        print(f"✓ Imported {len(df)} holdings into portfolio '{portfolio.name}'")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error importing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_initial_data()
