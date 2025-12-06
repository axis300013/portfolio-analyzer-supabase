import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import FxRate

def fetch_mnb_rates(target_date: date = None) -> tuple[dict, str]:
    """
    Fetch FX rates from MNB for a specific date.
    Returns tuple of (dict of {currency: rate_to_huf}, source_name)
    """
    if target_date is None:
        target_date = date.today()
    
    rates = {}
    
    # Try Method 1: ExchangeRate-API (free, reliable)
    try:
        url = "https://api.exchangerate-api.com/v4/latest/HUF"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data:
                # Convert to HUF per 1 unit of currency (inverse of what API returns)
                for curr, rate in data['rates'].items():
                    if curr in ['USD', 'EUR', 'CHF', 'GBP', 'CZK', 'PLN']:
                        # API gives HUF per 1 unit, we need inverse
                        rates[curr] = Decimal(str(1 / rate))
                
                if rates:
                    print(f"✓ Fetched rates from ExchangeRate-API")
                    return rates, 'ExchangeRate-API'
    except Exception as e:
        print(f"ExchangeRate-API failed: {e}")
    
    # Try Method 2: Frankfurter API (ECB data, free)
    try:
        url = f"https://api.frankfurter.app/{target_date.strftime('%Y-%m-%d')}?to=HUF"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'HUF' in data['rates']:
                # This gives us EUR to HUF
                eur_to_huf = Decimal(str(data['rates']['HUF']))
                rates['EUR'] = eur_to_huf
                
                # Get USD to EUR, then calculate USD to HUF
                url2 = f"https://api.frankfurter.app/{target_date.strftime('%Y-%m-%d')}?from=USD&to=EUR"
                response2 = requests.get(url2, timeout=10)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if 'rates' in data2 and 'EUR' in data2['rates']:
                        usd_to_eur = Decimal(str(data2['rates']['EUR']))
                        rates['USD'] = eur_to_huf / usd_to_eur
                
                if rates:
                    print(f"✓ Fetched rates from Frankfurter API")
                    return rates, 'Frankfurter API (ECB)'
    except Exception as e:
        print(f"Frankfurter API failed: {e}")
    
    # Try Method 3: Fallback to hardcoded recent rates (as backup)
    if not rates:
        print("⚠ Using fallback rates (recent averages)")
        rates = {
            'USD': Decimal('355.50'),
            'EUR': Decimal('395.20'),
            'CHF': Decimal('405.30'),
            'GBP': Decimal('462.80')
        }
    
    return rates, 'Fallback (hardcoded)'

def store_fx_rates(rates: dict, rate_date: date, source: str, db: Session):
    """Store fetched rates in database"""
    for currency, rate in rates.items():
        # Check if record exists
        existing = db.query(FxRate).filter(
            FxRate.rate_date == rate_date,
            FxRate.base_currency == currency,
            FxRate.target_currency == 'HUF',
            FxRate.source == source
        ).first()
        
        if existing:
            # Update existing record
            existing.rate = rate
            existing.retrieved_at = datetime.now()
        else:
            # Create new record
            fx_rate = FxRate(
                rate_date=rate_date,
                base_currency=currency,
                target_currency='HUF',
                rate=rate,
                source=source
            )
            db.add(fx_rate)
    
    db.commit()

def run_fx_fetch():
    """Main function to fetch and store FX rates"""
    db = SessionLocal()
    try:
        today = date.today()
        rates, source = fetch_mnb_rates(today)
        
        if rates:
            store_fx_rates(rates, today, source, db)
            print(f"✓ Stored {len(rates)} FX rates for {today}")
        else:
            print("✗ No rates fetched")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_fx_fetch()
