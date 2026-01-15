"""Show all portfolio rows from CSV"""
import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'history.csv')

for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue

print("All portfolio/long rows:\n")

for idx, row in df.iterrows():
    cat_type = row.iloc[0]
    if pd.notna(cat_type) and 'long' in str(cat_type).lower():
        item_name = row.iloc[1]
        print(f"Row {idx}: {cat_type} - {item_name}")
        # Show first 5 value columns
        for col_idx in range(3, min(8, len(row))):
            val = row.iloc[col_idx]
            if pd.notna(val) and val != 0:
                print(f"  Column {col_idx} ({df.columns[col_idx]}): {val}")
        print()
