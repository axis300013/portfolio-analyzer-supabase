"""
Test script for Alfa Voluntary Pension Fund portal automation
Portal: https://www.alfanyugdij.hu/TagiPweb/
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from decimal import Decimal
import re

def test_alfa_pension_login(username: str, password: str, headless: bool = False):
    """
    Test login and balance extraction from Alfa Pension portal
    """
    driver = None
    try:
        print("Setting up Chrome driver...")
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
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Opening Alfa pension portal...")
        driver.get('https://www.alfanyugdij.hu/TagiPweb/')
        time.sleep(3)
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Save page source for inspection
        with open('alfa_login_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Page source saved to alfa_login_page.html")
        
        # Try to find login form
        print("\nLooking for login form...")
        
        # Try different selectors for username field
        username_selectors = [
            ('id', 'username'),
            ('id', 'Username'),
            ('id', 'user'),
            ('id', 'login'),
            ('name', 'username'),
            ('name', 'Username'),
            ('css', 'input[type="text"]'),
            ('css', 'input[name*="user"]'),
            ('css', 'input[id*="user"]'),
        ]
        
        username_field = None
        for selector_type, selector in username_selectors:
            try:
                if selector_type == 'id':
                    username_field = driver.find_element(By.ID, selector)
                elif selector_type == 'name':
                    username_field = driver.find_element(By.NAME, selector)
                elif selector_type == 'css':
                    username_field = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"Found username field with {selector_type}: {selector}")
                break
            except:
                continue
        
        if not username_field:
            print("❌ Could not find username field")
            print("\nSearching for all input fields...")
            inputs = driver.find_elements(By.TAG_NAME, 'input')
            for i, inp in enumerate(inputs):
                print(f"  Input {i}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}")
            return None, None, "Username field not found"
        
        # Try to find password field
        password_selectors = [
            ('id', 'password'),
            ('id', 'Password'),
            ('id', 'pass'),
            ('name', 'password'),
            ('name', 'Password'),
            ('css', 'input[type="password"]'),
        ]
        
        password_field = None
        for selector_type, selector in password_selectors:
            try:
                if selector_type == 'id':
                    password_field = driver.find_element(By.ID, selector)
                elif selector_type == 'name':
                    password_field = driver.find_element(By.NAME, selector)
                elif selector_type == 'css':
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"Found password field with {selector_type}: {selector}")
                break
            except:
                continue
        
        if not password_field:
            print("❌ Could not find password field")
            return None, None, "Password field not found"
        
        # Fill in credentials
        print("\nFilling login form...")
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Find and click login button
        login_button_selectors = [
            ('id', 'submit'),
            ('id', 'login'),
            ('id', 'btnLogin'),
            ('css', 'button[type="submit"]'),
            ('css', 'input[type="submit"]'),
            ('css', 'button:contains("Belépés")'),
            ('xpath', '//button[contains(text(), "Belép")]'),
            ('xpath', '//input[@value="Belépés"]'),
        ]
        
        login_button = None
        for selector_type, selector in login_button_selectors:
            try:
                if selector_type == 'id':
                    login_button = driver.find_element(By.ID, selector)
                elif selector_type == 'css':
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                elif selector_type == 'xpath':
                    login_button = driver.find_element(By.XPATH, selector)
                
                print(f"Found login button: {selector_type} - '{selector}'")
                break
            except:
                continue
        
        if not login_button:
            print("❌ Could not find login button")
            print("\nSearching for all buttons...")
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            for i, btn in enumerate(buttons):
                print(f"  Button {i}: text={btn.text}, type={btn.get_attribute('type')}")
            
            # Try submitting the form directly
            print("\nTrying to submit form directly...")
            username_field.submit()
        else:
            print("Submitting login...")
            login_button.click()
        
        time.sleep(5)
        
        print(f"\nAfter login - Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Save post-login page
        with open('alfa_after_login.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Post-login page saved to alfa_after_login.html")
        
        # Check if login was successful
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        print("\nPage text (first 1000 chars):")
        print(page_text[:1000])
        
        # Look for balance - specifically "Nyugdíjpénztári számlaegyenlege"
        balance_patterns = [
            r'Nyugdíjpénztári számlaegyenlege.*?([0-9\s]+)\s*HUF',
            r'számlaegyenlege.*?([0-9\s]+)\s*HUF',
            r'Az Ön egyenlege.*?([0-9\s]+)\s*HUF',
            r'egyenleg.*?([0-9\s]+)\s*HUF',
        ]
        
        balance = None
        balance_date = None
        
        for pattern in balance_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    balance_str = match.group(1).replace(' ', '').replace('\xa0', '').replace('\n', '')
                    balance = Decimal(balance_str)
                    print(f"✓ Found balance: {balance:,.0f} HUF (pattern: {pattern})")
                    
                    # Try to extract date from pattern like "(2025.12.01. napi árfolyam alapján)"
                    date_match = re.search(r'\((\d{4})\.(\d{2})\.(\d{2})\.\s*napi', page_text)
                    if date_match:
                        from datetime import date as dt
                        balance_date = dt(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
                        print(f"✓ Balance date: {balance_date}")
                    break
                except Exception as e:
                    print(f"  Failed to parse: {e}")
                    continue
        
        if balance:
            print(f"\n✅ SUCCESS!")
            print(f"Balance: {balance:,.0f} Ft")
            return balance, balance_date, None
        else:
            print("\n⚠ Login appears successful but couldn't find balance")
            print("Check alfa_after_login.html for manual inspection")
            return None, None, "Balance not found in page"
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, str(e)
    
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()


if __name__ == "__main__":
    print("Testing Alfa Voluntary Pension Fund portal automation")
    print("="*60)
    
    username = "12266379"
    password = "Mobilemobile01"
    
    balance, balance_date, error = test_alfa_pension_login(username, password, headless=False)
    
    if error:
        print(f"\n❌ FAILED: {error}")
    else:
        print(f"\n✅ SUCCESS!")
        print(f"Balance: {balance:,.0f} Ft")
