"""Check Erste Bond instrument prices via direct SQL"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Find Erste Bond instrument
    result = conn.execute(text("""
        SELECT id, name, isin, instrument_type
        FROM instruments
        WHERE name LIKE '%Erste%Bond%' OR name LIKE '%Dollar%Corporate%'
    """)).fetchall()
    
    print("=" * 80)
    print("ERSTE BOND INSTRUMENTS:")
    print("=" * 80)
    
    for row in result:
        inst_id, name, isin, inst_type = row
        print(f"\nID: {inst_id}")
        print(f"Name: {name}")
        print(f"ISIN: {isin}")
        print(f"Type: {inst_type}")
        
        # Check manual prices
        manual = conn.execute(text("""
            SELECT override_date, price, currency, created_by
            FROM manual_prices
            WHERE instrument_id = :inst_id
            ORDER BY override_date DESC
            LIMIT 5
        """), {"inst_id": inst_id}).fetchall()
        
        if manual:
            print(f"\n  Manual Prices (last 5):")
            for mp in manual:
                print(f"    {mp[0]}: {mp[1]} {mp[2]} (by: {mp[3]})")
        
        # Check automatic prices
        auto = conn.execute(text("""
            SELECT price_date, price, currency, source
            FROM prices
            WHERE instrument_id = :inst_id
            ORDER BY price_date DESC
            LIMIT 5
        """), {"inst_id": inst_id}).fetchall()
        
        if auto:
            print(f"\n  Automatic Prices (last 5):")
            for p in auto:
                print(f"    {p[0]}: {p[1]} {p[2]} (source: {p[3]})")

print("\n" + "=" * 80)
