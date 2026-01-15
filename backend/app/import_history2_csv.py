"""
Import history2.csv (2015-2024 historical data) into Supabase.
This CSV has a transposed format:
- Row 1: Years
- Row 2: Month-Day (e.g., "3-Jul", "3-Aug")
- Subsequent rows: Category, Item Name, then values for each month
"""
import os
import sys
import pandas as pd
from datetime import date
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

# Category type mappings (same as history.csv)
CATEGORY_TYPE_MAP = {
    'cash': 'CASH',
    'long': 'PORTFOLIO',
    'property': 'PROPERTY',
    'pension': 'PENSION',
    'loan': 'LOAN',
}

# Item name mappings (same as history.csv)
ITEM_NAME_MAP = {
    'Jozsonal': 'Tartozás felém',
    'Magánnyugdjj robi': 'Self Fund',
    'Aegon Önk nyugdíjp. Robi': 'Aegon -> Alfa Önk nyugdíjp. Robi',
}

def clean_value(val):
    """Clean and convert value to float."""
    if pd.isna(val) or val == '' or str(val).strip() == '-' or str(val).strip() == '':
        return None
    
    # Remove spaces and commas
    val_str = str(val).replace(' ', '').replace(',', '')
    try:
        return float(val_str)
    except:
        return None

def parse_date_from_headers(year_row, date_row, col_idx):
    """Parse date from year and month-day headers."""
    year = year_row.iloc[col_idx]
    date_str = date_row.iloc[col_idx]
    
    if pd.isna(year) or pd.isna(date_str):
        return None
    
    try:
        year = int(float(year))
        # Parse date string like "3-Jul", "1-Feb"
        day_month = str(date_str).strip()
        if '-' not in day_month:
            return None
        
        day, month_abbr = day_month.split('-')
        month_map = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        month = month_map.get(month_abbr)
        if not month:
            return None
        
        # Use 1st of month for all snapshots
        return date(year, month, 1)
    except:
        return None

def get_or_create_wealth_category(db, category_type: str, name: str, is_liability: bool) -> int:
    """Get existing category ID or create new one."""
    # Map name
    mapped_name = ITEM_NAME_MAP.get(name, name)
    
    # Detect currency from name
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
    
    # Create new
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

def get_or_create_instrument(db, name: str) -> int:
    """Get existing instrument ID or create new one for portfolio items."""
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
        SELECT id FROM instruments WHERE name = :name
    """), {'name': name}).fetchone()
    
    if result:
        return result[0]
    
    # Create new
    try:
        # Generate a dummy ISIN based on name
        dummy_isin = 'HIST' + name[:6].upper().replace(' ', '')
        result = db.execute(text("""
            INSERT INTO instruments (name, isin, currency)
            VALUES (:name, :isin, :currency)
            RETURNING id
        """), {'name': name, 'isin': dummy_isin, 'currency': currency})
        new_id = result.fetchone()[0]
        db.commit()
        return new_id
    except Exception as e:
        db.rollback()
        raise e

print("📋 CSV file: " + os.path.join(os.path.dirname(__file__), '..', '..', 'history2.csv'))
csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'history2.csv')

# Try multiple encodings
for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
    try:
        df = pd.read_csv(csv_path, encoding=encoding, header=None)
        print(f"✓ Successfully read with encoding: {encoding}")
        break
    except UnicodeDecodeError:
        continue
else:
    raise Exception("Could not decode CSV with any known encoding")

print(f"Found {len(df)} rows and {len(df.columns)} columns")

with engine.connect() as db:
    # Get portfolio ID
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
    
    # Extract header rows
    year_row = df.iloc[0]
    date_row = df.iloc[1]
    
    stats = {
        'portfolio_inserted': 0,
        'wealth_inserted': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Process each data row (skip header rows and Total row)
    for idx in range(2, len(df)):
        row = df.iloc[idx]
        
        category_type_raw = row.iloc[0]
        item_name = row.iloc[1]
        
        # Skip empty rows and Total row
        if pd.isna(category_type_raw) or pd.isna(item_name):
            continue
        
        if str(item_name).strip().lower() in ['total', 'totals']:
            continue
        
        # Map category type
        category_type = CATEGORY_TYPE_MAP.get(str(category_type_raw).strip().lower(), None)
        if not category_type:
            print(f"⚠️  Unknown category type: {category_type_raw} for {item_name}")
            stats['skipped'] += 1
            continue
        
        item_name = str(item_name).strip()
        is_liability = category_type == 'LOAN'
        
        print(f"\n📌 Processing: {category_type} - {item_name}")
        
        # Get or create entity
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
            db.rollback()
            continue
        
        # Process each value column (starting from column 2)
        for col_idx in range(2, len(row)):
            snapshot_date = parse_date_from_headers(year_row, date_row, col_idx)
            if not snapshot_date:
                continue
            
            # Skip if date overlaps with history.csv (>= 2024-07-01)
            if snapshot_date >= date(2024, 7, 1):
                continue
            
            value = clean_value(row.iloc[col_idx])
            if value is None:
                continue
            
            try:
                if category_type == 'PORTFOLIO':
                    # Insert into portfolio_values_daily
                    existing = db.execute(text("""
                        SELECT id FROM portfolio_values_daily
                        WHERE portfolio_id = :pid AND snapshot_date = :date AND instrument_id = :iid
                    """), {
                        'pid': portfolio_id,
                        'date': snapshot_date,
                        'iid': entity_id
                    }).fetchone()
                    
                    if not existing:
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
                            VALUES (:cid, :date, :val, 'Imported from history2.csv')
                        """), {
                            'cid': entity_id,
                            'date': snapshot_date,
                            'val': float(value)
                        })
                        stats['wealth_inserted'] += 1
                
                db.commit()
                
            except Exception as e:
                print(f"   X Error inserting value for {snapshot_date}: {str(e)[:100]}")
                db.rollback()
                stats['errors'] += 1
    
    print("\n" + "="*80)
    print("📊 Import Summary:")
    print(f"   Portfolio records inserted: {stats['portfolio_inserted']}")
    print(f"   Wealth records inserted: {stats['wealth_inserted']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   Errors: {stats['errors']}")
    print("="*80)
