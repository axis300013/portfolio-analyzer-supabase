"""
Fix manual_prices sequence to match existing data
Run this if you get "duplicate key value violates unique constraint" errors
"""
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def fix_sequence():
    """Reset the manual_prices_id_seq to the correct value"""
    conn = None
    try:
        # Use DATABASE_URL from .env (Supabase connection)
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in .env file")
        
        print(f"Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get the current max ID
        cursor.execute("SELECT MAX(id) FROM manual_prices")
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            print("No records in manual_prices table")
            max_id = 0
        
        print(f"Current max ID in manual_prices: {max_id}")
        
        # Reset the sequence to max_id + 1
        new_seq_value = max_id + 1
        cursor.execute(f"SELECT setval('manual_prices_id_seq', {new_seq_value}, false)")
        
        print(f"✅ Sequence reset to {new_seq_value}")
        
        # Verify the change
        cursor.execute("SELECT last_value FROM manual_prices_id_seq")
        last_value = cursor.fetchone()[0]
        print(f"Current sequence value: {last_value}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Manual prices sequence fixed successfully!")
        print("You can now insert new manual prices without conflicts.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    print("Fixing manual_prices sequence...")
    print("=" * 50)
    fix_sequence()
