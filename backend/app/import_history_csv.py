"""
Import historical data from history.csv (2024 Jul - 2025 Nov) into Supabase.

This script:
1. Reads history.csv with monthly snapshots
2. Maps historical items to existing categories in wealth_categories and instruments
3. Inserts data into portfolio_values_daily and wealth_values tables
4. Ensures data is displayed chronologically before current live data
"""

import os
import sys
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Get Supabase connection from environment
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    sys.exit(1)

# Create database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Category mapping from history.csv to current system
CATEGORY_TYPE_MAP = {
    'cash': 'CASH',
    'long': 'PORTFOLIO',  # Investment instruments
    'Long': 'PORTFOLIO',
    'Prop': 'PROPERTY',
    'property': 'PROPERTY',
    'Pensionr': 'PENSION',
    'pension': 'PENSION',
    'Loan': 'LOAN',
    'loan': 'LOAN',
    'Cash': 'CASH',  # Some items use uppercase
}

# Item name mappings to existing categories/instruments
ITEM_NAME_MAP = {
    # Pension mappings
    'Magánnyugdjj robi': 'Self Fund',
    'Aegon -> Alfa önk nyugdíjp. Robi': 'Voluntary Fund',
    
    # Loan mappings
    'Várható kiadások': 'Expected Expenses',
    'Hitelállomány (Fundamenta)': 'Loan Balance (Fundamenta)',
    'Hitelállomány CIB, Peterdy': 'Hitel állomány CIB, Peterdy',
    'Kawasaki kötelezettség': 'Kawasaki kötelezettség',
    'Cabrio kötelezettség': 'Cabrio kötelezettség',
    
    # Cash mappings
    'Jozsonal': 'Tartozás felém',
    'Tartozás felénk': 'Tartozás felém',
    
    # Keep other names as-is for now
}

# Month names in Hungarian (column headers)
MONTH_NAMES_HU = [
    'július', 'augusztus', 'szeptember', 'október', 'november', 'december',  # 2024
    'január', 'február', 'március', 'április', 'május', 'június',  # 2025
    'július', 'augusztus', 'szeptember', 'október', 'november'  # 2025
]

def parse_month_column(col_name: str, col_index: int) -> Optional[date]:
    """
    Parse month column name to date.
    Columns 5-10 are 2024 (Jul-Dec), columns 11-22 are 2025 (Jan-Nov)
    """
    # Skip non-month columns (Actuals, Baseline)
    if col_index < 3:
        return None
    
    month_index = col_index - 3  # Adjust for Actuals, Baseline
    
    if month_index >= len(MONTH_NAMES_HU):
        return None
    
    # Determine year based on month index
    if month_index < 6:  # July-December 2024
        year = 2024
        month = month_index + 7  # July=7, August=8, ..., December=12
    else:  # January-November 2025
        year = 2025
        month_offset = month_index - 6
        month = month_offset + 1  # January=1, February=2, ..., November=11
    
    # Use first day of month for snapshot date
    return date(year, month, 1)


def clean_value(value_str) -> Optional[Decimal]:
    """Clean and convert value string to Decimal."""
    if pd.isna(value_str) or value_str == '' or value_str == '-':
        return None
    
    try:
        # Remove spaces and convert to float first, then Decimal
        cleaned = str(value_str).replace(' ', '').replace(',', '')
        return Decimal(cleaned)
    except (ValueError, TypeError):
        return None


def get_or_create_wealth_category(db, category_type: str, name: str, is_liability: bool = False) -> int:
    """Get existing wealth category ID or create new one."""
    # Map name if needed
    mapped_name = ITEM_NAME_MAP.get(name, name)
    
    # Determine currency (default HUF)
    currency = 'HUF'
    if 'EUR' in name.upper():
        currency = 'EUR'
    elif 'CHF' in name.upper():
        currency = 'CHF'
    elif 'USD' in name.upper():
        currency = 'USD'
    elif 'GBP' in name.upper():
        currency = 'GBP'
    
    # Check if exists
    result = db.execute(text("""
        SELECT id FROM wealth_categories 
        WHERE category_type = :cat_type AND name = :name
    """), {'cat_type': category_type.lower(), 'name': mapped_name}).fetchone()
    
    if result:
        return result[0]
    
    # Create new category - let database generate ID
    try:
        result = db.execute(text("""
            INSERT INTO wealth_categories (category_type, name, currency, is_liability)
            VALUES (:cat_type, :name, :currency, :is_liability)
            RETURNING id
        """), {
            'cat_type': category_type.lower(),
            'name': mapped_name,
            'currency': currency,
            'is_liability': is_liability
        })
        new_id = result.fetchone()[0]
        db.commit()
        return new_id
    except Exception as e:
        db.rollback()
        raise e


def get_or_create_instrument(db, name: str, isin: str = None) -> int:
    """Get existing instrument ID or create new one for portfolio items."""
    # Determine currency from name
    currency = 'HUF'
    if 'EUR' in name.upper():
        currency = 'EUR'
    elif 'CHF' in name.upper():
        currency = 'CHF'
    elif 'USD' in name.upper():
        currency = 'USD'
    
    # Generate ISIN if not provided (use name hash for historical data)
    if not isin:
        isin = f"HIST{abs(hash(name)) % 1000000:06d}"
    
    # Check if exists by name or ISIN
    result = db.execute(text("""
        SELECT id FROM instruments 
        WHERE name = :name OR isin = :isin
    """), {'name': name, 'isin': isin}).fetchone()
    
    if result:
        return result[0]
    
    # Create new instrument - let database generate ID
    try:
        result = db.execute(text("""
            INSERT INTO instruments (isin, name, currency, instrument_type, source)
            VALUES (:isin, :name, :currency, 'Historical', 'history.csv')
            RETURNING id
        """), {
            'isin': isin,
            'name': name,
            'currency': currency
        })
        new_id = result.fetchone()[0]
        db.commit()
        return new_id
    except Exception as e:
        db.rollback()
        raise e


