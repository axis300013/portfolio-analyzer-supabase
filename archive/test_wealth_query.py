"""
Test script to verify wealth values query logic
Shows the most recent value for each wealth category
"""
from backend.app.supabase_client import SupabaseRESTClient
from datetime import datetime

client = SupabaseRESTClient()

print("Fetching all wealth values ordered by category and date...")
all_data = client.client.table('wealth_values').select('''
    *,
    wealth_categories(name, category_type, is_liability)
''').order('wealth_category_id').order('value_date', desc=True).execute()

print(f"Total records fetched: {len(all_data.data)}\n")

# Group by category - keep only most recent for each
latest_by_category = {}
for item in all_data.data:
    category_id = item['wealth_category_id']
    if category_id not in latest_by_category:
        latest_by_category[category_id] = item

print(f"Unique categories with latest values: {len(latest_by_category)}\n")

# Show breakdown by category type
by_type = {}
for item in latest_by_category.values():
    cat_type = item['wealth_categories']['category_type'].upper()
    if cat_type not in by_type:
        by_type[cat_type] = []
    by_type[cat_type].append(item)

# Display results
for cat_type in sorted(by_type.keys()):
    items = by_type[cat_type]
    # Filter non-zero
    non_zero = [i for i in items if i['present_value'] != 0]
    print(f"\n{cat_type}: {len(items)} total, {len(non_zero)} non-zero")
    print("-" * 80)
    for item in items:
        name = item['wealth_categories']['name']
        value = item['present_value']
        date = item['value_date']
        status = "✓" if value != 0 else "✗"
        print(f"  {status} {name:30} {value:>12,.0f} HUF  (date: {date})")

print("\n" + "=" * 80)
print("SUMMARY:")
print(f"Total categories: {len(latest_by_category)}")
print(f"Non-zero values: {len([i for i in latest_by_category.values() if i['present_value'] != 0])}")
print(f"Zero values: {len([i for i in latest_by_category.values() if i['present_value'] == 0])}")
