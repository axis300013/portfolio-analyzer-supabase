from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Instrument, Price
import requests
from bs4 import BeautifulSoup
import re
from .fetch_erste_market import fetch_erste_market_price

def fetch_price_bse(isin: str, ticker: str, price_date: date) -> tuple[Decimal, str]:
    """Fetch price from Budapest Stock Exchange (BÉT)"""
    try:
        # Try Yahoo Finance with .BD suffix (Budapest)
        if ticker:
            yahoo_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.BD"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(yahoo_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        price = result['meta']['regularMarketPrice']
                        return Decimal(str(price)), 'Yahoo Finance'
        
        # Fallback: Try alternative Yahoo Finance endpoint
        if ticker:
            alt_url = f"https://finance.yahoo.com/quote/{ticker}.BD"
            response = requests.get(alt_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for price in the main price display
                price_elem = soup.find('fin-streamer', {'data-symbol': f'{ticker}.BD', 'data-field': 'regularMarketPrice'})
                if price_elem and price_elem.get('value'):
                    return Decimal(price_elem['value']), 'Yahoo Finance Web'
                
                # Alternative: look for price in specific classes
                price_elem = soup.find('span', {'class': re.compile(r'Fw\(b\)|livePrice')})
                if price_elem:
                    price_text = price_elem.text.strip().replace(',', '')
                    if re.match(r'^\d+\.?\d*$', price_text):
                        return Decimal(price_text), 'Yahoo Finance Web'
        
        return None, None
        
    except Exception as e:
        print(f"Error fetching BSE price for {isin} / {ticker}: {e}")
        return None, None

def fetch_price_fund(isin: str, name: str, price_date: date) -> tuple[Decimal, str]:
    """Fetch price for Hungarian funds
    
    First tries Erste Market web scraping, then falls back to last known price.
    Fund prices are typically updated daily after market close.
    """
    try:
        # Try Erste Market website scraping
        price, currency, date_str = fetch_erste_market_price(isin)
        if price:
            return Decimal(str(price)), 'Erste Market'
        
        # For funds without Erste Market listing, return None to use last known price
        return None, None
        
    except Exception as e:
        print(f"Error fetching fund price for {name}: {e}")
        return None, None

def fetch_price_bond(isin: str, name: str, price_date: date, instrument_currency: str) -> tuple[Decimal, str]:
    """Fetch price for bonds
    
    First tries Erste Market web scraping, then uses fixed values for government bonds.
    """
    try:
        # Special case: Hungarian government bond with fixed par value
        if isin == 'HU0000403522':  # 2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR
            return Decimal('1.0'), 'Fixed Par Value'
        
        # Try Erste Market website scraping for other bonds
        price, currency, date_str = fetch_erste_market_price(isin)
        if price:
            return Decimal(str(price)), 'Erste Market'
        
        # For bonds without pricing, return None to use last known price
        return None, None
        
    except Exception as e:
        print(f"Error fetching bond price for {name}: {e}")
        return None, None

def fetch_and_store_price(instrument: Instrument, price_date: date, db: Session):
    """Fetch and store price for a single instrument
    
    If unable to fetch new price, keeps the most recent price from database.
    This is common for funds (daily update after close) and bonds (infrequent trading).
    """
    price = None
    source = None
    
    if instrument.instrument_type == 'equity':
        # Try to get ticker from instrument, or use common tickers for Hungarian stocks
        ticker_map = {
            'HU0000073507': 'MTEL',       # Magyar Telekom
            'HU0000153937': 'MOL',        # MOL
            'HU0000061726': 'OTP'         # OTP
        }
        ticker = instrument.ticker or ticker_map.get(instrument.isin)
        price, source = fetch_price_bse(instrument.isin, ticker, price_date)
        
    elif instrument.instrument_type == 'fund':
        price, source = fetch_price_fund(instrument.isin, instrument.name, price_date)
        
    elif instrument.instrument_type == 'bond':
        # Use new bond fetcher with Erste Market + fixed values
        price, source = fetch_price_bond(instrument.isin, instrument.name, price_date, instrument.currency)
    
    if price:
        # Check if this price already exists
        existing = db.query(Price).filter(
            Price.instrument_id == instrument.id,
            Price.price_date == price_date,
            Price.source == source
        ).first()
        
        if existing:
            # Update existing price if different
            if existing.price != price:
                existing.price = price
                existing.retrieved_at = datetime.now()
                db.commit()
                return True, 'updated'
            else:
                return True, 'exists'
        else:
            # Create new price record
            price_record = Price(
                instrument_id=instrument.id,
                price_date=price_date,
                price=price,
                currency=instrument.currency,
                source=source
            )
            db.add(price_record)
            db.commit()
            return True, 'fetched'
    else:
        # Check if we have a recent price in database
        last_price = db.query(Price)\
            .filter(Price.instrument_id == instrument.id)\
            .order_by(Price.price_date.desc())\
            .first()
        
        if last_price:
            # Use the most recent price we have
            if last_price.price_date < price_date:
                # Copy forward the last price to today
                price_record = Price(
                    instrument_id=instrument.id,
                    price_date=price_date,
                    price=last_price.price,
                    currency=instrument.currency,
                    source=f"{last_price.source} (carried forward)"
                )
                db.merge(price_record)
                db.commit()
                return True, 'carried_forward'
            else:
                return True, 'exists'
        
        return False, 'no_data'

def run_price_fetch():
    """Fetch prices for all instruments"""
    db = SessionLocal()
    try:
        today = date.today()
        instruments = db.query(Instrument).all()
        
        fetched = 0
        carried_forward = 0
        exists = 0
        failed = 0
        
        for instrument in instruments:
            success, status = fetch_and_store_price(instrument, today, db)
            
            if success:
                if status == 'fetched':
                    print(f"✓ Fetched new price for {instrument.name}")
                    fetched += 1
                elif status == 'carried_forward':
                    print(f"→ Carried forward price for {instrument.name}")
                    carried_forward += 1
                elif status == 'exists':
                    print(f"✓ Price already exists for {instrument.name}")
                    exists += 1
            else:
                print(f"✗ No price available for {instrument.name}")
                failed += 1
        
        print(f"\nSummary: {fetched} fetched, {carried_forward} carried forward, {exists} already exist, {failed} failed")
        print(f"Total: {fetched + carried_forward + exists}/{len(instruments)} instruments have prices for {today}")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_price_fetch()
