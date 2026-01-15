"""
Verify that all data from history.csv was imported correctly by comparing totals.
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

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

# Read CSV with correct encoding
csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'history.csv')

for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        print(f"✓ Successfully read CSV with encoding: {encoding}")
        break
    except UnicodeDecodeError:
        continue
else:
    print("ERROR: Could not read CSV with any encoding")
    sys.exit(1)

print(f"CSV has {len(df)} rows and {len(df.columns)} columns")
print()

# Extract totals row (check both first and second columns)
totals_row = None
for idx in range(len(df) - 1, -1, -1):
    # Check first column
    if pd.notna(df.iloc[idx, 0]) and str(df.iloc[idx, 0]).strip().lower() == 'totals':
        totals_row = df.iloc[idx]
        break
    # Check second column
    if pd.notna(df.iloc[idx, 1]) and str(df.iloc[idx, 1]).strip().lower() == 'totals':
        totals_row = df.iloc[idx]
        break

if totals_row is None:
    print("ERROR: Could not find 'Totals' row in CSV")
    sys.exit(1)

print("=" * 80)
print("CSV TOTALS (from history.csv)")
print("=" * 80)

# Month columns start at index 3
month_columns = df.columns[3:]
csv_totals = {}

for col_idx, col_name in enumerate(month_columns, start=3):
    # Parse month
    month_index = col_idx - 3
    if month_index < 6:  # July-December 2024
        year = 2024
        month = month_index + 7
    else:  # January-November 2025
        year = 2025
        month = month_index - 6 + 1
    
    snapshot_date = date(year, month, 1)
    
    # Get total from CSV
    total_value = totals_row[col_name]
    if pd.notna(total_value):
        csv_totals[snapshot_date] = float(total_value)
        print(f"{snapshot_date}: {total_value:,.2f} HUF")

print()
print("=" * 80)
print("DATABASE TOTALS (from total_wealth_snapshots)")
print("=" * 80)

# Get totals from database
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT snapshot_date, net_wealth_huf
        FROM total_wealth_snapshots
        WHERE snapshot_date >= '2024-07-01' AND snapshot_date <= '2025-11-01'
        ORDER BY snapshot_date
    """))
    
    db_totals = {}
    for row in result:
        snapshot_date = row[0]
        net_wealth = float(row[1])
        db_totals[snapshot_date] = net_wealth
        print(f"{snapshot_date}: {net_wealth:,.2f} HUF")

print()
print("=" * 80)
print("COMPARISON (CSV vs Database)")
print("=" * 80)

all_dates = sorted(set(csv_totals.keys()) | set(db_totals.keys()))
differences = []
missing_in_db = []
missing_in_csv = []

for snapshot_date in all_dates:
    csv_val = csv_totals.get(snapshot_date)
    db_val = db_totals.get(snapshot_date)
    
    if csv_val is None:
        missing_in_csv.append(snapshot_date)
        print(f"{snapshot_date}: MISSING IN CSV | DB: {db_val:,.2f}")
    elif db_val is None:
        missing_in_db.append(snapshot_date)
        print(f"{snapshot_date}: CSV: {csv_val:,.2f} | MISSING IN DB")
    else:
        diff = abs(csv_val - db_val)
        diff_pct = (diff / csv_val * 100) if csv_val != 0 else 0
        
        if diff > 1:  # More than 1 HUF difference (accounting for rounding)
            status = "⚠️ DIFFERENCE"
            differences.append((snapshot_date, csv_val, db_val, diff, diff_pct))
        else:
            status = "✓ MATCH"
        
        print(f"{snapshot_date}: {status}")
        print(f"  CSV: {csv_val:,.2f} HUF")
        print(f"  DB:  {db_val:,.2f} HUF")
        if diff > 1:
            print(f"  Diff: {diff:,.2f} HUF ({diff_pct:.2f}%)")
        print()

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total dates in CSV: {len(csv_totals)}")
print(f"Total dates in DB: {len(db_totals)}")
print(f"Dates with differences > 1 HUF: {len(differences)}")
print(f"Dates missing in DB: {len(missing_in_db)}")
print(f"Dates missing in CSV: {len(missing_in_csv)}")

if differences:
    print()
    print("⚠️ DIFFERENCES FOUND:")
    for snapshot_date, csv_val, db_val, diff, diff_pct in differences:
        print(f"  {snapshot_date}: Diff = {diff:,.2f} HUF ({diff_pct:.2f}%)")

if missing_in_db:
    print()
    print("⚠️ MISSING IN DATABASE:")
    for snapshot_date in missing_in_db:
        print(f"  {snapshot_date}: {csv_totals[snapshot_date]:,.2f} HUF")

if not differences and not missing_in_db:
    print()
    print("✅ ALL DATA IMPORTED CORRECTLY! Totals match between CSV and database.")
