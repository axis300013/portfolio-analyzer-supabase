"""Verify that the dashboard shows complete wealth data"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import date

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

today = date.today()

print(f"\n{'='*70}")
print(f"DASHBOARD DATA VERIFICATION FOR {today}")
print(f"{'='*70}\n")

# Get total wealth breakdown
cursor.execute("""
    SELECT 
        wc.category_type,
        wc.is_liability,
        COUNT(*) as item_count,
        SUM(wv.present_value) as total_value
    FROM wealth_values wv
    JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
    WHERE wv.value_date = %s
    GROUP BY wc.category_type, wc.is_liability
    ORDER BY wc.is_liability, wc.category_type
""", (today,))

breakdown = cursor.fetchall()

print("Wealth Breakdown by Category:\n")
print(f"{'Category Type':<20} {'Type':<15} {'Items':>8} {'Total Value (HUF)':>20}")
print("-" * 70)

assets_total = 0
liabilities_total = 0

for cat_type, is_liability, count, total in breakdown:
    asset_type = "LIABILITY" if is_liability else "ASSET"
    print(f"{cat_type:<20} {asset_type:<15} {count:>8} {total:>20,.0f}")
    
    if is_liability:
        liabilities_total += float(total)
    else:
        assets_total += float(total)

# Get portfolio value
cursor.execute("""
    SELECT SUM(value_huf) as total_portfolio
    FROM portfolio_values_daily
    WHERE snapshot_date = %s
""", (today,))

portfolio_result = cursor.fetchone()
portfolio_value = float(portfolio_result[0]) if portfolio_result and portfolio_result[0] else 0

print("\n" + "="*70)
print("TOTAL SUMMARY:")
print("="*70)
print(f"Portfolio Value:        {portfolio_value:>20,.0f} HUF")
print(f"Other Assets:           {assets_total:>20,.0f} HUF")
print(f"Total Assets:           {portfolio_value + assets_total:>20,.0f} HUF")
print(f"Liabilities:            {liabilities_total:>20,.0f} HUF")
print("-" * 70)
print(f"NET WEALTH:             {portfolio_value + assets_total - liabilities_total:>20,.0f} HUF")
print("="*70)

# List key items that should be present
print("\n\nKEY ITEMS CHECK:")
print("-" * 70)

key_items = [
    ('Peterdy 29', 'property'),
    ('Szokolya', 'property'),
    ('Hitel??llom??ny CIB, Peterdy', 'loan'),  # Special characters version
    ('Self Fund', 'pension'),
    ('Voluntary Fund', 'pension')
]

all_present = True
for item_name, item_type in key_items:
    cursor.execute("""
        SELECT wv.present_value
        FROM wealth_values wv
        JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
        WHERE wc.name = %s AND wv.value_date = %s
    """, (item_name, today))
    
    result = cursor.fetchone()
    if result:
        print(f"✅ {item_name:<40} {result[0]:>15,.0f} HUF")
    else:
        print(f"❌ {item_name:<40} {'MISSING':>15}")
        all_present = False

print("-" * 70)
if all_present:
    print("✅ ALL KEY ITEMS PRESENT - Dashboard should show complete data!")
else:
    print("❌ SOME ITEMS MISSING - Dashboard may show incomplete data")
print("="*70 + "\n")

conn.close()
