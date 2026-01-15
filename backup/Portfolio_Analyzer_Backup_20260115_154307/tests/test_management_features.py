"""
Test portfolio management features: transactions, manual prices, instrument management
"""

import requests
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

def test_add_new_instrument():
    """Test adding a new instrument"""
    print("\n=== Test 1: Add New Instrument ===")
    
    payload = {
        "isin": "US0378331005",
        "name": "Apple Inc.",
        "currency": "USD",
        "instrument_type": "EQUITY",
        "ticker": "AAPL",
        "source": "Yahoo Finance"
    }
    
    response = requests.post(f"{BASE_URL}/instruments", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Instrument added: {data['name']} (ISIN: {data['isin']})")
        return data['id']
    elif response.status_code == 400 and "already exists" in response.text:
        print("⚠️  Instrument already exists - getting existing")
        response = requests.get(f"{BASE_URL}/instruments/US0378331005")
        return response.json()['id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_get_all_instruments():
    """Test retrieving all instruments"""
    print("\n=== Test 2: Get All Instruments ===")
    
    response = requests.get(f"{BASE_URL}/instruments")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        instruments = response.json()
        print(f"✅ Total instruments: {len(instruments)}")
        print(f"Sample instruments: {[inst['name'] for inst in instruments[:3]]}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_add_transaction(instrument_id=None):
    """Test adding a BUY transaction"""
    print("\n=== Test 3: Add Transaction (BUY) ===")
    
    if not instrument_id:
        # Use Magyar Telekom (instrument_id=1 typically)
        instrument_id = 1
    
    payload = {
        "portfolio_id": 1,
        "instrument_id": instrument_id,
        "transaction_date": date.today().isoformat(),
        "transaction_type": "BUY",
        "quantity": 100.0,
        "price": 1750.0,
        "notes": "Test purchase",
        "created_by": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/transactions", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Transaction added: {data['transaction_type']} {data['quantity']} units")
        print(f"   Date: {data['transaction_date']}, Price: {data['price']}")
        return data['id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_get_transaction_history():
    """Test retrieving transaction history"""
    print("\n=== Test 4: Get Transaction History ===")
    
    response = requests.get(f"{BASE_URL}/transactions/1")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        transactions = response.json()
        print(f"✅ Total transactions: {len(transactions)}")
        if transactions:
            print(f"Most recent: {transactions[0]['transaction_type']} {transactions[0]['quantity']} "
                  f"{transactions[0]['instrument_name']} on {transactions[0]['transaction_date']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_add_manual_price():
    """Test adding a manual price override"""
    print("\n=== Test 5: Add Manual Price Override ===")
    
    # Magyar Telekom override
    payload = {
        "instrument_id": 1,
        "override_date": date.today().isoformat(),
        "price": 1800.0,
        "currency": "HUF",
        "reason": "Manual adjustment for testing",
        "created_by": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/prices/manual", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Manual price added: {data['price']} {data['currency']}")
        print(f"   Date: {data['override_date']}, Reason: {data['reason']}")
        return data['id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_get_manual_prices():
    """Test retrieving manual price overrides"""
    print("\n=== Test 6: Get Manual Price Overrides ===")
    
    response = requests.get(f"{BASE_URL}/prices/manual")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        manual_prices = response.json()
        print(f"✅ Total manual prices: {len(manual_prices)}")
        if manual_prices:
            print(f"Sample: {manual_prices[0]['instrument_name']} - "
                  f"{manual_prices[0]['price']} {manual_prices[0]['currency']} "
                  f"on {manual_prices[0]['override_date']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_transaction_with_filter():
    """Test transaction filtering by date"""
    print("\n=== Test 7: Get Filtered Transactions ===")
    
    start_date = (date.today() - timedelta(days=7)).isoformat()
    end_date = date.today().isoformat()
    
    response = requests.get(
        f"{BASE_URL}/transactions/1",
        params={"start_date": start_date, "end_date": end_date}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        transactions = response.json()
        print(f"✅ Transactions in last 7 days: {len(transactions)}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_get_instrument_by_isin():
    """Test getting instrument by ISIN"""
    print("\n=== Test 8: Get Instrument by ISIN ===")
    
    response = requests.get(f"{BASE_URL}/instruments/HU0000073507")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        instrument = response.json()
        print(f"✅ Found: {instrument['name']} ({instrument['isin']})")
        print(f"   Type: {instrument['instrument_type']}, Currency: {instrument['currency']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def run_all_tests():
    """Run all management feature tests"""
    print("=" * 60)
    print("PORTFOLIO MANAGEMENT FEATURES - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Add instrument
    instrument_id = test_add_new_instrument()
    results.append(("Add New Instrument", instrument_id is not None))
    
    # Test 2: Get all instruments
    results.append(("Get All Instruments", test_get_all_instruments()))
    
    # Test 3: Add transaction
    transaction_id = test_add_transaction()
    results.append(("Add Transaction", transaction_id is not None))
    
    # Test 4: Get transaction history
    results.append(("Get Transaction History", test_get_transaction_history()))
    
    # Test 5: Add manual price
    manual_price_id = test_add_manual_price()
    results.append(("Add Manual Price", manual_price_id is not None))
    
    # Test 6: Get manual prices
    results.append(("Get Manual Prices", test_get_manual_prices()))
    
    # Test 7: Filtered transactions
    results.append(("Filtered Transactions", test_transaction_with_filter()))
    
    # Test 8: Get instrument by ISIN
    results.append(("Get Instrument by ISIN", test_get_instrument_by_isin()))
    
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
        print("\n🎉 ALL TESTS PASSED! Portfolio management features working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")

if __name__ == "__main__":
    run_all_tests()
