"""
Generate snapshots for ALL historical data (2015-2025).
Combines data from history2.csv (2015-2024) and history.csv (2024-2025).
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import date

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Get all unique dates from wealth_values (both history2 and history)
    result = conn.execute(text("""
        SELECT DISTINCT value_date
        FROM wealth_values
        WHERE note LIKE '%history%'
        ORDER BY value_date
    """)).fetchall()
    
    all_dates = [r[0] for r in result]
    print(f"Found {len(all_dates)} unique dates in historical data")
    if all_dates:
        print(f"Date range: {all_dates[0]} to {all_dates[-1]}")
    
    inserted = 0
    skipped = 0
    updated = 0
    
    for snapshot_date in all_dates:
        # Check if snapshot already exists
        existing = conn.execute(text("""
            SELECT id FROM total_wealth_snapshots
            WHERE snapshot_date = :date
        """), {'date': snapshot_date}).fetchone()
        
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
        
        # Get portfolio value from portfolio_values_daily
        portfolio_result = conn.execute(text("""
            SELECT COALESCE(SUM(value_huf), 0) as total_portfolio
            FROM portfolio_values_daily
            WHERE snapshot_date = :date
        """), {'date': snapshot_date}).fetchone()
        
        portfolio_value_huf = float(portfolio_result[0]) if portfolio_result else 0
        other_assets_huf = cash_huf + property_huf + pension_huf + other_huf
        net_wealth_huf = portfolio_value_huf + other_assets_huf - total_liabilities_huf
        
        if existing:
            # Update existing snapshot
            conn.execute(text("""
                UPDATE total_wealth_snapshots
                SET portfolio_value_huf = :portfolio,
                    other_assets_huf = :other_assets,
                    cash_huf = :cash,
                    property_huf = :property,
                    pension_huf = :pension,
                    other_huf = :other,
                    total_liabilities_huf = :liabilities,
                    net_wealth_huf = :net_wealth
                WHERE snapshot_date = :date
            """), {
                'date': snapshot_date,
                'portfolio': portfolio_value_huf,
                'other_assets': other_assets_huf,
                'cash': cash_huf,
                'property': property_huf,
                'pension': pension_huf,
                'other': other_huf,
                'liabilities': total_liabilities_huf,
                'net_wealth': net_wealth_huf
            })
            print(f"  ✓ Updated snapshot for {snapshot_date}: Net Wealth = {net_wealth_huf:,.0f} HUF")
            updated += 1
        else:
            # Insert new snapshot
            conn.execute(text("""
                INSERT INTO total_wealth_snapshots 
                (snapshot_date, portfolio_value_huf, other_assets_huf, cash_huf, 
                 property_huf, pension_huf, other_huf, total_liabilities_huf, net_wealth_huf)
                VALUES 
                (:date, :portfolio, :other_assets, :cash, :property, :pension, :other, :liabilities, :net_wealth)
            """), {
                'date': snapshot_date,
                'portfolio': portfolio_value_huf,
                'other_assets': other_assets_huf,
                'cash': cash_huf,
                'property': property_huf,
                'pension': pension_huf,
                'other': other_huf,
                'liabilities': total_liabilities_huf,
                'net_wealth': net_wealth_huf
            })
            print(f"  ✓ Created snapshot for {snapshot_date}: Net Wealth = {net_wealth_huf:,.0f} HUF")
            inserted += 1
        
        conn.commit()
    
    print("\n" + "="*80)
    print("Summary:")
    print(f"  Inserted: {inserted} snapshots")
    print(f"  Updated:  {updated} snapshots")
    print(f"  Total:    {len(all_dates)} dates processed")
    print("="*80)
