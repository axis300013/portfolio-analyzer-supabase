"""Verify total snapshot count and date range."""
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv()

# Database connection
engine = create_engine(os.getenv('DATABASE_URL'))

print("\n" + "="*80)
print("SNAPSHOT VERIFICATION")
print("="*80)

with engine.connect() as conn:
    # Total count and date range
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total,
            MIN(snapshot_date) as earliest,
            MAX(snapshot_date) as latest
        FROM total_wealth_snapshots
    """)).fetchone()
    
    print(f"\nTotal snapshots in database: {result[0]}")
    print(f"Date range: {result[1]} to {result[2]}")
    
    # Historical vs current breakdown
    historical = conn.execute(text("""
        SELECT COUNT(*) 
        FROM total_wealth_snapshots
        WHERE snapshot_date < '2024-12-01'
    """)).fetchone()[0]
    
    current = result[0] - historical
    
    print(f"\nBreakdown:")
    print(f"  Historical snapshots (pre Dec-2024): {historical}")
    print(f"  Current snapshots (Dec-2024 onwards): {current}")
    
    # Sample of earliest and latest
    print(f"\n{'='*80}")
    print("Sample Data Points:")
    print(f"{'='*80}")
    
    earliest_5 = conn.execute(text("""
        SELECT snapshot_date, net_wealth_huf
        FROM total_wealth_snapshots
        ORDER BY snapshot_date ASC
        LIMIT 5
    """)).fetchall()
    
    print("\nEarliest 5 snapshots:")
    for row in earliest_5:
        print(f"  {row[0]}: {row[1]:,.0f} HUF")
    
    latest_5 = conn.execute(text("""
        SELECT snapshot_date, net_wealth_huf
        FROM total_wealth_snapshots
        ORDER BY snapshot_date DESC
        LIMIT 5
    """)).fetchall()
    
    print("\nLatest 5 snapshots:")
    for row in latest_5:
        print(f"  {row[0]}: {row[1]:,.0f} HUF")

print(f"\n{'='*80}")
print("✓ VERIFICATION COMPLETE")
print(f"{'='*80}\n")
