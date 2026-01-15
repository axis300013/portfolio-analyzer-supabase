"""Check today's wealth data vs yesterday"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import date, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

today = date.today()
yesterday = today - timedelta(days=1)

print(f"\n{'='*80}")
print(f"WEALTH VALUES COMPARISON: {yesterday} vs {today}")
print(f"{'='*80}\n")

# Get all categories
cursor.execute("""
    SELECT wc.id, wc.name, wc.category_type, wc.is_liability
    FROM wealth_categories wc
    ORDER BY wc.category_type, wc.name
""")

categories = cursor.fetchall()

print(f"{'Category':<40} {'Type':<15} {'Yesterday':>15} {'Today':>15} {'Status'}")
print("-" * 110)

missing_today = []
found_today = []

for cat_id, cat_name, cat_type, is_liability in categories:
    # Get yesterday's value
    cursor.execute("""
        SELECT present_value
        FROM wealth_values
        WHERE wealth_category_id = %s AND value_date = %s
    """, (cat_id, yesterday))
    yesterday_row = cursor.fetchone()
    
    # Get today's value
    cursor.execute("""
        SELECT present_value
        FROM wealth_values
        WHERE wealth_category_id = %s AND value_date = %s
    """, (cat_id, today))
    today_row = cursor.fetchone()
    
    yesterday_val = f"{yesterday_row[0]:,.0f}" if yesterday_row else "---"
    today_val = f"{today_row[0]:,.0f}" if today_row else "MISSING"
    
    liability_marker = " (LIABILITY)" if is_liability else ""
    
    if yesterday_row and not today_row:
        status = "⚠️ MISSING"
        missing_today.append((cat_id, cat_name, cat_type, yesterday_row[0]))
    elif today_row:
        status = "✅ OK"
        found_today.append(cat_name)
    else:
        status = ""
    
    print(f"{cat_name:<40} {cat_type:<15} {yesterday_val:>15} {today_val:>15} {status}")

print(f"\n{'='*80}")
print(f"Summary:")
print(f"  - Categories with values today: {len(found_today)}")
print(f"  - Categories missing today (but had yesterday): {len(missing_today)}")
print(f"{'='*80}\n")

if missing_today:
    print("MISSING CATEGORIES:")
    for cat_id, cat_name, cat_type, yesterday_val in missing_today:
        print(f"  - {cat_name} ({cat_type}): {yesterday_val:,.0f}")

conn.close()
