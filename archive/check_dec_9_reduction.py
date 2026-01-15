"""
Check what happened on December 9, 2025 (last automatic reduction)
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Check values for the loan categories around December 9
loan_categories = {
    12: "Hitelállomány CIB, Peterdy",
    15: "Kawasaki kötelezettség",
    17: "Cabrio kötelezettség"
}

print("Loan Values Around December 9, 2025 (Last Automatic Reduction)")
print("=" * 90)

for cat_id, cat_name in loan_categories.items():
    print(f"\n{cat_name}")
    print("-" * 90)
    
    cursor.execute("""
        SELECT value_date, present_value, note
        FROM wealth_values
        WHERE wealth_category_id = %s
          AND value_date >= '2025-12-05'
          AND value_date <= '2025-12-15'
        ORDER BY value_date
    """, (cat_id,))
    
    print(f"{'Date':<15} {'Value':>20} {'Change':>15} {'Note':<40}")
    print("-" * 90)
    
    prev_value = None
    for value_date, present_value, note in cursor.fetchall():
        change = ""
        if prev_value is not None:
            diff = present_value - prev_value
            change = f"{diff:+,.2f}"
        print(f"{str(value_date):<15} {present_value:>20,.2f} {change:>15} {(note or '')[:40]}")
        prev_value = present_value

conn.close()
