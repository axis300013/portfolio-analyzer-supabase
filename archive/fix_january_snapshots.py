"""
Generate missing snapshots for January 2026
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# Dates that need snapshots
missing_dates = ['2026-01-05', '2026-01-11', '2026-01-12']

print("="*70)
print("GENERATING MISSING SNAPSHOTS FOR JANUARY 2026")
print("="*70)

with engine.connect() as conn:
    for snapshot_date in missing_dates:
        print(f"\nProcessing {snapshot_date}...")
        
        # Check if snapshot already exists
        existing = conn.execute(text("""
            SELECT id FROM total_wealth_snapshots
            WHERE snapshot_date = :date
        """), {'date': snapshot_date}).fetchone()
        
        if existing:
            print(f"  ℹ️  Snapshot already exists, skipping")
            continue
        
        # Aggregate wealth values by category type
        aggregates = conn.execute(text("""
            SELECT 
                wc.category_type,
                wc.is_liability,
                SUM(wv.present_value) as total
            FROM wealth_values wv
            JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
            WHERE wv.value_date = :date
            GROUP BY wc.category_type, wc.is_liability
        """), {'date': snapshot_date}).fetchall()
        
        # Initialize values
        cash_huf = 0
        property_huf = 0
        pension_huf = 0
        other_huf = 0
        total_liabilities_huf = 0
        
        for row in aggregates:
            category_type = row[0]
            is_liability = row[1]
            total = float(row[2])
            
            if is_liability or category_type == 'loan':
                total_liabilities_huf += abs(total)
            elif category_type == 'cash':
                cash_huf += total
            elif category_type == 'property':
                property_huf += total
            elif category_type == 'pension':
                pension_huf += total
            else:
                other_huf += total
        
        # Get portfolio value
        portfolio_result = conn.execute(text("""
            SELECT SUM(value_huf)
            FROM portfolio_values_daily
            WHERE snapshot_date = :date
        """), {'date': snapshot_date}).fetchone()
        
        portfolio_value_huf = float(portfolio_result[0]) if portfolio_result and portfolio_result[0] else 0
        
        # Calculate totals
        other_assets_huf = cash_huf + property_huf + pension_huf + other_huf
        net_wealth_huf = portfolio_value_huf + other_assets_huf - total_liabilities_huf
        
        # Insert snapshot
        conn.execute(text("""
            INSERT INTO total_wealth_snapshots (
                snapshot_date,
                portfolio_value_huf,
                other_assets_huf,
                total_liabilities_huf,
                net_wealth_huf,
                cash_huf,
                property_huf,
                pension_huf,
                other_huf
            ) VALUES (
                :snapshot_date,
                :portfolio_value_huf,
                :other_assets_huf,
                :total_liabilities_huf,
                :net_wealth_huf,
                :cash_huf,
                :property_huf,
                :pension_huf,
                :other_huf
            )
        """), {
            'snapshot_date': snapshot_date,
            'portfolio_value_huf': portfolio_value_huf,
            'other_assets_huf': other_assets_huf,
            'total_liabilities_huf': total_liabilities_huf,
            'net_wealth_huf': net_wealth_huf,
            'cash_huf': cash_huf,
            'property_huf': property_huf,
            'pension_huf': pension_huf,
            'other_huf': other_huf
        })
        conn.commit()
        
        print(f"  ✓ Created snapshot:")
        print(f"    Portfolio: {portfolio_value_huf:,.0f} HUF")
        print(f"    Other assets: {other_assets_huf:,.0f} HUF")
        print(f"    Liabilities: {total_liabilities_huf:,.0f} HUF")
        print(f"    Net wealth: {net_wealth_huf:,.0f} HUF")

print("\n" + "="*70)
print("DONE!")
print("="*70)
