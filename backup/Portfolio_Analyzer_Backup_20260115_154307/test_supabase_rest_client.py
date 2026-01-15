#!/usr/bin/env python
"""Test Supabase REST API client"""
import os
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
from dotenv import load_dotenv
load_dotenv()
from backend.app.supabase_client import get_supabase_client

print("Testing Supabase REST API client...")
try:
    client = get_supabase_client()
    
    # Test 1: Get wealth categories
    cats = client.get_all_wealth_categories()
    print(f"✅ Get wealth categories works! Found {len(cats)} categories")
    for c in cats[:5]:
        print(f"  - ID {c['id']}: {c['name']}")
    
    # Test 2: Get instruments
    instruments = client.get_all_instruments()
    print(f"\n✅ Get instruments works! Found {len(instruments)} instruments")
    for inst in instruments[:3]:
        print(f"  - {inst['name']} ({inst['isin']})")
    
    # Test 3: Get latest FX rates
    fx_rates = client.get_latest_fx_rates()
    print(f"\n✅ Get FX rates works! Found {len(fx_rates)} rates")
    
    print("\n🎉 SUCCESS! Supabase REST API client is working!")
    print("This bypasses the PostgreSQL port 5432 block.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
