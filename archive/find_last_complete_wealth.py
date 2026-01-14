"""Find the last date with complete wealth data"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import date, timedelta

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Get dates with wealth values, ordered by date descending
cursor.execute("""
    SELECT value_date, COUNT(*) as value_count
    FROM wealth_values
    GROUP BY value_date
    ORDER BY value_date DESC
    LIMIT 20
""")

dates = cursor.fetchall()

print("\n" + "="*60)
print("WEALTH VALUES BY DATE (Last 20 days)")
print("="*60)
print(f"{'Date':<15} {'Value Count':>15}")
print("-"*60)

for value_date, count in dates:
    print(f"{value_date} {count:>15}")

# Find the most recent date with > 10 values (probably complete)
cursor.execute("""
    SELECT value_date, COUNT(*) as value_count
    FROM wealth_values
    GROUP BY value_date
    HAVING COUNT(*) > 10
    ORDER BY value_date DESC
    LIMIT 1
""")

last_complete = cursor.fetchone()

if last_complete:
    print(f"\n{'='*60}")
    print(f"Last date with >10 wealth values: {last_complete[0]} ({last_complete[1]} values)")
    print(f"{'='*60}")
    
    # Show breakdown for that date
    cursor.execute("""
        SELECT wc.category_type, COUNT(*) as count, SUM(wv.present_value) as total
        FROM wealth_values wv
        JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
        WHERE wv.value_date = %s
        GROUP BY wc.category_type
        ORDER BY wc.category_type
    """, (last_complete[0],))
    
    breakdown = cursor.fetchall()
    print(f"\nBreakdown for {last_complete[0]}:")
    for cat_type, count, total in breakdown:
        print(f"  {cat_type:<15}: {count:>3} items, {total:>15,.0f} total")

conn.close()
