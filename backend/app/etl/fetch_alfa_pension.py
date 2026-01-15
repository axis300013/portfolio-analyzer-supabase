"""
Alfa Voluntary Pension Fund Balance Fetcher
Fetches balance from https://www.alfanyugdij.hu/TagiPweb/
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from decimal import Decimal
from datetime import date
import re

def fetch_alfa_pension_balance(username: str, password: str, headless: bool = True):
    """
    Fetch balance from Alfa Voluntary Pension Fund portal
    
    Args:
        username: User's contract number
        password: User's password
        headless: Run browser in headless mode (default: True)
    
    Returns:
        tuple: (balance: Decimal, balance_date: date, error: str)
               If successful, returns (balance, date, None)
               If failed, returns (None, None, error_message)
    """
    driver = None
    try:
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Opening Alfa pension portal...")
        driver.get('https://www.alfanyugdij.hu/TagiPweb/')
        time.sleep(3)
        
        print("Waiting for page to load...")
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Find username field
        print("Looking for login form...")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
        )
        print(f"Found username field with selector: input[type=\"text\"]")
        
        # Find password field
        password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        
        # Fill in credentials
        print("Filling login form...")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Find and click login button
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        print(f"Found login button: button[type=\"submit\"]")
        
        print("Submitting login...")
        login_button.click()
        
        # Wait for redirect
        time.sleep(5)
        
        print("Checking if login successful...")
        
        # Get page text
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        print("Page text found:")
        print(page_text[:500])
        
        # Look for balance - "Nyugdíjpénztári számlaegyenlege"
        balance_pattern = r'Nyugdíjpénztári számlaegyenlege.*?([0-9\s]+)\s*HUF'
        match = re.search(balance_pattern, page_text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            # Try alternative patterns
            alternative_patterns = [
                r'számlaegyenlege.*?([0-9\s]+)\s*HUF',
                r'Az Ön egyenlege.*?([0-9\s]+)\s*HUF',
            ]
            
            for alt_pattern in alternative_patterns:
                match = re.search(alt_pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    balance_pattern = alt_pattern
                    break
        
        if not match:
            return None, None, "Balance not found in page"
        
        # Parse balance
        balance_str = match.group(1).replace(' ', '').replace('\xa0', '').replace('\n', '')
        balance = Decimal(balance_str)
        print(f"✓ Balance found: {balance:,.0f} HUF (pattern: {balance_pattern})")
        
        # Try to extract date from pattern like "(2025.12.01. napi árfolyam alapján)"
        balance_date = None
        date_match = re.search(r'\((\d{4})\.(\d{2})\.(\d{2})\.\s*napi', page_text)
        if date_match:
            balance_date = date(
                int(date_match.group(1)), 
                int(date_match.group(2)), 
                int(date_match.group(3))
            )
            print(f"✓ Balance date: {balance_date}")
        
        return balance, balance_date, None
        
    except Exception as e:
        error_msg = f"Error fetching Alfa pension balance: {str(e)}"
        print(f"✗ {error_msg}")
        import traceback
        traceback.print_exc()
        return None, None, error_msg
    
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    # Test the scraper
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    username = os.getenv('ALFA_USERNAME', '12266379')
    password = os.getenv('ALFA_PASSWORD', 'Mobilemobile01')
    
    print("Testing Alfa Voluntary Pension Fund scraper")
    print("="*60)
    
    balance, balance_date, error = fetch_alfa_pension_balance(username, password, headless=False)
    
    if error:
        print(f"\n❌ FAILED: {error}")
    else:
        print(f"\n✅ SUCCESS!")
        print(f"Balance: {balance:,.0f} HUF")
        if balance_date:
            print(f"Date: {balance_date}")
