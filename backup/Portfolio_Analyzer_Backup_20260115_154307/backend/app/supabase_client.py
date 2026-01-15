"""
Supabase REST API Client
Uses HTTPS API instead of direct PostgreSQL connection
This works around ISP/firewall blocks on PostgreSQL port 5432
"""
import os
from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from datetime import datetime

class SupabaseRESTClient:
    """Wrapper for Supabase REST API operations"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        # Try service key first, fallback to anon key
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_KEY) must be set in environment")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # FX Rates
    def insert_fx_rate(self, currency: str, rate: float, date: str, source: str) -> Dict:
        """Insert or update FX rate (base_currency -> currency, target_currency = HUF)"""
        data = {
            "base_currency": currency,
            "target_currency": "HUF",
            "rate": rate,
            "rate_date": date,
            "source": source,
        }
        result = (
            self.client.table("fx_rates")
            .upsert(data, on_conflict="rate_date,base_currency,target_currency,source")
            .execute()
        )
        return result.data[0] if result.data else {}

    def get_fx_rates_for_date(self, rate_date: str) -> List[Dict]:
        """Get all FX rates for a given date"""
        result = (
            self.client.table("fx_rates")
            .select("*")
            .eq("rate_date", rate_date)
            .execute()
        )
        return result.data
    
    def get_latest_fx_rates(self) -> List[Dict]:
        """Get latest FX rates for each currency"""
        result = self.client.table("fx_rates")\
            .select("*")\
            .order("rate_date", desc=True)\
            .execute()
        return result.data
    
    # Instruments
    def get_all_instruments(self, active_only: bool = True) -> List[Dict]:
        """Get all instruments"""
        query = self.client.table("instruments").select("*")
        if active_only:
            query = query.eq("is_active", True)
        result = query.execute()
        return result.data
    
    def upsert_instrument(self, data: Dict) -> Dict:
        """Insert or update instrument"""
        result = self.client.table("instruments").upsert(data).execute()
        return result.data[0] if result.data else {}

    # Prices
    def upsert_price(self, instrument_id: int, price: float, price_date: str, currency: str, source: str) -> Dict:
        """Insert or update price record"""
        payload = {
            "instrument_id": instrument_id,
            "price": price,
            "price_date": price_date,
            "currency": currency,
            "source": source,
        }
        result = (
            self.client.table("prices")
            .upsert(payload, on_conflict="instrument_id,price_date,source")
            .execute()
        )
        return result.data[0] if result.data else {}

    def get_latest_price(self, instrument_id: int) -> Optional[Dict]:
        """Get latest price for instrument"""
        result = (
            self.client.table("prices")
            .select("*")
            .eq("instrument_id", instrument_id)
            .order("price_date", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_price_on_or_before(self, instrument_id: int, price_date: str) -> Optional[Dict]:
        """Get most recent price on or before a date"""
        result = (
            self.client.table("prices")
            .select("*")
            .eq("instrument_id", instrument_id)
            .lte("price_date", price_date)
            .order("price_date", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    
    # Manual Prices
    def insert_manual_price(self, instrument_id: int, price: float, price_date: str, currency: str) -> Dict:
        """Insert manual price"""
        data = {
            "instrument_id": instrument_id,
            "price": price,
            "price_date": price_date,
            "currency": currency
        }
        result = self.client.table("manual_prices").upsert(data).execute()
        return result.data[0] if result.data else {}
    
    def get_latest_manual_price(self, instrument_id: int) -> Optional[Dict]:
        """Get latest manual price for instrument"""
        result = self.client.table("manual_prices")\
            .select("*")\
            .eq("instrument_id", instrument_id)\
            .order("price_date", desc=True)\
            .limit(1)\
            .execute()
        return result.data[0] if result.data else None
    
    # Transactions
    def get_all_transactions(self) -> List[Dict]:
        """Get all transactions"""
        result = self.client.table("transactions").select("*").execute()
        return result.data

    def get_portfolios(self) -> List[Dict]:
        """Get all portfolios"""
        result = self.client.table("portfolios").select("*").execute()
        return result.data
    
    # Portfolio Values Daily
    def insert_portfolio_value(self, data: Dict) -> Dict:
        """Insert portfolio value for a day"""
        result = (
            self.client.table("portfolio_values_daily")
            .upsert(data, on_conflict="portfolio_id,snapshot_date,instrument_id")
            .execute()
        )
        return result.data[0] if result.data else {}

    def get_holdings(self, portfolio_id: int) -> List[Dict]:
        """Get holdings for a portfolio"""
        result = (
            self.client.table("holdings")
            .select("*")
            .eq("portfolio_id", portfolio_id)
            .execute()
        )
        return result.data

    def get_instrument(self, instrument_id: int) -> Optional[Dict]:
        result = (
            self.client.table("instruments")
            .select("*")
            .eq("id", instrument_id)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_fx_rate_on_or_before(self, base_currency: str, target_currency: str, rate_date: str) -> Optional[Dict]:
        result = (
            self.client.table("fx_rates")
            .select("*")
            .eq("base_currency", base_currency)
            .eq("target_currency", target_currency)
            .lte("rate_date", rate_date)
            .order("rate_date", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    
    def get_portfolio_values_by_date(self, snapshot_date: str) -> List[Dict]:
        """Get all portfolio values for a specific date"""
        result = self.client.table("portfolio_values_daily")\
            .select("*")\
            .eq("snapshot_date", snapshot_date)\
            .execute()
        return result.data
    
    def delete_portfolio_values_by_date(self, snapshot_date: str) -> None:
        """Delete portfolio values for a specific date"""
        self.client.table("portfolio_values_daily")\
            .delete()\
            .eq("snapshot_date", snapshot_date)\
            .execute()
    
    # Wealth Categories
    def get_all_wealth_categories(self) -> List[Dict]:
        """Get all wealth categories"""
        result = self.client.table("wealth_categories").select("*").execute()
        return result.data
    
    # Wealth Values
    def get_latest_wealth_values(self) -> List[Dict]:
        """Get latest wealth value for each category"""
        # Get all wealth values ordered by date
        result = self.client.table("wealth_values")\
            .select("*, wealth_categories(*)")\
            .order("value_date", desc=True)\
            .execute()
        
        # Group by category and keep only latest
        seen_categories = set()
        latest_values = []
        for value in result.data:
            cat_id = value['wealth_category_id']
            if cat_id not in seen_categories:
                seen_categories.add(cat_id)
                latest_values.append(value)
        
        return latest_values
    
    def insert_wealth_value(self, data: Dict) -> Dict:
        """Insert wealth value"""
        result = self.client.table("wealth_values").upsert(data).execute()
        return result.data[0] if result.data else {}
    
    def get_wealth_values_by_date(self, value_date: str) -> List[Dict]:
        """Get all wealth values for a specific date"""
        result = self.client.table("wealth_values")\
            .select("*, wealth_categories(*)")\
            .eq("value_date", value_date)\
            .execute()
        return result.data
    
    # Total Wealth Snapshots
    def insert_wealth_snapshot(self, data: Dict) -> Dict:
        """Insert total wealth snapshot"""
        result = (
            self.client.table("total_wealth_snapshots")
            .upsert(data, on_conflict="snapshot_date")
            .execute()
        )
        return result.data[0] if result.data else {}
    
    def get_latest_snapshot(self) -> Optional[Dict]:
        """Get latest wealth snapshot"""
        result = self.client.table("total_wealth_snapshots")\
            .select("*")\
            .order("snapshot_date", desc=True)\
            .limit(1)\
            .execute()
        return result.data[0] if result.data else None
    
    # Generic query method
    def query(self, table: str, select: str = "*", filters: Optional[Dict] = None) -> List[Dict]:
        """Generic query method"""
        query = self.client.table(table).select(select)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data


# Global instance
_supabase_client: Optional[SupabaseRESTClient] = None

def get_supabase_client() -> SupabaseRESTClient:
    """Get or create Supabase REST client singleton"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseRESTClient()
    return _supabase_client
