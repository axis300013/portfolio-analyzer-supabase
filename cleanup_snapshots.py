"""
Delete incorrect snapshot data from Supabase
Removes snapshots for December 2nd and 4th, 2025
"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import date

# Load environment variables
load_dotenv()

def cleanup_snapshots():
    """Delete snapshots for December 2 and 4, 2025"""
    conn = None
    try:
        # Use DATABASE_URL from .env (Supabase connection)
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in .env file")
        
        print(f"Connecting to Supabase...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Dates to delete
        dates_to_delete = ['2025-12-02', '2025-12-04']
        
        total_deleted = 0
        
        for snapshot_date in dates_to_delete:
            print(f"\n📅 Processing {snapshot_date}...")
            date_deleted = 0
            
            # 1. Check and delete from total_wealth_snapshots
            cursor.execute(
                "SELECT snapshot_date, net_wealth_huf FROM total_wealth_snapshots WHERE snapshot_date = %s",
                (snapshot_date,)
            )
            result = cursor.fetchone()
            
            if result:
                print(f"   Found in total_wealth_snapshots: Net Wealth = {result[1]:,.2f} HUF")
                cursor.execute(
                    "DELETE FROM total_wealth_snapshots WHERE snapshot_date = %s",
                    (snapshot_date,)
                )
                date_deleted += cursor.rowcount
                print(f"   ✅ Deleted {cursor.rowcount} from total_wealth_snapshots")
            
            # 2. Check and delete from wealth_values
            cursor.execute(
                "SELECT COUNT(*) FROM wealth_values WHERE value_date = %s",
                (snapshot_date,)
            )
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"   Found in wealth_values: {count} records")
                cursor.execute(
                    "DELETE FROM wealth_values WHERE value_date = %s",
                    (snapshot_date,)
                )
                date_deleted += cursor.rowcount
                print(f"   ✅ Deleted {cursor.rowcount} from wealth_values")
            
            # 3. Check and delete from portfolio_values_daily
            cursor.execute(
                "SELECT COUNT(*) FROM portfolio_values_daily WHERE snapshot_date = %s",
                (snapshot_date,)
            )
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"   Found in portfolio_values_daily: {count} records")
                cursor.execute(
                    "DELETE FROM portfolio_values_daily WHERE snapshot_date = %s",
                    (snapshot_date,)
                )
                date_deleted += cursor.rowcount
                print(f"   ✅ Deleted {cursor.rowcount} from portfolio_values_daily")
            
            if date_deleted == 0:
                print(f"   ℹ️  No data found for this date")
            else:
                total_deleted += date_deleted
                print(f"   📊 Total deleted for {snapshot_date}: {date_deleted} records")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Cleanup completed! Total records deleted: {total_deleted}")
        print("=" * 60)
        
        # Show remaining December snapshots
        print("\nRemaining December 2025 snapshots:")
        cursor.execute("""
            SELECT snapshot_date, net_wealth_huf, portfolio_value_huf
            FROM total_wealth_snapshots 
            WHERE snapshot_date >= '2025-12-01' AND snapshot_date < '2026-01-01'
            ORDER BY snapshot_date
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"{'Date':<15} {'Net Wealth (HUF)':>20} {'Portfolio (HUF)':>20}")
            print("-" * 60)
            for row in results:
                print(f"{row[0]!s:<15} {row[1]:>20,.2f} {row[2]:>20,.2f}")
        else:
            print("No December snapshots remaining")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("Cleaning up incorrect Supabase snapshots...")
    print("=" * 60)
    print("Deleting snapshots for:")
    print("  - December 2, 2025")
    print("  - December 4, 2025")
    print("=" * 60)
    
    # Confirm before deleting
    confirm = input("\nProceed with deletion? (yes/no): ").strip().lower()
    if confirm == 'yes':
        cleanup_snapshots()
    else:
        print("Cancelled.")
