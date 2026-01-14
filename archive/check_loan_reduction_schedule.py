"""
Check loan reduction status and schedule
"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import date, datetime

load_dotenv()

# Monthly reduction configuration
MONTHLY_REDUCTIONS = {
    "Hitel??llom??ny CIB, Peterdy": 236667,
    "Kawasaki k??telezetts??g": 40000,
    "Cabrio k??telezetts??g": 118958
}

def check_status():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    print("=" * 80)
    print("AUTOMATIC LOAN REDUCTION STATUS")
    print("=" * 80)
    
    # Check last reduction date
    if os.path.exists("data/last_loan_reduction.txt"):
        with open("data/last_loan_reduction.txt", 'r') as f:
            last_reduction_str = f.read().strip()
            last_reduction = datetime.strptime(last_reduction_str, "%Y-%m-%d").date()
            print(f"\n📅 Last Reduction Applied: {last_reduction}")
    else:
        print("\n⚠️  No last reduction date found")
        last_reduction = None
    
    today = date.today()
    print(f"📅 Today's Date: {today}")
    
    # Determine next reduction
    if last_reduction:
        if today.year > last_reduction.year or today.month > last_reduction.month:
            print(f"✅ NEXT REDUCTION DUE: Today ({today}) - New month detected!")
            next_reduction = today
        else:
            # Calculate next month
            if today.month == 12:
                next_reduction = date(today.year + 1, 1, 1)
            else:
                next_reduction = date(today.year, today.month + 1, 1)
            print(f"⏳ Next Reduction: {next_reduction} (1st of next month)")
    else:
        print(f"✅ NEXT REDUCTION DUE: Today ({today}) - Never run before!")
        next_reduction = today
    
    print("\n" + "=" * 80)
    print("CONFIGURED MONTHLY REDUCTIONS")
    print("=" * 80)
    
    for category_name, reduction_amount in MONTHLY_REDUCTIONS.items():
        print(f"\n📋 {category_name}: -{reduction_amount:,.0f} HUF per month")
        
        # Find this category in database
        cursor.execute("""
            SELECT wc.id, wc.is_liability, wv.present_value, wv.value_date
            FROM wealth_categories wc
            LEFT JOIN LATERAL (
                SELECT present_value, value_date
                FROM wealth_values
                WHERE wealth_category_id = wc.id
                ORDER BY value_date DESC
                LIMIT 1
            ) wv ON true
            WHERE wc.name = %s
        """, (category_name,))
        
        result = cursor.fetchone()
        if result:
            cat_id, is_liability, current_value, value_date = result
            print(f"   ID: {cat_id}")
            print(f"   Is Liability: {is_liability}")
            if current_value is not None:
                print(f"   Current Value: {current_value:,.2f} HUF (as of {value_date})")
                after_reduction = float(current_value) - reduction_amount
                if after_reduction < 0:
                    after_reduction = 0
                print(f"   After Reduction: {after_reduction:,.2f} HUF")
            else:
                print(f"   ⚠️  No value found")
        else:
            print(f"   ❌ Category not found in database!")
            print(f"   💡 Searching for similar names...")
            
            # Search for similar
            cursor.execute("""
                SELECT name, id, is_liability
                FROM wealth_categories
                WHERE name ILIKE %s
                LIMIT 3
            """, (f"%{category_name[:10]}%",))
            
            similar = cursor.fetchall()
            if similar:
                for sim_name, sim_id, sim_liability in similar:
                    print(f"      - {sim_name} (ID: {sim_id}, Liability: {sim_liability})")
    
    # Check for any values recorded today that might be reductions
    print("\n" + "=" * 80)
    print(f"VALUES RECORDED TODAY ({today})")
    print("=" * 80)
    
    cursor.execute("""
        SELECT wc.name, wv.present_value, wv.note
        FROM wealth_values wv
        JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
        WHERE wv.value_date = %s
          AND wc.is_liability = true
        ORDER BY wc.name
    """, (today,))
    
    today_values = cursor.fetchall()
    if today_values:
        for name, value, note in today_values:
            print(f"  {name}: {value:,.2f} HUF")
            if note:
                print(f"    Note: {note}")
    else:
        print("  No liability values recorded today")
    
    conn.close()

if __name__ == "__main__":
    check_status()
