"""Delete 2025-12-03 snapshot (test data)"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

target_date = '2025-12-03'

with engine.connect() as conn:
    # Check what exists first
    print(f"\n{'='*80}")
    print(f"Checking data for {target_date}")
    print(f"{'='*80}\n")
    
    snapshot = conn.execute(text("""
        SELECT snapshot_date, portfolio_value_huf, other_assets_huf, net_wealth_huf
        FROM total_wealth_snapshots
        WHERE snapshot_date = :date
    """), {"date": target_date}).fetchone()
    
    if snapshot:
        print(f"Total Wealth Snapshot:")
        print(f"  Portfolio: {snapshot[1]:,.0f} HUF")
        print(f"  Other Assets: {snapshot[2]:,.0f} HUF")
        print(f"  Net Wealth: {snapshot[3]:,.0f} HUF")
    else:
        print(f"No total_wealth_snapshots entry found")
    
    portfolio_count = conn.execute(text("""
        SELECT COUNT(*) FROM portfolio_values_daily WHERE snapshot_date = :date
    """), {"date": target_date}).scalar()
    print(f"\nPortfolio values: {portfolio_count} records")
    
    wealth_count = conn.execute(text("""
        SELECT COUNT(*) FROM wealth_values WHERE value_date = :date
    """), {"date": target_date}).scalar()
    print(f"Wealth values: {wealth_count} records")
    
    # Delete
    print(f"\n{'='*80}")
    print(f"Deleting {target_date} data...")
    print(f"{'='*80}\n")
    
    result1 = conn.execute(text("""
        DELETE FROM total_wealth_snapshots WHERE snapshot_date = :date
    """), {"date": target_date})
    print(f"✓ Deleted from total_wealth_snapshots: {result1.rowcount} rows")
    
    result2 = conn.execute(text("""
        DELETE FROM portfolio_values_daily WHERE snapshot_date = :date
    """), {"date": target_date})
    print(f"✓ Deleted from portfolio_values_daily: {result2.rowcount} rows")
    
    result3 = conn.execute(text("""
        DELETE FROM wealth_values WHERE value_date = :date
    """), {"date": target_date})
    print(f"✓ Deleted from wealth_values: {result3.rowcount} rows")
    
    conn.commit()
    print(f"\n{'='*80}")
    print(f"✓ All {target_date} data deleted successfully")
    print(f"{'='*80}\n")
