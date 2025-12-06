"""
Erste Market Web Scraper for Hungarian Funds and Bonds
Scrapes NAV (Net Asset Value) prices from erstemarket.hu using ISIN numbers
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

def fetch_erste_market_price(isin: str) -> tuple[float | None, str | None, str | None]:
    """
    Fetch price for a fund or bond from Erste Market website
    
    Args:
        isin: ISIN identifier for the instrument
        
    Returns:
        Tuple of (price, currency, date_string) or (None, None, None) if fetch fails
    """
    url = f"https://www.erstemarket.hu/befektetesi_alapok/alap/{isin}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find the price - it's in an h2 tag with format "2.446675 HUF"
        # The structure shows: <h2>2.446675 HUF</h2>
        price_elements = soup.find_all('h2')
        
        price_value = None
        price_date = None
        currency = None
        
        for h2 in price_elements:
            text = h2.get_text(strip=True)
            # Look for pattern like "2.446675 HUF" or "222.14 USD" or "10.50 EUR"
            match = re.search(r'([\d.]+)\s*(HUF|USD|EUR|CHF|GBP)', text)
            if match:
                try:
                    price_value = float(match.group(1))
                    currency = match.group(2)
                    logger.info(f"Found price for {isin}: {price_value} {currency}")
                    break
                except ValueError:
                    continue
        
        if not price_value:
            logger.warning(f"Could not find price for {isin} on Erste Market")
            return None, None, None
        
        # Find the date - format is "Árfolyam dátuma: 2025.12.02."
        # Look in the full HTML text
        date_pattern = re.compile(r'Árfolyam dátuma:\s*(\d{4}\.\d{2}\.\d{2})')
        page_text = soup.get_text()
        match = date_pattern.search(page_text)
        if match:
            price_date = match.group(1)
            logger.info(f"Found price date for {isin}: {price_date}")
        else:
            # Default to today if date not found
            price_date = datetime.now().strftime('%Y.%m.%d')
            logger.warning(f"Could not find date for {isin}, using current date")
        
        return price_value, currency, price_date
        
    except requests.RequestException as e:
        logger.error(f"Error fetching Erste Market data for {isin}: {e}")
        return None, None, None
    except Exception as e:
        logger.error(f"Unexpected error parsing Erste Market data for {isin}: {e}")
        return None, None, None


def fetch_all_erste_market_prices(isins: list[str]) -> dict[str, tuple[float, str, str]]:
    """
    Fetch prices for multiple ISINs from Erste Market
    
    Args:
        isins: List of ISIN identifiers
        
    Returns:
        Dictionary mapping ISIN to (price, currency, date) tuple
    """
    results = {}
    
    for isin in isins:
        price, currency, date = fetch_erste_market_price(isin)
        if price is not None:
            results[isin] = (price, currency or 'HUF', date or datetime.now().strftime('%Y.%m.%d'))
    
    return results


if __name__ == "__main__":
    # Test with example ISINs
    logging.basicConfig(level=logging.INFO)
    
    test_isins = [
        ("HU0000705058", "MBH Ingatlan (HUF)"),
        ("AT0000605332", "Erste Bond Dollar (USD)"),
    ]
    
    print(f"\nTesting Erste Market scraper...")
    
    for test_isin, description in test_isins:
        print(f"\n{description}: {test_isin}")
        price, currency, date = fetch_erste_market_price(test_isin)
        
        if price:
            print(f"✓ Success!")
            print(f"  Price: {price} {currency}")
            print(f"  Date: {date}")
        else:
            print(f"✗ Failed to fetch price")
