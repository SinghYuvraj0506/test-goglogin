from utils.scrapping.ScreenObserver import ScreenObserver, callbackEventHandler
import time
from scripts.login import insta_login
from scripts.exploreReel import explore_reels_randomly
from scripts.browseExplore import browse_explore_page
from scripts.goToMessages import search_and_message_users
from utils.basicHelpers import get_ip_proxy
import logging
from selenium.webdriver.common.by import By
from gologinHandlers import GologinHandler

class MainExecutor:
    def __init__(self, profile_id: str = None):
        self.profile_id = profile_id
        self.logged_in = False  # Fixed typo: loggined -> logged_in
        self.gologin = None
        self.observer = None
        self.initialized = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    def initialize_session(self):
        """Initialize GoLogin session and driver"""
        try:
            self.logger.info(f"Initializing session for profile: {self.profile_id}")
            
            # Initialize GoLogin handler
            self.gologin = GologinHandler(
                profile_id=self.profile_id
            )

            self.gologin.connect_gologin_session()
            
            # Get driver from gologin handler
            self.driver = self.gologin.driver

            # Verify proxy
            get_ip_proxy(self.driver)
            
            # Start screen observer
            self.observer = ScreenObserver(self.driver, callback_function=callbackEventHandler)
            self.observer.start_monitoring()

            # Force initial revival
            self.observer.health_monitor.revive_driver("scroll")
            
            self.initialized = True
            self.logger.info("✅ Session initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize session: {e}")
            print(e)
            self.cleanup()
            return False


    def check_login_status(self):
        """Check if user is already logged into Instagram"""
        try:
            if not self.driver:
                return False
                
            # Navigate to Instagram if not already there
            if "instagram.com" not in self.driver.current_url:
                self.driver.get("https://www.instagram.com")
                time.sleep(3)
            
            try:
                self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Home']")
                self.logged_in = True
                self.logger.info("✅ User is already logged in")
                return True
            except:
                pass
            
            # Additional check: look for profile menu
            # try:
            #     self.driver.find_element("xpath", "//img[alt=contains(text(),'profile photo')]")
            #     self.logged_in = True
            #     self.logger.info("✅ User is already logged in (profile detected)")
            #     return True
            # except:
            #     pass
            
            self.logged_in = False
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            self.logged_in = False
            return False

    def perform_login(self):
        """Perform Instagram login and save cookies"""
        try:
            if self.check_login_status():
                self.logger.info("Already logged in, skipping login process")
                return True
            
            self.logger.info("Performing Instagram login...")
            
            # Perform login
            login_success = insta_login(self.driver)
            
            if login_success:
                time.sleep(3)  # Wait for login to complete
                
                # Verify login was successful
                if self.check_login_status():
                    self.logged_in = True
                    
                    # Save cookies after successful login
                    if self.save_cookies():
                        self.logger.info("✅ Login successful and cookies saved")
                        return True
                    else:
                        self.logger.warning("⚠️ Login successful but failed to save cookies")
                        return True  # Still return True as login worked
                else:
                    self.logger.error("❌ Login appears to have failed")
                    return False
            else:
                self.logger.error("❌ Login function returned failure")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login process failed: {e}")
            return False

    def save_cookies(self):
        """Save current cookies to GoLogin profile"""
        try:
            if not self.driver or not self.gologin:
                return False
            
            # Get current cookies
            cookies = self.driver.get_cookies()
            self.logger.info(f"Attempting to save {len(cookies)} cookies")
            
            # Filter Instagram cookies
            insta_cookies = [cookie for cookie in cookies if 'instagram.com' in cookie.get('domain', '')]
            self.logger.info(f"Found {len(insta_cookies)} Instagram-specific cookies")
            
            return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to save cookies: {e}")
            return False

    def run_activities(self):
        """Run Instagram activities"""
        try:
            if not self.logged_in:
                self.logger.error("Cannot run activities - not logged in")
                return False
            
            self.logger.info("Starting Instagram activities...")

            # self.driver.get("https://yuvrajsingh.info")
            # time.sleep(5)
            # print("✅DOne portfolio")
            
            # Run explore reels
            # explore_reels_randomly(self.driver, self.observer)
            # browse_explore_page(self.driver, self.observer)
            # view stories

            # account warmup
            
            # Uncomment for messaging
            search_and_message_users(
                self.driver, 
                usernames_list=["ssinghyuvraj02","anjali.singh960"],
                message_text="Hey bro whatsup ajsndn",
                observer=self.observer
            )

            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Activities failed: {e}")
            return False

    def execute(self):
        """Main execution method"""
        try:
            # Initialize session
            if not self.initialize_session():
                return False
            
            time.sleep(4)

            # Handle login
            if not self.perform_login():
                return False
            
            time.sleep(5)
            
            # Run activities
            self.run_activities()

            time.sleep(20)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Execution failed: {e}")
            return False
        # finally:
            # self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        try:
            self.logger.info("Cleaning up resources...")
            
            # Save cookies before cleanup
            if self.logged_in and self.driver and self.gologin:
                try:
                    self.save_cookies()
                except Exception as e:
                    self.logger.error(f"Failed to save cookies during cleanup: {e}")
            
            # Stop observer
            if self.observer:
                try:
                    self.observer.stop_monitoring()
                    self.logger.info("✅ Observer stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping observer: {e}")
            
            # Stop GoLogin session
            if self.gologin:
                try:
                    self.gologin.stop_gologin_session()
                    self.logger.info("✅ GoLogin session stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping GoLogin session: {e}")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

