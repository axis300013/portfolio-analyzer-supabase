"""Check Erste Bond instrument and its prices"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

# Load environment
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(bind=engine)

# Import models after engine is created
sys.path.insert(0, os.path.dirname(__file__))
from models import Instrument, Price, ManualPrice

db = SessionLocal()

# Find Erste Bond instrument
instruments = db.query(Instrument).filter(
    or_(
        Instrument.name.like('%Erste%Bond%'),
        Instrument.name.like('%Dollar%Corporate%')
    )
).all()

print("=" * 80)
print("ERSTE BOND INSTRUMENTS:")
print("=" * 80)
for i in instruments:
    print(f"\nID: {i.id}")
    print(f"Name: {i.name}")
    print(f"ISIN: {i.isin}")
    print(f"Type: {i.instrument_type}")
    
    # Check manual prices
    manual_prices = db.query(ManualPrice).filter(
        ManualPrice.instrument_id == i.id
    ).order_by(ManualPrice.override_date.desc()).limit(5).all()
    
    if manual_prices:
        print(f"\n  Manual Prices (last 5):")
        for mp in manual_prices:
            print(f"    {mp.override_date}: {mp.price} {mp.currency} (created_by: {mp.created_by})")
    
    # Check automatic prices
    auto_prices = db.query(Price).filter(
        Price.instrument_id == i.id
    ).order_by(Price.price_date.desc()).limit(5).all()
    
    if auto_prices:
        print(f"\n  Automatic Prices (last 5):")
        for p in auto_prices:
            print(f"    {p.price_date}: {p.price} {p.currency} (source: {p.source})")

db.close()
print("\n" + "=" * 80)
