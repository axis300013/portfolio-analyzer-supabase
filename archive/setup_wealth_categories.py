"""
Setup script for automated wealth fetchers
Creates necessary wealth categories in Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Check if "Self Fund" category exists
print("Checking for 'Self Fund' wealth category...")

response = supabase.table('wealth_categories')\
    .select('*')\
    .eq('name', 'Self Fund')\
    .execute()

if response.data:
    print(f"✓ Category exists: {response.data[0]}")
else:
    print("Category not found. Creating...")
    
    # Create the category
    result = supabase.table('wealth_categories')\
        .insert({
            'category_type': 'pension',
            'name': 'Self Fund',
            'currency': 'HUF',
            'is_liability': False
        })\
        .execute()
    
    print(f"✓ Created category: {result.data[0]}")

print("\nSetup complete!")
