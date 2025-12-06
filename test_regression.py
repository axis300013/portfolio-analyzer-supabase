"""
Comprehensive Regression Test Suite for Portfolio Analyzer
Tests data persistence, API endpoints, and historical functionality
"""
import requests
from datetime import date, timedelta
from backend.app.db import SessionLocal
from backend.app.models import PortfolioValueDaily, Price, FxRate, Instrument

API_BASE = "http://localhost:8000"

class TestDataPersistence:
    """Test that data is properly saved and retrievable"""
    
    def setup_method(self):
        self.db = SessionLocal()
    
    def teardown_method(self):
        self.db.close()
    
    def test_portfolio_values_exist(self):
        """Test that portfolio values are stored"""
        count = self.db.query(PortfolioValueDaily).count()
        assert count > 0, "No portfolio values in database"
        print(f"✓ Portfolio values: {count} records")
    
    def test_prices_exist(self):
        """Test that prices are stored"""
        count = self.db.query(Price).count()
        assert count > 0, "No prices in database"
        print(f"✓ Prices: {count} records")
    
    def test_fx_rates_exist(self):
        """Test that FX rates are stored"""
        count = self.db.query(FxRate).count()
        assert count > 0, "No FX rates in database"
        print(f"✓ FX Rates: {count} records")
    
    def test_instruments_exist(self):
        """Test that instruments are stored"""
        count = self.db.query(Instrument).count()
        assert count == 9, f"Expected 9 instruments, found {count}"
        print(f"✓ Instruments: {count} records")
    
    def test_todays_data_exists(self):
        """Test that today's data is present"""
        today = date.today()
        pv_count = self.db.query(PortfolioValueDaily).filter(
            PortfolioValueDaily.snapshot_date == today
        ).count()
        assert pv_count > 0, f"No portfolio values for {today}"
        print(f"✓ Today's data ({today}): {pv_count} records")
    
    def test_all_instruments_have_prices(self):
        """Test that all instruments have recent prices"""
        instruments = self.db.query(Instrument).all()
        today = date.today()
        
        for instr in instruments:
            price = self.db.query(Price).filter(
                Price.instrument_id == instr.id,
                Price.price_date == today
            ).first()
            assert price is not None, f"No price for {instr.name} on {today}"
        
        print(f"✓ All {len(instruments)} instruments have prices for {today}")
    
    def test_real_prices_not_test(self):
        """Test that we have real prices, not just test data"""
        today = date.today()
        real_prices = self.db.query(Price).filter(
            Price.price_date == today,
            Price.source != 'test'
        ).count()
        
        assert real_prices >= 6, f"Only {real_prices} real prices, expected at least 6"
        print(f"✓ Real prices: {real_prices} records")


