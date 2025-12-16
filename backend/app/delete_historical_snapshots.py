"""
Delete existing historical snapshots and regenerate with correct portfolio values.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Delete historical snapshots (2024-07 to 2025-11)
    result = conn.execute(text("""
        DELETE FROM total_wealth_snapshots
        WHERE snapshot_date >= '2024-07-01' AND snapshot_date <= '2025-11-01'
        RETURNING snapshot_date
    """))
    
    deleted_dates = [r[0] for r in result.fetchall()]
    conn.commit()
    
    print(f"Deleted {len(deleted_dates)} historical snapshots")
    print(f"Date range: {min(deleted_dates)} to {max(deleted_dates)}")
