from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from gologin import GoLogin
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.exploreReel import explore_reels_randomly
from scripts.browseExplore import browse_explore_page
from utils.basicHelpers import get_ip_proxy


def main():
    driver = None
    gologin = None
    
    try:
        print("🚀 Starting Instagram automation...")
        
        params = {
            'token': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODUzMDNhMGUyNDczOGUyOGVjOWNhZWEiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2ODZiNDg2ODg0YTEzYjdkOTUxNWFkODkifQ.CefiYpRiCocixtheKySboexl-q8lSPe63r45BTN1Y30",
            'extra_params': [
                # '--headless=new',
                '--no-sandbox', 
                '--disable-dev-shm-usage',
                # '--disable-gpu',
                # '--disable-background-timer-throttling',
                # '--disable-backgrounding-occluded-windows',
                # '--disable-renderer-backgrounding',
                # '--disable-features=TranslateUI',
                # '--disable-ipc-flooding-protection',
                # '--window-size=1920,1080',
                # '--remote-debugging-port=0'
            ]
        }
        
        print("🔧 Initializing GoLogin...")
        gologin = GoLogin(params)
        profile_id = "687a70de4e313015a3383efe"
        gologin.setProfileId(profile_id)
        
        print("🌐 Starting GoLogin profile...")
        try:
            debugger_address = gologin.start()
            print(f"🐛 Debugger Address: {debugger_address}")
            
            # Wait a moment for GoLogin to fully start
            time.sleep(3)
            
            # Test if the debugger address is accessible
            import requests
            try:
                test_url = f"http://{debugger_address}/json"
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    print("✅ Debugger address is accessible")
                else:
                    print(f"⚠️ Debugger address returned status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Could not verify debugger address: {e}")
                
        except Exception as e:
            print(f"❌ Error starting GoLogin: {e}")
            raise

        # Use pre-installed ChromeDriver instead of WebDriverManager
        chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/root/.wdm/drivers/chromedriver/linux64/137.0.7151.56')
        full_chromedriver_path = os.path.join(chromedriver_path, 'chromedriver')
        
        print(f"🔍 Looking for ChromeDriver at: {full_chromedriver_path}")
        
        if os.path.exists(full_chromedriver_path):
            print("✅ Using pre-installed ChromeDriver")
            service = Service(full_chromedriver_path)
        else:
            print("⚠️ Pre-installed ChromeDriver not found, using WebDriverManager")
            # Fallback to WebDriverManager but specify the version
            chromium_version = gologin.get_chromium_version()
            print(f"🔧 Chromium version from GoLogin: {chromium_version}")
            service = Service(ChromeDriverManager(driver_version=chromium_version).install())
        
        chrome_options = Options()
        
        # Try to connect to debugger address with validation
        if debugger_address and ":" in debugger_address:
            print(f"🔗 Attempting to connect to debugger: {debugger_address}")
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        else:
            print("⚠️ Invalid or missing debugger address, continuing without it")
        
        # Essential Chrome options for Docker environment
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-background-timer-throttling')
        # chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        # chrome_options.add_argument('--disable-renderer-backgrounding')
        # chrome_options.add_argument('--disable-features=TranslateUI')
        # chrome_options.add_argument('--disable-ipc-flooding-protection')
        # chrome_options.add_argument('--disable-extensions')
        # chrome_options.add_argument('--disable-default-apps')
        # chrome_options.add_argument('--disable-sync')
        # chrome_options.add_argument('--disable-translate')
        # chrome_options.add_argument('--hide-scrollbars')
        # chrome_options.add_argument('--mute-audio')
        # chrome_options.add_argument('--no-first-run')
        # chrome_options.add_argument('--disable-notifications')
        # chrome_options.add_argument('--disable-permissions-api')
        # chrome_options.add_argument('--disable-web-security')
        # chrome_options.add_argument('--allow-running-insecure-content')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--ignore-ssl-errors')
        # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        
        print("🚗 Creating Chrome driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("🌐 Checking proxy data...")
        get_ip_proxy(driver)
        time.sleep(2)

        print("📱 Navigating to Instagram...")
        driver.get("https://www.instagram.com/")
        print("✅ Instagram loaded")
        
        # Wait for page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Page body loaded")
        except Exception as e:
            print(f"⚠️ Timeout waiting for page load: {e}")

        time.sleep(3)
        
        # Scroll a bit
        driver.execute_script("window.scrollTo(0, 100);")
        time.sleep(2)

        print("📸 Taking screenshot...")
        screenshot_path = "/app/instagram_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot saved to {screenshot_path}")

        # Uncomment these when ready to test
        # try:
        #     print("🎬 Starting reel exploration...")
        #     explore_reels_randomly(driver)
        #     print("🔍 Browsing explore page...")
        #     browse_explore_page(driver)
        # except Exception as e:
        #     print(f"❌ Error in Instagram automation: {e}")

        print("⏳ Waiting 20 seconds before cleanup...")
        time.sleep(20)

    except Exception as e:
        print(f'❌ Main Error: {e}')
        import traceback
        print("📋 Full traceback:")
        traceback.print_exc()
        
    finally:
        print("🧹 Cleaning up...")
        try:
            if driver:
                driver.quit()
                print("✅ Chrome driver closed")
        except Exception as e:
            print(f"⚠️ Error closing driver: {e}")
            
        try:
            if gologin:
                gologin.stop()
                print("✅ GoLogin stopped")
        except Exception as e:
            print(f"⚠️ Error stopping GoLogin: {e}")
        
        print("✅ Cleanup completed")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ Fatal error: {e}')
        sys.exit(1)