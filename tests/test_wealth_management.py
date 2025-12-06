"""
Test wealth management features
"""
import requests
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

BASE_URL = "http://localhost:8000"

def test_get_wealth_categories():
    """Test 1: Get all wealth categories"""
    print("\n=== Test 1: Get Wealth Categories ===")
    
    response = requests.get(f"{BASE_URL}/wealth/categories")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ Total categories: {len(categories)}")
        
        # Count by type
        by_type = {}
        for cat in categories:
            cat_type = cat['category_type']
            by_type[cat_type] = by_type.get(cat_type, 0) + 1
        
        print(f"   Cash: {by_type.get('cash', 0)}")
        print(f"   Property: {by_type.get('property', 0)}")
        print(f"   Pension: {by_type.get('pension', 0)}")
        print(f"   Loans: {by_type.get('loan', 0)}")
        
        return True, categories
    else:
        print(f"❌ Failed: {response.text}")
        return False, []


def test_add_wealth_values(categories):
    """Test 2: Add wealth values for current month"""
    print("\n=== Test 2: Add Wealth Values ===")
    
    today = date.today()
    
    # Test values for each category
    test_values = {
        'MKB account EUR': 5000.0,
        'MKB account HUF': 500000.0,
        'CIB account HUF': 1000000.0,
        'Cash at home HUF': 50000.0,
        'Revolut Account HUF': 200000.0,
        'Cash at home EUR': 1000.0,
        'SZÉP Kártya HUF': 150000.0,
        'Peterdy 29': 45000000.0,
        'Self Fund': 3000000.0,
        'Voluntary Fund': 2500000.0,
        'Tartozás felém': 500000.0,
        'Hitelállomány CIB, Peterdy': 25000000.0,  # Loan
        'motor Kawasaki': 1500000.0,
        'BMW Cabrio': 2500000.0,
        'Kawasaki kötelezettség': 800000.0,  # Loan
        'Szokolya': 15000000.0,
        'Cabrio kötelezettség': 1200000.0  # Loan
    }
    
    success_count = 0
    
    for cat in categories:
        if cat['name'] in test_values:
            payload = {
                "wealth_category_id": cat['id'],
                "value_date": today.isoformat(),
                "present_value": test_values[cat['name']],
                "note": f"Test value for {today.strftime('%B %Y')}"
            }
            
            response = requests.post(f"{BASE_URL}/wealth/values", json=payload)
            
            if response.status_code == 200:
                success_count += 1
            else:
                print(f"   ❌ Failed for {cat['name']}: {response.text}")
    
    print(f"✅ Added {success_count}/{len(test_values)} wealth values")
    return success_count == len(test_values)


