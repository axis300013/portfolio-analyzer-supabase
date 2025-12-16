"""Check CSV structure to find the totals row."""
import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'history.csv')

for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        print(f"✓ Read with encoding: {encoding}")
        break
    except UnicodeDecodeError:
        continue

print(f"\nCSV Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\n" + "="*80)
print("First column values (looking for 'Totals'):")
print("="*80)

for idx in range(len(df)):
    first_col = df.iloc[idx, 0]
    if pd.notna(first_col):
        print(f"Row {idx}: '{first_col}'")

print("\n" + "="*80)
print("Last 5 rows:")
print("="*80)
print(df.tail(5))
