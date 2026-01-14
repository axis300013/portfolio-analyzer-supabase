"""
Copy missing wealth values from January 1 to January 2, 2026
"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import date

load_dotenv()

def copy_missing_values():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    source_date = '2026-01-01'
    target_date = '2026-01-02'
    
    print(f"Copying missing wealth values from {source_date} to {target_date}...")
    print("=" * 80)
    
    # Find categories that have Jan 1 values but not Jan 2
    cursor.execute("""
        SELECT wc.id, wc.name, wc.category_type, wv1.present_value
        FROM wealth_categories wc
        JOIN wealth_values wv1 ON wc.id = wv1.wealth_category_id AND wv1.value_date = %s
        LEFT JOIN wealth_values wv2 ON wc.id = wv2.wealth_category_id AND wv2.value_date = %s
        WHERE wv2.id IS NULL
        ORDER BY wc.category_type, wc.name
    """, (source_date, target_date))
    
    missing = cursor.fetchall()
    
    if not missing:
        print("✅ No missing values - all Jan 1 values already exist on Jan 2")
        conn.close()
        return
    
    print(f"\nFound {len(missing)} categories missing on {target_date}:\n")
    
    copied_count = 0
    for cat_id, cat_name, cat_type, value in missing:
        print(f"  Copying {cat_type}: {cat_name} = {value:,.2f} HUF")
        
        try:
            cursor.execute("""
                INSERT INTO wealth_values (wealth_category_id, value_date, present_value, note)
                VALUES (%s, %s, %s, %s)
            """, (cat_id, target_date, value, f"Copied from {source_date}"))
            
            copied_count += 1
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"✅ Successfully copied {copied_count} out of {len(missing)} values")
    print("=" * 80)

if __name__ == "__main__":
    copy_missing_values()
