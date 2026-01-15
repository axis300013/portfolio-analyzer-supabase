#!/usr/bin/env python
"""Test Supabase HTTPS API (same as mobile app uses)"""
from supabase import create_client

url = 'https://hrlzrirsvifxsnccxvsa.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQzMTcsImV4cCI6MjA4MDUyMDMxN30.IAhjGmpcNA9KIi6fSTIPauVVNTIRSb8jBNCJTpmHodA'

print("Testing Supabase HTTPS API (same method mobile app uses)...")
try:
    client = create_client(url, key)
    result = client.table('wealth_categories').select('id,name').limit(5).execute()
    print(f"✅ SUCCESS! HTTPS API Works!")
    print(f"Found {len(result.data)} wealth categories:")
    for r in result.data:
        print(f"  - ID {r['id']}: {r['name']}")
    print("\n✅ This proves: HTTPS to Supabase works fine!")
    print("❌ Only PostgreSQL port 5432 IPv6 is blocked")
except Exception as e:
    print(f"❌ HTTPS API Failed: {e}")
