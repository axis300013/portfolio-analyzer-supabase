"""
Check all tables for December 2 and 4, 2025 data
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_all_tables():
    """Check for any data on December 2 and 4, 2025"""
    conn = None
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in .env file")
        
        print(f"Connecting to Supabase...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        dates_to_check = ['2025-12-02', '2025-12-04']
        
        # Tables to check
        tables_to_check = [
            ('total_wealth_snapshots', 'snapshot_date'),
            ('wealth_values', 'value_date'),
            ('portfolio_values_daily', 'value_date'),
            ('transactions', 'transaction_date'),
            ('manual_prices', 'override_date')
        ]
        
        print("\nSearching for data on December 2 and 4, 2025...")
        print("=" * 70)
        
        for table_name, date_column in tables_to_check:
            print(f"\n📊 Checking {table_name}...")
            
            for check_date in dates_to_check:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE {date_column} = %s
                """, (check_date,))
                
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"   ⚠️  {check_date}: Found {count} records")
                    
                    # Show sample data
                    cursor.execute(f"""
                        SELECT * FROM {table_name} 
                        WHERE {date_column} = %s
                        LIMIT 3
                    """, (check_date,))
                    
                    rows = cursor.fetchall()
                    for row in rows:
                        print(f"      {row}")
                else:
                    print(f"   ✓ {check_date}: No records")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_all_tables()