class TestAPIEndpoints:
    """Test that all API endpoints work correctly"""
    
    def test_root_endpoint(self):
        """Test API root endpoint"""
        response = requests.get(f"{API_BASE}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✓ Root endpoint working")
    
    def test_snapshot_endpoint(self):
        """Test snapshot endpoint"""
        today = date.today()
        response = requests.get(
            f"{API_BASE}/portfolio/1/snapshot",
            params={"snapshot_date": today.isoformat()}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Snapshot returned no data"
        print(f"✓ Snapshot endpoint: {len(data)} instruments")
    
    def test_summary_endpoint(self):
        """Test summary endpoint"""
        today = date.today()
        response = requests.get(
            f"{API_BASE}/portfolio/1/summary",
            params={"snapshot_date": today.isoformat()}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_value_huf" in data
        assert data["total_value_huf"] > 0
        print(f"✓ Summary endpoint: {data['total_value_huf']:,.2f} HUF")
    
    def test_history_endpoint(self):
        """Test history endpoint"""
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        response = requests.get(
            f"{API_BASE}/portfolio/1/history",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ History endpoint: {len(data)} records")
    
    def test_snapshot_has_price_sources(self):
        """Test that snapshot includes price sources"""
        today = date.today()
        response = requests.get(
            f"{API_BASE}/portfolio/1/snapshot",
            params={"snapshot_date": today.isoformat()}
        )
        data = response.json()
        
        for item in data:
            assert "price_source" in item, f"Missing price_source for {item.get('name')}"
            assert item["price_source"] != "unknown", f"Unknown price source for {item.get('name')}"
        
        print(f"✓ All instruments have price sources")


class TestDataIntegrity:
    """Test data integrity and calculations"""
    
    def setup_method(self):
        self.db = SessionLocal()
    
    def teardown_method(self):
        self.db.close()
    
    def test_portfolio_value_matches_sum(self):
        """Test that total portfolio value matches sum of holdings"""
        today = date.today()
        
        # Get from API
        response = requests.get(
            f"{API_BASE}/portfolio/1/summary",
            params={"snapshot_date": today.isoformat()}
        )
        api_total = response.json()["total_value_huf"]
        
        # Calculate from database
        holdings = self.db.query(PortfolioValueDaily).filter(
            PortfolioValueDaily.snapshot_date == today
        ).all()
        db_total = sum(float(h.value_huf) for h in holdings)
        
        # Allow 0.01% tolerance for rounding
        diff = abs(api_total - db_total)
        tolerance = db_total * 0.0001
        assert diff <= tolerance, f"API total ({api_total}) != DB total ({db_total}), diff={diff}"
        
        print(f"✓ Portfolio value integrity: {db_total:,.2f} HUF")
    
    def test_fx_conversions(self):
        """Test FX rate conversions are correct"""
        today = date.today()
        
        # Get USD instrument
        usd_holding = self.db.query(PortfolioValueDaily).join(
            Instrument
        ).filter(
            PortfolioValueDaily.snapshot_date == today,
            Instrument.currency == 'USD'
        ).first()
        
        if usd_holding:
            # Check FX conversion
            calculated_huf = float(usd_holding.quantity * usd_holding.price * usd_holding.fx_rate)
            stored_huf = float(usd_holding.value_huf)
            
            diff = abs(calculated_huf - stored_huf)
            assert diff < 1, f"FX conversion error: {calculated_huf} vs {stored_huf}"
            print(f"✓ FX conversions correct")
    
    def test_magyar_telekom_price(self):
        """Test that Magyar Telekom has correct ticker and price"""
        today = date.today()
        
        mtel = self.db.query(Instrument).filter(
            Instrument.isin == 'HU0000073507'
        ).first()
        
        price = self.db.query(Price).filter(
            Price.instrument_id == mtel.id,
            Price.price_date == today,
            Price.source.like('%Yahoo%')
        ).first()
        
        assert price is not None, "Magyar Telekom missing Yahoo Finance price"
        assert float(price.price) > 1000, f"Magyar Telekom price {price.price} seems too low"
        print(f"✓ Magyar Telekom: {price.price} HUF from {price.source}")
    
    def test_erste_bond_quantity(self):
        """Test that Erste Bond has corrected fractional quantity"""
        erste_bond = self.db.query(Instrument).filter(
            Instrument.isin == 'AT0000605332'
        ).first()
        
        from backend.app.models import Holding
        holding = self.db.query(Holding).filter(
            Holding.instrument_id == erste_bond.id
        ).first()
        
        # Should be 115.107, not 115107
        assert float(holding.quantity) < 200, f"Erste Bond quantity {holding.quantity} too large - should be 115.107"
        assert float(holding.quantity) > 100, f"Erste Bond quantity {holding.quantity} too small"
        print(f"✓ Erste Bond quantity: {holding.quantity} (corrected)")


def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*80)
    print("  PORTFOLIO ANALYZER - REGRESSION TEST SUITE".center(80))
    print("="*80 + "\n")
    
    test_classes = [
        ("Data Persistence", TestDataPersistence),
        ("API Endpoints", TestAPIEndpoints),
        ("Data Integrity", TestDataIntegrity)
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for category, test_class in test_classes:
        print(f"\n{category}:")
        print("-" * 80)
        
        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
                
                if hasattr(test_instance, 'teardown_method'):
                    test_instance.teardown_method()
                    
            except AssertionError as e:
                failed_tests.append((method_name, str(e)))
                print(f"✗ {method_name}: FAILED - {e}")
            except Exception as e:
                failed_tests.append((method_name, f"Error: {e}"))
                print(f"✗ {method_name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("  TEST SUMMARY".center(80))
    print("="*80)
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed: {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
    
    if failed_tests:
        print("\nFailed Tests:")
        for test_name, error in failed_tests:
            print(f"  ✗ {test_name}")
            print(f"    {error}")
    else:
        print("\n🎉 ALL TESTS PASSED!")
    
    print("\n" + "="*80 + "\n")
    
    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