def import_history_csv(csv_path: str, db):
    """Import history.csv into Supabase."""
    print(f"Reading {csv_path}...")
    
    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"Successfully read with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise Exception("Could not decode CSV with any known encoding")
    
    # Get column names
    columns = df.columns.tolist()
    print(f"Found {len(df)} rows and {len(columns)} columns")
    
    stats = {
        'portfolio_inserted': 0,
        'wealth_inserted': 0,
        'categories_created': 0,
        'instruments_created': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Get portfolio ID (use first portfolio or create one)
    portfolio_result = db.execute(text("SELECT id FROM portfolios LIMIT 1")).fetchone()
    if not portfolio_result:
        portfolio_result = db.execute(text("""
            INSERT INTO portfolios (name, owner, currency)
            VALUES ('Historical Portfolio', 'System', 'HUF')
            RETURNING id
        """))
        db.commit()
    portfolio_id = portfolio_result[0]
    
    print(f"📦 Using portfolio ID: {portfolio_id}")
    
    # Process each row
    for idx, row in df.iterrows():
        if idx >= len(df) - 2:  # Skip Totals and Change rows
            continue
        
        category_type_raw = row.iloc[0]  # First column
        item_name = row.iloc[1]  # Second column
        
        # Skip empty rows
        if pd.isna(category_type_raw) or pd.isna(item_name):
            continue
        
        # Map category type
        category_type = CATEGORY_TYPE_MAP.get(str(category_type_raw).strip(), None)
        if not category_type:
            print(f"⚠️  Unknown category type: {category_type_raw} for {item_name}")
            stats['skipped'] += 1
            continue
        
        item_name = str(item_name).strip()
        is_liability = category_type == 'LOAN'
        
        print(f"\n📌 Processing: {category_type} - {item_name}")
        
        # Get or create category/instrument
        try:
            if category_type == 'PORTFOLIO':
                entity_id = get_or_create_instrument(db, item_name)
                print(f"   > Instrument ID: {entity_id}")
            else:
                entity_id = get_or_create_wealth_category(db, category_type, item_name, is_liability)
                print(f"   > Category ID: {entity_id}")
        except Exception as e:
            print(f"   X Error creating entity: {str(e)[:100]}")
            stats['errors'] += 1
            db.rollback()  # Rollback failed transaction
            continue
        
        # Process each month column
        for col_idx, col_name in enumerate(columns[3:], start=3):  # Skip first 3 columns
            snapshot_date = parse_month_column(col_name, col_idx)
            if not snapshot_date:
                continue
            
            value = clean_value(row.iloc[col_idx])
            if value is None:
                continue
            
            try:
                if category_type == 'PORTFOLIO':
                    # Insert into portfolio_values_daily
                    # Check if already exists
                    existing = db.execute(text("""
                        SELECT id FROM portfolio_values_daily
                        WHERE portfolio_id = :pid AND snapshot_date = :date AND instrument_id = :iid
                    """), {
                        'pid': portfolio_id,
                        'date': snapshot_date,
                        'iid': entity_id
                    }).fetchone()
                    
                    if not existing:
                        # Use value as HUF, set quantity to 1, price to value
                        db.execute(text("""
                            INSERT INTO portfolio_values_daily 
                            (portfolio_id, snapshot_date, instrument_id, quantity, price, 
                             instrument_currency, fx_rate, value_huf)
                            VALUES (:pid, :date, :iid, 1, :val, 'HUF', 1, :val)
                        """), {
                            'pid': portfolio_id,
                            'date': snapshot_date,
                            'iid': entity_id,
                            'val': float(value)
                        })
                        stats['portfolio_inserted'] += 1
                else:
                    # Insert into wealth_values
                    existing = db.execute(text("""
                        SELECT id FROM wealth_values
                        WHERE wealth_category_id = :cid AND value_date = :date
                    """), {
                        'cid': entity_id,
                        'date': snapshot_date
                    }).fetchone()
                    
                    if not existing:
                        db.execute(text("""
                            INSERT INTO wealth_values 
                            (wealth_category_id, value_date, present_value, note)
                            VALUES (:cid, :date, :val, 'Imported from history.csv')
                        """), {
                            'cid': entity_id,
                            'date': snapshot_date,
                            'val': float(value)
                        })
                        stats['wealth_inserted'] += 1
                
                db.commit()
                
            except Exception as e:
                print(f"   ❌ Error inserting {snapshot_date}: {e}")
                stats['errors'] += 1
                db.rollback()
                continue
    
    print("\n" + "="*60)
    print("📊 Import Summary:")
    print(f"   Portfolio records inserted: {stats['portfolio_inserted']}")
    print(f"   Wealth records inserted: {stats['wealth_inserted']}")
    print(f"   Categories created: {stats['categories_created']}")
    print(f"   Instruments created: {stats['instruments_created']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['errors']}")
    print("="*60)
    
    return stats


if __name__ == '__main__':
    # Look for history.csv in project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(project_root, 'history.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        print(f"   Looking in: {project_root}")
        sys.exit(1)
    
    print("🚀 Starting historical data import...")
    print(f"📂 CSV file: {csv_path}")
    
    db = SessionLocal()
    try:
        stats = import_history_csv(csv_path, db)
        print("\n✅ Import completed successfully!")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
