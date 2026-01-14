"""
Check loan values before and after December 31, 2025
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_loan_values():
    """Check loan values around December 31"""
    conn = None
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get loan categories
        cursor.execute("""
            SELECT id, name 
            FROM wealth_categories 
            WHERE is_liability = true
            ORDER BY name
        """)
        
        categories = cursor.fetchall()
        
        print("Loan/Liability Values Around December 31, 2025:")
        print("=" * 80)
        
        for cat_id, cat_name in categories:
            print(f"\n📋 {cat_name} (ID: {cat_id})")
            print("-" * 80)
            
            # Get values for December 2025
            cursor.execute("""
                SELECT value_date, present_value, note
                FROM wealth_values
                WHERE wealth_category_id = %s
                  AND value_date >= '2025-12-20'
                  AND value_date <= '2026-01-05'
                ORDER BY value_date
            """, (cat_id,))
            
            values = cursor.fetchall()
            
            if values:
                print(f"{'Date':<15} {'Value':>20} {'Note':<40}")
                print("-" * 80)
                for value_date, present_value, note in values:
                    note_str = (note or '')[:40]
                    print(f"{str(value_date):<15} {present_value:>20,.2f} {note_str:<40}")
            else:
                print("No values found")
        
        # Check last reduction date
        if os.path.exists("data/last_loan_reduction.txt"):
            with open("data/last_loan_reduction.txt", 'r') as f:
                last_reduction = f.read().strip()
                print(f"\n\n📅 Last automatic reduction date: {last_reduction}")
        else:
            print("\n\n⚠️  No last reduction date file found")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_loan_values()
