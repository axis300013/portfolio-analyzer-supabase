"""
Verify January 2026 loan reductions were applied
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

print("=" * 90)
print("JANUARY 2026 LOAN REDUCTION VERIFICATION")
print("=" * 90)

# Check last reduction date file
if os.path.exists("data/last_loan_reduction.txt"):
    with open("data/last_loan_reduction.txt", 'r') as f:
        print(f"\n📅 Last Reduction File: {f.read().strip()}")

loan_categories = {
    12: "Hitel??llom??ny CIB, Peterdy",
    15: "Kawasaki k??telezetts??g",
    17: "Cabrio k??telezetts??g"
}

print("\n" + "=" * 90)
print("LOAN VALUES - DECEMBER 31 vs JANUARY 1-2")
print("=" * 90)

for cat_id, cat_name in loan_categories.items():
    print(f"\n{cat_name}")
    print("-" * 90)
    
    cursor.execute("""
        SELECT value_date, present_value, note
        FROM wealth_values
        WHERE wealth_category_id = %s
          AND value_date >= '2025-12-31'
          AND value_date <= '2026-01-03'
        ORDER BY value_date
    """, (cat_id,))
    
    print(f"{'Date':<15} {'Value':>20} {'Change':>15} {'Note':<45}")
    print("-" * 90)
    
    prev_value = None
    for value_date, present_value, note in cursor.fetchall():
        change = ""
        if prev_value is not None:
            diff = present_value - prev_value
            change = f"{diff:+,.2f}"
        note_str = (note or '')[:45]
        print(f"{str(value_date):<15} {present_value:>20,.2f} {change:>15} {note_str:<45}")
        prev_value = present_value

# Check if there were any entries created on Jan 1 or Jan 2
print("\n" + "=" * 90)
print("ALL LIABILITY ENTRIES ON JANUARY 1-2, 2026")
print("=" * 90)

cursor.execute("""
    SELECT wc.name, wv.value_date, wv.present_value, wv.note
    FROM wealth_values wv
    JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
    WHERE wc.is_liability = true
      AND wv.value_date >= '2026-01-01'
      AND wv.value_date <= '2026-01-02'
    ORDER BY wc.name, wv.value_date
""")

results = cursor.fetchall()
if results:
    for name, value_date, value, note in results:
        print(f"\n{name}")
        print(f"  Date: {value_date}")
        print(f"  Value: {value:,.2f} HUF")
        print(f"  Note: {note or 'None'}")
else:
    print("No liability values recorded on January 1-2")

conn.close()
