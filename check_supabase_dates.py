#!/usr/bin/env python3
"""Quick script to check what dates exist in Supabase"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("Connecting to Supabase...")
print(f"Database: {DATABASE_URL.split('@')[1].split('/')[0]}")
print()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check portfolio_values_daily
    print("📊 PORTFOLIO_VALUES_DAILY:")
    cursor.execute("""
        SELECT DISTINCT snapshot_date 
        FROM portfolio_values_daily 
        ORDER BY snapshot_date DESC 
        LIMIT 10
    """)
    dates = cursor.fetchall()
    for row in dates:
        print(f"  ✓ {row[0]}")
    
    # Count records for today
    print()
    print("🔍 Records for 2025-12-06:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM portfolio_values_daily 
        WHERE snapshot_date = '2025-12-06'
    """)
    count = cursor.fetchone()[0]
    print(f"  portfolio_values_daily: {count} records")
    
    # Check wealth_values
    cursor.execute("""
        SELECT COUNT(*) 
        FROM wealth_values 
        WHERE value_date = '2025-12-06'
    """)
    wealth_count = cursor.fetchone()[0]
    print(f"  wealth_values: {wealth_count} records")
    
    # Check total_wealth_snapshots
    cursor.execute("""
        SELECT COUNT(*) 
        FROM total_wealth_snapshots 
        WHERE snapshot_date = '2025-12-06'
    """)
    total_count = cursor.fetchone()[0]
    print(f"  total_wealth_snapshots: {total_count} records")
    
    if count > 0:
        print()
        print("✅ Today's data EXISTS in Supabase!")
        print("   The mobile app should show 2025-12-06 as selectable.")
    else:
        print()
        print("❌ Today's data NOT FOUND in Supabase.")
        print("   The Daily Update may not have completed successfully.")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
