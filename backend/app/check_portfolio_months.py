"""Check which portfolio months are in database"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            i.name,
            pvd.snapshot_date,
            pvd.value_huf
        FROM portfolio_values_daily pvd
        JOIN instruments i ON pvd.instrument_id = i.id
        WHERE pvd.snapshot_date >= '2024-07-01' AND pvd.snapshot_date <= '2025-11-01'
        ORDER BY i.name, pvd.snapshot_date
    """))
    
    current_instrument = None
    for row in result:
        name, date, value = row
        if name != current_instrument:
            if current_instrument:
                print()
            current_instrument = name
            print(f"{name}:")
        print(f"  {date}: {value:,.0f} HUF")
