import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Check wealth_values with historical data
    result = conn.execute(text("""
        SELECT wc.name, wc.category_type, wv.value_date, wv.present_value 
        FROM wealth_values wv 
        JOIN wealth_categories wc ON wv.wealth_category_id = wc.id 
        WHERE wv.note LIKE '%history.csv%' 
        ORDER BY wv.value_date 
        LIMIT 10
    """)).fetchall()
    
    print("First 10 imported wealth records:")
    print("-" * 80)
    for r in result:
        print(f"{r[0]:30} | {r[1]:10} | {r[2]} | {r[3]:>15,.0f} HUF")
    
    # Check if backend API returns this data
    print("\n" + "=" * 80)
    print("Checking date ranges in wealth_values...")
    result = conn.execute(text("""
        SELECT 
            MIN(value_date) as earliest,
            MAX(value_date) as latest,
            COUNT(*) as total_records
        FROM wealth_values
    """)).fetchone()
    
    print(f"All wealth_values: {result[2]} records from {result[0]} to {result[1]}")
    
    # Check historical vs current
    result = conn.execute(text("""
        SELECT 
            CASE WHEN note LIKE '%history.csv%' THEN 'Historical' ELSE 'Current' END as source,
            COUNT(*) as count,
            MIN(value_date) as min_date,
            MAX(value_date) as max_date
        FROM wealth_values
        GROUP BY CASE WHEN note LIKE '%history.csv%' THEN 'Historical' ELSE 'Current' END
        ORDER BY source
    """)).fetchall()
    
    print("\nBreakdown by source:")
    for r in result:
        print(f"  {r[0]:12}: {r[1]:4} records  ({r[2]} to {r[3]})")
