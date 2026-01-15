"""
Check which categories and items were imported from history.csv
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("WEALTH CATEGORIES FROM HISTORICAL IMPORT")
print("=" * 80)

with engine.connect() as conn:
    # Get unique items imported from history.csv
    result = conn.execute(text("""
        SELECT DISTINCT 
            wc.category_type,
            wc.is_liability,
            wv.item_name,
            COUNT(*) as record_count,
            MIN(wv.present_value) as min_value,
            MAX(wv.present_value) as max_value
        FROM wealth_values wv
        JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
        WHERE wv.note LIKE '%history.csv%'
        GROUP BY wc.category_type, wc.is_liability, wv.item_name
        ORDER BY wc.category_type, wv.item_name
    """))
    
    for row in result:
        cat_type, is_liability, item_name, count, min_val, max_val = row
        print(f"\n{cat_type} ({'LIABILITY' if is_liability else 'ASSET'}): {item_name}")
        print(f"  Records: {count}")
        print(f"  Value range: {min_val:,.2f} to {max_val:,.2f} HUF")

print("\n" + "=" * 80)
print("SUMMARY BY CATEGORY TYPE")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            wc.category_type,
            wc.is_liability,
            COUNT(DISTINCT wv.item_name) as item_count,
            COUNT(*) as record_count,
            SUM(wv.present_value) as total_value
        FROM wealth_values wv
        JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
        WHERE wv.note LIKE '%history.csv%'
        GROUP BY wc.category_type, wc.is_liability
        ORDER BY wc.category_type
    """))
    
    for row in result:
        cat_type, is_liability, item_count, record_count, total_value = row
        print(f"\n{cat_type} ({'LIABILITY' if is_liability else 'ASSET'}):")
        print(f"  Unique items: {item_count}")
        print(f"  Total records: {record_count}")
        print(f"  Total value: {total_value:,.2f} HUF")
