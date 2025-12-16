"""
Horizont Pension Fund Web Scraper
Fetches current balance from https://portal.horizontmagannyugdijpenztar.hu
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date, datetime
import time
import re
from decimal import Decimal

def fetch_horizont_pension_balance(username: str, password: str, headless: bool = True) -> tuple[Decimal, date, str]:
    """
    Fetch pension balance from Horizont portal
    
    Args:
        username: Email address for login
        password: Password
        headless: Run browser in headless mode (default True)
        
    Returns:
        Tuple of (balance, balance_date, error_message)
        If successful, error_message is None
        If failed, balance and balance_date are None
    """
    
    # Configure Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')  # Run without opening browser window
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Hide automation
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    
    try:
        # Initialize Chrome driver with automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Opening Horizont portal...")
        driver.get('https://portal.horizontmagannyugdijpenztar.hu/main/#/bejelentkezes')
        
        # Wait longer for SPA to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Print page source for debugging
        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)
        
        print("Looking for login form...")
        
        # Try multiple selectors for username field
        username_selectors = [
            'input[type="email"]',
            'input[type="text"]',
            'input[name="username"]',
            'input[name="email"]',
            'input[id*="username"]',
            'input[id*="email"]',
            'input[placeholder*="mail"]',
            'input[placeholder*="felhasználó"]'
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Found username field with selector: {selector}")
                break
            except:
                continue
        
        if not username_field:
            # If no field found, save page source for debugging
            with open('horizont_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Page source saved to horizont_page_source.html")
            raise Exception("Could not find username input field")
        
        password_field = driver.find_element(By.CSS_SELECTOR, 
            'input[type="password"], input[name="password"], input[id*="password"]')
        
        print("Filling login form...")
        username_field.clear()
        username_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)
        
        # Save page source before looking for button
        with open('horizont_login_form.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Page source saved to horizont_login_form.html")
        
        # Find and click login button - try multiple selectors
        login_button = None
        button_selectors = [
            'button[type="submit"]',
            'button[class*="login"]',
            'button[class*="btn"]',
            'input[type="submit"]',
            'button',  # Any button
            'a[class*="login"]',
            '*[type="submit"]'
        ]
        
        for selector in button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in buttons:
                    btn_text = btn.text.lower() if btn.text else ''
                    if 'bejelent' in btn_text or 'login' in btn_text or btn.get_attribute('type') == 'submit':
                        login_button = btn
                        print(f"Found login button: {selector} - '{btn.text}'")
                        break
                if login_button:
                    break
            except:
                continue
        
        if not login_button:
            raise Exception("Could not find login button")
        
        print("Submitting login...")
        login_button.click()
        
        # Wait for redirect after login (SPA navigation)
        time.sleep(5)
        
        # Check if login was successful by looking for dashboard elements
        print("Checking if login successful...")
        
        # Look for balance text: "A 2025.12.03. napi egyenleged:"
        # This might be in different elements depending on the page structure
        balance_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                "//*[contains(text(), 'napi egyenleged') or contains(text(), 'egyenleg')]"))
        )
        
        # Get the full page text to search for the balance
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        print("Page text found:")
        print(page_text[:500])  # Print first 500 chars for debugging
        
        # Parse the balance using regex
        # Looking for pattern like: "A 2025.12.03. napi egyenleged: 11 865 992 Ft"
        balance_pattern = r'A (\d{4})\.(\d{2})\.(\d{2})\. napi egyenleged[:\s]+([0-9\s]+)\s*Ft'
        match = re.search(balance_pattern, page_text)
        
        if match:
            year, month, day = match.group(1), match.group(2), match.group(3)
            balance_str = match.group(4).replace(' ', '')  # Remove spaces
            
            balance = Decimal(balance_str)
            balance_date = date(int(year), int(month), int(day))
            
            print(f"✓ Balance found: {balance:,.0f} Ft (as of {balance_date})")
            return balance, balance_date, None
        else:
            # Alternative: Look for any large number followed by Ft
            alt_pattern = r'([0-9\s]{7,})\s*Ft'
            alt_match = re.search(alt_pattern, page_text)
            
            if alt_match:
                balance_str = alt_match.group(1).replace(' ', '')
                balance = Decimal(balance_str)
                balance_date = date.today()  # Use today's date as fallback
                
                print(f"✓ Balance found (alternative): {balance:,.0f} Ft")
                return balance, balance_date, None
            else:
                return None, None, "Balance text not found on page"
    
    except Exception as e:
        error_msg = f"Error during web scraping: {str(e)}"
        print(f"✗ {error_msg}")
        
        # Save screenshot for debugging if driver is available
        if driver:
            try:
                screenshot_path = f"horizont_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
            except:
                pass
        
        return None, None, error_msg
    
    finally:
        if driver:
            driver.quit()


def test_horizont_scraper():
    """Test the Horizont pension scraper"""
    print("\n" + "="*60)
    print("TESTING HORIZONT PENSION FUND SCRAPER")
    print("="*60)
    
    # Credentials (should be moved to .env in production)
    USERNAME = "axis3000@gmail.com"
    PASSWORD = "Clobufclobuf01#"
    
    # First try with visible browser to see what's happening
    print("\n🔍 Running in VISIBLE mode for debugging...")
    balance, balance_date, error = fetch_horizont_pension_balance(USERNAME, PASSWORD, headless=False)
    
    if error:
        print(f"\n❌ FAILED: {error}")
        return False
    else:
        print(f"\n✅ SUCCESS!")
        print(f"   Balance: {balance:,.0f} Ft")
        print(f"   Date: {balance_date}")
        return True


if __name__ == "__main__":
    # First, check if Selenium and Chrome driver are available
    try:
        from selenium import webdriver
        print("✓ Selenium is installed")
        
        # Try to initialize Chrome driver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            options = Options()
            options.add_argument('--headless')
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.quit()
            print("✓ Chrome WebDriver is available")
            
            # Run the test
            test_horizont_scraper()
            
        except Exception as e:
            print(f"\n❌ Chrome WebDriver not available: {e}")
            print("\nTo install Chrome WebDriver:")
            print("1. Install via pip: pip install webdriver-manager")
            print("2. Or download manually: https://chromedriver.chromium.org/")
            
    except ImportError:
        print("❌ Selenium not installed")
        print("\nTo install: pip install selenium webdriver-manager")
