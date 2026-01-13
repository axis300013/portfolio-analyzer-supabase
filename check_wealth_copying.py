"""
Check wealth values copied on January 1-2, 2026
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

print("=" * 100)
print("WEALTH VALUES COMPARISON: JANUARY 1 vs JANUARY 2, 2026")
print("=" * 100)

# Get all wealth categories
cursor.execute("""
    SELECT id, name, category_type, is_liability
    FROM wealth_categories
    ORDER BY category_type, name
""")

categories = cursor.fetchall()

print(f"\n{'Category Type':<15} {'Category Name':<40} {'Jan 1':>15} {'Jan 2':>15} {'Status':<20}")
print("-" * 100)

for cat_id, cat_name, cat_type, is_liability in categories:
    # Get value for Jan 1
    cursor.execute("""
        SELECT present_value, note
        FROM wealth_values
        WHERE wealth_category_id = %s AND value_date = '2026-01-01'
    """, (cat_id,))
    jan1 = cursor.fetchone()
    
    # Get value for Jan 2
    cursor.execute("""
        SELECT present_value, note
        FROM wealth_values
        WHERE wealth_category_id = %s AND value_date = '2026-01-02'
    """, (cat_id,))
    jan2 = cursor.fetchone()
    
    jan1_val = f"{jan1[0]:,.0f}" if jan1 else "MISSING"
    jan2_val = f"{jan2[0]:,.0f}" if jan2 else "MISSING"
    
    # Determine status
    if jan1 and jan2:
        if jan2[1] and "Copied from" in jan2[1]:
            status = "✓ Copied"
        elif jan2[1] and "Automatic" in jan2[1]:
            status = "✓ Auto-reduced"
        else:
            status = "Updated"
    elif jan1 and not jan2:
        status = "❌ NOT COPIED!"
    elif not jan1 and jan2:
        status = "New entry"
    else:
        status = "No data"
    
    if jan1 or jan2:
        print(f"{cat_type:<15} {cat_name[:39]:<40} {jan1_val:>15} {jan2_val:>15} {status:<20}")

# Summary
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

cursor.execute("""
    SELECT 
        COUNT(DISTINCT wc.id) as total_categories,
        SUM(CASE WHEN wv1.id IS NOT NULL THEN 1 ELSE 0 END) as jan1_count,
        SUM(CASE WHEN wv2.id IS NOT NULL THEN 1 ELSE 0 END) as jan2_count,
        SUM(CASE WHEN wv1.id IS NOT NULL AND wv2.id IS NULL THEN 1 ELSE 0 END) as missing_jan2
    FROM wealth_categories wc
    LEFT JOIN wealth_values wv1 ON wc.id = wv1.wealth_category_id AND wv1.value_date = '2026-01-01'
    LEFT JOIN wealth_values wv2 ON wc.id = wv2.wealth_category_id AND wv2.value_date = '2026-01-02'
    WHERE wv1.id IS NOT NULL OR wv2.id IS NOT NULL
""")

total, jan1_count, jan2_count, missing = cursor.fetchone()
print(f"Total categories with data: {total}")
print(f"Values on Jan 1: {jan1_count}")
print(f"Values on Jan 2: {jan2_count}")
print(f"❌ Jan 1 values NOT copied to Jan 2: {missing}")

if missing > 0:
    print("\n⚠️ Categories missing on Jan 2:")
    cursor.execute("""
        SELECT wc.name, wc.category_type, wv1.present_value
        FROM wealth_categories wc
        JOIN wealth_values wv1 ON wc.id = wv1.wealth_category_id AND wv1.value_date = '2026-01-01'
        LEFT JOIN wealth_values wv2 ON wc.id = wv2.wealth_category_id AND wv2.value_date = '2026-01-02'
        WHERE wv2.id IS NULL
        ORDER BY wc.category_type, wc.name
    """)
    
    for name, cat_type, value in cursor.fetchall():
        print(f"  - {cat_type}: {name} ({value:,.0f} HUF)")

conn.close()
