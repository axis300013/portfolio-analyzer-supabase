"""Check actual wealth category names in Supabase"""
import requests

API_URL = "http://localhost:8000"

try:
    response = requests.get(f"{API_URL}/wealth/categories")
    
    if response.status_code == 200:
        categories = response.json()
        
        print("\n📋 Wealth Categories in Supabase:")
        print("="*60)
        
        for cat in categories:
            print(f"ID: {cat['id']}")
            print(f"Name: '{cat['name']}'")
            print(f"Type: {cat['category_type']}")
            print(f"Currency: {cat['currency']}")
            print(f"Is Liability: {cat['is_liability']}")
            print("-"*60)
        
        # Check for pension categories specifically
        pension_cats = [c for c in categories if c['category_type'] == 'pension']
        
        print(f"\n💼 Pension Categories: {len(pension_cats)}")
        for cat in pension_cats:
            print(f"   - '{cat['name']}'")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure the backend API is running:")
    print("  Start desktop app or run: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
