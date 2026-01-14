"""
Fix missing Self Fund data for Jan 11 and 12, 2026
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

print("="*70)
print("FIXING MISSING SELF FUND DATA")
print("="*70)

with engine.connect() as conn:
    # Get Self Fund category ID
    result = conn.execute(text("""
        SELECT id FROM wealth_categories WHERE name = 'Self Fund'
    """)).fetchone()
    
    if not result:
        print("❌ Self Fund category not found!")
        exit(1)
    
    self_fund_id = result[0]
    print(f"\n✓ Self Fund category ID: {self_fund_id}")
    
    # Get last known value (Jan 10)
    result = conn.execute(text("""
        SELECT present_value, note
        FROM wealth_values
        WHERE wealth_category_id = :cat_id
            AND value_date = '2026-01-10'
    """), {'cat_id': self_fund_id}).fetchone()
    
    if not result:
        print("❌ No Self Fund value found for 2026-01-10!")
        exit(1)
    
    last_value = float(result[0])
    last_note = result[1]
    print(f"✓ Last known value (Jan 10): {last_value:,.0f} HUF")
    print(f"  Note: {last_note}")
    
    # Check if values already exist for Jan 11 and 12
    for date in ['2026-01-11', '2026-01-12']:
        existing = conn.execute(text("""
            SELECT id FROM wealth_values
            WHERE wealth_category_id = :cat_id
                AND value_date = :date
        """), {'cat_id': self_fund_id, 'date': date}).fetchone()
        
        if existing:
            print(f"\n⚠️  {date}: Value already exists, skipping")
            continue
        
        # Insert copied value
        conn.execute(text("""
            INSERT INTO wealth_values (
                wealth_category_id,
                value_date,
                present_value,
                note
            ) VALUES (
                :cat_id,
                :date,
                :value,
                :note
            )
        """), {
            'cat_id': self_fund_id,
            'date': date,
            'value': last_value,
            'note': f'Copied from {last_note or "2026-01-10"} (automated copy)'
        })
        conn.commit()
        print(f"\n✓ {date}: Inserted {last_value:,.0f} HUF")
    
    # Now regenerate snapshots for Jan 11 and 12
    print("\n" + "="*70)
    print("REGENERATING SNAPSHOTS")
    print("="*70)
    
    for snapshot_date in ['2026-01-11', '2026-01-12']:
        print(f"\nProcessing {snapshot_date}...")
        
        # Delete existing snapshot
        conn.execute(text("""
            DELETE FROM total_wealth_snapshots
            WHERE snapshot_date = :date
        """), {'date': snapshot_date})
        conn.commit()
        
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
        
        print(f"  ✓ Regenerated snapshot:")
        print(f"    Portfolio: {portfolio_value_huf:,.0f} HUF")
        print(f"    Pension: {pension_huf:,.0f} HUF")
        print(f"    Other assets: {other_assets_huf:,.0f} HUF")
        print(f"    Net wealth: {net_wealth_huf:,.0f} HUF")

print("\n" + "="*70)
print("DONE! Self Fund data copied and snapshots regenerated")
print("="*70)