def test_get_wealth_values():
    """Test 3: Get wealth values for today"""
    print("\n=== Test 3: Get Wealth Values for Today ===")
    
    today = date.today()
    response = requests.get(f"{BASE_URL}/wealth/values/{today.isoformat()}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        values = response.json()
        print(f"✅ Retrieved {len(values)} wealth values")
        
        # Show sample
        if values:
            print(f"   Sample: {values[0]['name']} = {values[0]['present_value']:,.2f} {values[0]['currency']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_calculate_total_wealth():
    """Test 4: Calculate total wealth"""
    print("\n=== Test 4: Calculate Total Wealth ===")
    
    today = date.today()
    response = requests.get(f"{BASE_URL}/wealth/total/{today.isoformat()}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total wealth calculated:")
        print(f"   Portfolio Value: {data['portfolio_value_huf']:,.2f} HUF")
        print(f"   Other Assets: {data['other_assets_huf']:,.2f} HUF")
        print(f"   Total Liabilities: {data['total_liabilities_huf']:,.2f} HUF")
        print(f"   Net Wealth: {data['net_wealth_huf']:,.2f} HUF")
        print(f"   ")
        print(f"   Breakdown:")
        print(f"     Cash: {data['breakdown']['cash']:,.2f} HUF")
        print(f"     Property: {data['breakdown']['property']:,.2f} HUF")
        print(f"     Pension: {data['breakdown']['pension']:,.2f} HUF")
        print(f"     Loans: {data['breakdown']['loans']:,.2f} HUF")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_save_wealth_snapshot():
    """Test 5: Save wealth snapshot"""
    print("\n=== Test 5: Save Wealth Snapshot ===")
    
    today = date.today()
    response = requests.post(f"{BASE_URL}/wealth/snapshot/{today.isoformat()}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Snapshot saved:")
        print(f"   Date: {data['snapshot_date']}")
        print(f"   Net Wealth: {data['net_wealth_huf']:,.2f} HUF")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_wealth_history(categories):
    """Test 6: Get wealth history for a category"""
    print("\n=== Test 6: Get Wealth History ===")
    
    # Get first cash category
    cash_cat = next((c for c in categories if c['category_type'] == 'cash'), None)
    
    if not cash_cat:
        print("❌ No cash category found")
        return False
    
    response = requests.get(f"{BASE_URL}/wealth/history/{cash_cat['id']}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        history = response.json()
        print(f"✅ History for '{cash_cat['name']}':")
        print(f"   Total records: {len(history)}")
        
        if history:
            print(f"   Latest: {history[0]['date']} = {history[0]['value']:,.2f}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_get_snapshots():
    """Test 7: Get wealth snapshots"""
    print("\n=== Test 7: Get Wealth Snapshots ===")
    
    response = requests.get(f"{BASE_URL}/wealth/snapshots")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        snapshots = response.json()
        print(f"✅ Total snapshots: {len(snapshots)}")
        
        if snapshots:
            latest = snapshots[0]
            print(f"   Latest: {latest['snapshot_date']}")
            print(f"   Net Wealth: {latest['net_wealth_huf']:,.2f} HUF")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_update_wealth_value(categories):
    """Test 8: Update a wealth value"""
    print("\n=== Test 8: Update Wealth Value ===")
    
    # Update MKB account HUF
    mkb_cat = next((c for c in categories if c['name'] == 'MKB account HUF'), None)
    
    if not mkb_cat:
        print("❌ Category not found")
        return False
    
    today = date.today()
    payload = {
        "wealth_category_id": mkb_cat['id'],
        "value_date": today.isoformat(),
        "present_value": 600000.0,  # Updated value
        "note": "Updated test value"
    }
    
    response = requests.post(f"{BASE_URL}/wealth/values", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Value updated:")
        print(f"   {mkb_cat['name']}: {data['present_value']:,.2f} HUF")
        print(f"   Note: {data['note']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_add_new_category():
    """Test 9: Add a new wealth category"""
    print("\n=== Test 9: Add New Category ===")
    
    payload = {
        "category_type": "other",
        "name": "Test Investment Account",
        "currency": "USD",
        "is_liability": False
    }
    
    response = requests.post(f"{BASE_URL}/wealth/categories", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Category added:")
        print(f"   ID: {data['id']}")
        print(f"   Name: {data['name']}")
        print(f"   Type: {data['category_type']}")
        
        return True
    else:
        # Category might already exist
        if "already exists" in response.text or "unique" in response.text.lower():
            print(f"⚠️  Category already exists (OK)")
            return True
        print(f"❌ Failed: {response.text}")
        return False


def run_all_tests():
    """Run all wealth management tests"""
    print("=" * 60)
    print("WEALTH MANAGEMENT - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Get categories
    success, categories = test_get_wealth_categories()
    results.append(("Get Wealth Categories", success))
    
    if not success:
        print("\n⚠️  Cannot proceed without categories")
        return
    
    # Test 2: Add wealth values
    results.append(("Add Wealth Values", test_add_wealth_values(categories)))
    
    # Test 3: Get wealth values
    results.append(("Get Wealth Values", test_get_wealth_values()))
    
    # Test 4: Calculate total wealth
    results.append(("Calculate Total Wealth", test_calculate_total_wealth()))
    
    # Test 5: Save snapshot
    results.append(("Save Wealth Snapshot", test_save_wealth_snapshot()))
    
    # Test 6: Wealth history
    results.append(("Get Wealth History", test_wealth_history(categories)))
    
    # Test 7: Get snapshots
    results.append(("Get Wealth Snapshots", test_get_snapshots()))
    
    # Test 8: Update value
    results.append(("Update Wealth Value", test_update_wealth_value(categories)))
    
    # Test 9: Add new category
    results.append(("Add New Category", test_add_new_category()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Wealth management system working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")


if __name__ == "__main__":
    run_all_tests()
