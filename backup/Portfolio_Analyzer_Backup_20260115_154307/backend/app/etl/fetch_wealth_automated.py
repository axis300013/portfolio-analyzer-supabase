"""
Automated Wealth Value Fetcher
Fetches wealth values from external sources and saves to database
"""
from datetime import date
from decimal import Decimal
import os
from dotenv import load_dotenv
from .fetch_horizont_pension import fetch_horizont_pension_balance
from .fetch_alfa_pension import fetch_alfa_pension_balance
from ..supabase_client import get_supabase_client

load_dotenv()

# Detect cloud environment
IS_CLOUD = os.getenv('RAILWAY_ENVIRONMENT') == 'production'


class WealthFetcher:
    """Base class for automated wealth fetchers"""
    
    def __init__(self, category_name: str):
        self.category_name = category_name
        self.client = get_supabase_client()
    
    def get_category_id(self) -> int:
        """Get wealth category ID from database"""
        result = (
            self.client.client.table("wealth_categories")
            .select("id")
            .eq("name", self.category_name)
            .limit(1)
            .execute()
        ).data
        if not result:
            raise Exception(f"Wealth category '{self.category_name}' not found in database")
        return result[0]["id"]
    
    def save_value(self, value: Decimal, value_date: date, note: str = None):
        """Save wealth value to database"""
        category_id = self.get_category_id()

        existing = (
            self.client.client.table("wealth_values")
            .select("id")
            .eq("wealth_category_id", category_id)
            .eq("value_date", value_date.isoformat())
            .limit(1)
            .execute()
        ).data

        payload = {
            "wealth_category_id": category_id,
            "value_date": value_date.isoformat(),
            "present_value": float(value),
            "note": note,
        }

        if existing:
            payload["id"] = existing[0]["id"]
        self.client.insert_wealth_value(payload)

        status = "updated" if existing else "new"
        print(f"  [OK] Saved {self.category_name}: {value:,.0f} Ft ({status})")
    
    def fetch_and_save(self):
        """Fetch value and save to database - override in subclasses"""
        raise NotImplementedError("Subclasses must implement fetch_and_save()")


class HorizontPensionFetcher(WealthFetcher):
    """Fetcher for Horizont Pension Fund"""
    
    def __init__(self):
        super().__init__("Self Fund")
        self.username = os.getenv('HORIZONT_USERNAME')
        self.password = os.getenv('HORIZONT_PASSWORD')
    
    def fetch_and_save(self):
        """Fetch Horizont pension balance and save to database"""
        if IS_CLOUD:
            print("  [SKIP] Skipping Horizont fetch in cloud environment (Selenium not available)")
            return False
        
        if not self.username or not self.password:
            print("  [SKIP] Horizont credentials not found in .env - skipping")
            return False
        
        print(f"  Fetching {self.category_name}...")
        
        balance, balance_date, error = fetch_horizont_pension_balance(
            self.username, 
            self.password,
            headless=True  # Run in background
        )
        
        if error:
            print(f"  [ERROR] Failed to fetch {self.category_name}: {error}")
            return False
        
        # Save to database
        note = f"Auto-fetched from Horizont portal (balance date: {balance_date})"
        self.save_value(balance, date.today(), note)
        
        return True


class AlfaPensionFetcher(WealthFetcher):
    """Fetcher for Alfa Voluntary Pension Fund"""
    
    def __init__(self):
        super().__init__("Voluntary Fund")
        self.username = os.getenv('ALFA_USERNAME')
        self.password = os.getenv('ALFA_PASSWORD')
    
    def fetch_and_save(self):
        """Fetch Alfa pension balance and save to database"""
        if IS_CLOUD:
            print("  [SKIP] Skipping Alfa fetch in cloud environment (Selenium not available)")
            return False
        
        if not self.username or not self.password:
            print("  [SKIP] Alfa credentials not found in .env - skipping")
            return False
        
        print(f"  Fetching {self.category_name}...")
        
        balance, balance_date, error = fetch_alfa_pension_balance(
            self.username, 
            self.password,
            headless=True  # Run in background
        )
        
        if error:
            print(f"  [ERROR] Failed to fetch {self.category_name}: {error}")
            return False
        
        # Save to database
        note = f"Auto-fetched from Alfa portal (balance date: {balance_date})"
        self.save_value(balance, date.today(), note)
        
        return True


# Registry of all automated fetchers
WEALTH_FETCHERS = [
    HorizontPensionFetcher,
    AlfaPensionFetcher,
    # Add more fetchers here as they are implemented:
    # OTPBankFetcher,
    # RevolutFetcher,
    # etc.
]


def run_wealth_fetch():
    """Run all automated wealth fetchers"""
    print("\n" + "="*50)
    print("Fetching Automated Wealth Values")
    print("="*50)
    
    success_count = 0
    failed_count = 0
    
    for fetcher_class in WEALTH_FETCHERS:
        try:
            fetcher = fetcher_class()
            if fetcher.fetch_and_save():
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"  [ERROR] Error with {fetcher_class.__name__}: {e}")
            failed_count += 1
    
    print(f"\nWealth Fetch Summary: {success_count} successful, {failed_count} failed")
    print("="*50)


if __name__ == "__main__":
    run_wealth_fetch()
