"""Check which portfolio items have values in early months of history.csv"""
import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'history.csv')

for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue

print("Portfolio items in early months (July-December 2024):\n")

# Filter for long/portfolio items
portfolio_rows = df[df.iloc[:, 0].str.strip().str.lower() == 'long']

for idx, row in portfolio_rows.iterrows():
    item_name = row.iloc[1]
    # Columns 3-8 are July-December 2024
    early_values = row.iloc[3:9]
    has_data = any(pd.notna(v) and v != 0 for v in early_values)
    
    if has_data:
        print(f"{item_name}:")
        for col_idx, val in enumerate(early_values):
            month_names = ['July', 'August', 'September', 'October', 'November', 'December']
            if pd.notna(val) and val != 0:
                print(f"  2024 {month_names[col_idx]}: {val:,.0f}")
        print()
