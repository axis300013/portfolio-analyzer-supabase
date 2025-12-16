"""
Automated Wealth Value Fetcher
Fetches wealth values from external sources and saves to database
"""
from datetime import date
from decimal import Decimal
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .fetch_horizont_pension import fetch_horizont_pension_balance
from .fetch_alfa_pension import fetch_alfa_pension_balance

load_dotenv()

# Initialize database connection
database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)


class WealthFetcher:
    """Base class for automated wealth fetchers"""
    
    def __init__(self, category_name: str):
        self.category_name = category_name
    
    def get_category_id(self) -> int:
        """Get wealth category ID from database"""
        db = SessionLocal()
        try:
            result = db.execute(
                text("SELECT id FROM wealth_categories WHERE name = :name"),
                {"name": self.category_name}
            )
            row = result.fetchone()
            if not row:
                raise Exception(f"Wealth category '{self.category_name}' not found in database")
            return row[0]
        finally:
            db.close()
    
    def save_value(self, value: Decimal, value_date: date, note: str = None):
        """Save wealth value to database"""
        db = SessionLocal()
        try:
            category_id = self.get_category_id()
            
            # Check if value already exists for this date
            existing = db.execute(
                text("""
                    SELECT id FROM wealth_values 
                    WHERE wealth_category_id = :category_id 
                    AND value_date = :value_date
                """),
                {"category_id": category_id, "value_date": value_date}
            ).fetchone()
            
            if existing:
                # Update existing value
                db.execute(
                    text("""
                        UPDATE wealth_values 
                        SET present_value = :value, 
                            note = :note,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """),
                    {"value": float(value), "note": note, "id": existing[0]}
                )
                db.commit()
                print(f"  ✓ Updated {self.category_name}: {value:,.0f} Ft (updated)")
            else:
                # Insert new value
                db.execute(
                    text("""
                        INSERT INTO wealth_values 
                        (wealth_category_id, value_date, present_value, note)
                        VALUES (:category_id, :value_date, :value, :note)
                    """),
                    {
                        "category_id": category_id,
                        "value_date": value_date,
                        "value": float(value),
                        "note": note
                    }
                )
                db.commit()
                print(f"  ✓ Saved {self.category_name}: {value:,.0f} Ft (new)")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
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
        if not self.username or not self.password:
            print("  ⚠ Horizont credentials not found in .env - skipping")
            return False
        
        print(f"  Fetching {self.category_name}...")
        
        balance, balance_date, error = fetch_horizont_pension_balance(
            self.username, 
            self.password,
            headless=True  # Run in background
        )
        
        if error:
            print(f"  ✗ Failed to fetch {self.category_name}: {error}")
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
        if not self.username or not self.password:
            print("  ⚠ Alfa credentials not found in .env - skipping")
            return False
        
        print(f"  Fetching {self.category_name}...")
        
        balance, balance_date, error = fetch_alfa_pension_balance(
            self.username, 
            self.password,
            headless=True  # Run in background
        )
        
        if error:
            print(f"  ✗ Failed to fetch {self.category_name}: {error}")
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
            print(f"  ✗ Error with {fetcher_class.__name__}: {e}")
            failed_count += 1
    
    print(f"\nWealth Fetch Summary: {success_count} successful, {failed_count} failed")
    print("="*50)


if __name__ == "__main__":
    run_wealth_fetch()
