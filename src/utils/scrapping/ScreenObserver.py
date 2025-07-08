import time
import threading
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json
from datetime import datetime


class ScreenObserver:
    """
    A comprehensive observer that monitors URL changes and dialog appearances
    with automatic handling capabilities for Instagram
    """
    
    def __init__(self, driver, callback_function=None, log_level=logging.INFO):
        self.driver = driver
        self.callback_function = callback_function
        self.current_url = ""
        self.is_monitoring = False
        self.monitor_thread = None
        self.check_interval = 0.5  # Check every 500ms
        
        # Setup logging
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Dialog detection patterns
        self.dialog_patterns = {
            'instagram': {
                'login_required': [
                    "//div[contains(text(), 'Log in to continue')]",
                    "//div[contains(text(), 'You must log in to continue')]",
                    "//button[contains(text(), 'Log In')]",
                ],
                'cookies_consent': [
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'Allow')]",
                    "//div[contains(text(), 'cookies')]//button",
                    "//button[contains(text(), 'Accept All')]"
                ],
                'notification_popup': [
                    "//div[contains(text(), 'notifications')]",
                    "//button[contains(text(), 'Not Now')]",
                ],
                'save_info_onetap': [
                    "//button[contains(text(), 'Save Info')]",
                    "//button[contains(text(), 'Not Now')]",
                ],
                'age_verification': [
                    "//button[contains(text(), 'I am 18 or older')]",
                    "//button[contains(text(), 'Continue')]",
                    "//select[@name='birthday_month']"
                ],
                'rate_limit': [
                    "//div[contains(text(), 'Try again later')]",
                    "//div[contains(text(), 'Please wait')]",
                    "//div[contains(text(), 'temporary')]",
                    "//div[contains(text(), 'blocked')]"
                ],
                'captcha': [
                    "//div[contains(text(), 'security check')]",
                    "//div[contains(text(), 'verification')]",
                    "//iframe[contains(@src, 'recaptcha')]",
                    "//div[@class='g-recaptcha']"
                ],
                'suspicious_activity': [
                    "//div[contains(text(), 'suspicious activity')]",
                    "//div[contains(text(), 'unusual activity')]",
                    "//button[contains(text(), 'This Was Me')]"
                ],
                'account_suspended': [
                    "//div[contains(text(), 'account has been')]",
                    "//div[contains(text(), 'suspended')]",
                    "//div[contains(text(), 'disabled')]"
                ],
                'challenge_required': [
                    "//div[contains(text(), 'challenge')]",
                    "//div[contains(text(), 'verify')]",
                    "//div[contains(text(), 'confirm')]",
                    "//input[@name='email']",
                    "//input[@name='phone']"
                ]
            },
            'general': {
                'popup_modal': [
                    "//div[@role='dialog']",
                    "//div[contains(@class, 'modal')]",
                    "//div[contains(@class, 'popup')]"
                ],
                'close_buttons': [
                    "//button[@aria-label='Close']",
                    "//button[contains(@class, 'close')]",
                    "//span[contains(@class, 'close')]",
                    "//button[text()='×']"
                ],
                'overlay': [
                    "//div[contains(@class, 'overlay')]",
                    "//div[contains(@class, 'backdrop')]"
                ]
            }
        }
        
        # Action handlers for different dialog types
        self.action_handlers = {
            'login_required': self.handle_login_required,
            'cookies_consent': self.handle_cookies_consent,
            'notification_popup': self.handle_notification_popup,
            'save_info_onetap': self.handle_save_info_onetap,
            'age_verification': self.handle_age_verification,
            'rate_limit': self.handle_rate_limit,
            'captcha': self.handle_captcha,
            'suspicious_activity': self.handle_suspicious_activity,
            'account_suspended': self.handle_account_suspended,
            'challenge_required': self.handle_challenge_required,
            'popup_modal': self.handle_generic_popup,
            'close_buttons': self.handle_close_buttons,
            'overlay': self.handle_overlay
        }
        
        # URL change handlers
        self.url_change_handlers = {
            'blocked_page': self.handle_blocked_page,
            'error_page': self.handle_error_page,
            'onetap_save_info': self.handle_onetap_save_info,
            'challenge_redirect': self.handle_challenge_redirect
        }
        
        # Initialize current URL
        try:
            self.current_url = self.driver.current_url
        except:
            self.current_url = ""
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Screen monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("Screen monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Check for URL changes
                self._check_url_changes()
                
                # Check for dialogs
                self._check_dialogs()
                
                # Sleep before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)  # Wait longer on error
    
    def _check_url_changes(self):
        """Check for URL changes and handle them"""
        try:
            new_url = self.driver.current_url
            
            if new_url != self.current_url:
                self.logger.info(f"URL changed: {self.current_url} -> {new_url}")
                
                # Handle specific URL patterns
                self._handle_url_change(self.current_url, new_url)
                
                # Update current URL
                self.current_url = new_url
                
                # Call callback if provided
                if self.callback_function:
                    self.callback_function('url_change', {
                        'old_url': self.current_url,
                        'new_url': new_url,
                        'timestamp': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            self.logger.error(f"Error checking URL changes: {e}")
    
    def _check_dialogs(self):
        """Check for dialogs and handle them"""
        try:
            # Check Instagram-specific dialogs first
            for dialog_type, patterns in self.dialog_patterns['instagram'].items():
                if self._detect_dialog(patterns):
                    self.logger.info(f"Detected dialog: {dialog_type}")
                    success = self._handle_dialog(dialog_type)
                    
                    if not success:
                        self.logger.warning(f"Failed to handle dialog: {dialog_type}")
                        self._request_manual_intervention(dialog_type, patterns)
                    
                    return  # Handle one dialog at a time
            
            # Check general dialogs
            for dialog_type, patterns in self.dialog_patterns['general'].items():
                if self._detect_dialog(patterns):
                    self.logger.info(f"Detected general dialog: {dialog_type}")
                    success = self._handle_dialog(dialog_type)
                    
                    if not success:
                        self.logger.warning(f"Failed to handle general dialog: {dialog_type}")
                        self._request_manual_intervention(dialog_type, patterns)
                    
                    return
                    
        except Exception as e:
            self.logger.error(f"Error checking dialogs: {e}")
    
    def _detect_dialog(self, patterns):
        """Detect if any dialog pattern is present"""
        for pattern in patterns:
            try:
                element = self.driver.find_element(By.XPATH, pattern)
                if element.is_displayed():
                    return True
            except (NoSuchElementException, TimeoutException):
                continue
        return False
    
    def _handle_dialog(self, dialog_type):
        """Handle detected dialog using appropriate handler"""
        if dialog_type in self.action_handlers:
            try:
                return self.action_handlers[dialog_type]()
            except Exception as e:
                self.logger.error(f"Error handling dialog {dialog_type}: {e}")
                return False
        return False
    
    def _handle_url_change(self, old_url, new_url):
        """Handle URL changes with specific patterns"""
        # Check for onetap save info page
        if 'accounts/onetap' in new_url:
            self.url_change_handlers['onetap_save_info'](old_url, new_url)
        
        # Check for challenge redirect (excluding two-factor)
        elif '/challenge' in new_url and 'two_factor' not in new_url:
            self.url_change_handlers['challenge_redirect'](old_url, new_url)
        
        # Check for blocked/error pages
        elif 'blocked' in new_url or 'error' in new_url or '404' in new_url:
            self.url_change_handlers['blocked_page'](old_url, new_url)
        
    
    def _request_manual_intervention(self, dialog_type, patterns):
        """Request manual intervention for unhandled dialogs"""
        error_msg = f"""
        MANUAL INTERVENTION REQUIRED!
        
        Dialog Type: {dialog_type}
        Timestamp: {datetime.now().isoformat()}
        Current URL: {self.driver.current_url}
        Patterns Detected: {patterns}
        
        Please manually resolve this dialog and continue.
        """
        
        self.logger.error(error_msg)
        
        # Call callback with error
        if self.callback_function:
            self.callback_function('manual_intervention', {
                'dialog_type': dialog_type,
                'patterns': patterns,
                'url': self.driver.current_url,
                'timestamp': datetime.now().isoformat(),
                'message': error_msg
            })
    
    # Dialog Handler Methods
    def handle_login_required(self):
        """Handle login required dialogs"""
        try:
            # Try to find and click login button
            login_selectors = [
                "//button[contains(text(), 'Log In')]",
                "//button[contains(text(), 'Sign In')]"
            ]
            
            for selector in login_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling login required: {e}")
            return False
    
    def handle_cookies_consent(self):
        """Handle cookies consent dialogs"""
        try:
            accept_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Allow')]",
                "//button[contains(text(), 'Accept All')]",
                "//button[contains(text(), 'OK')]"
            ]
            
            for selector in accept_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling cookies consent: {e}")
            return False
    
    def handle_notification_popup(self):
        """Handle notification popups"""
        try:
            dismiss_selectors = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Maybe Later')]",
                "//button[contains(text(), 'Cancel')]",
                "//button[@aria-label='Close']",
                "//button[contains(text(), 'No Thanks')]"
            ]
            
            for selector in dismiss_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling notification popup: {e}")
            return False
    
    def handle_save_info_onetap(self):
        """Handle save info dialog at accounts/onetap"""
        try:
            # Look for button inside main[role='main']
            button_selector = "//main[@role='main']//button[@type='button']"
            
            element = self.driver.find_element(By.XPATH, button_selector)
            if element.is_displayed():
                element.click()
                time.sleep(1)
                self.logger.info("Successfully clicked save info button at onetap")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling save info onetap: {e}")
            return False
    
    def handle_age_verification(self):
        """Handle age verification dialogs"""
        try:
            # This typically requires manual intervention
            self.logger.warning("Age verification detected - requires manual intervention")
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling age verification: {e}")
            return False
    
    def handle_rate_limit(self):
        """Handle rate limit dialogs"""
        try:
            self.logger.warning("Rate limit detected - waiting and retrying")
            time.sleep(60)  # Wait 1 minute
            
            # Try to refresh the page
            self.driver.refresh()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling rate limit: {e}")
            return False
    
    def handle_captcha(self):
        """Handle CAPTCHA dialogs"""
        try:
            self.logger.warning("CAPTCHA detected - requires manual intervention")
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling CAPTCHA: {e}")
            return False
    
    def handle_suspicious_activity(self):
        """Handle suspicious activity dialogs"""
        try:
            # Try to click "This Was Me" button
            confirm_selectors = [
                "//button[contains(text(), 'This Was Me')]",
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Confirm')]"
            ]
            
            for selector in confirm_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling suspicious activity: {e}")
            return False
    
    def handle_account_suspended(self):
        """Handle account suspended dialogs"""
        try:
            self.logger.error("Account suspended - requires manual intervention")
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling account suspended: {e}")
            return False
    
    def handle_challenge_required(self):
        """Handle challenge required dialogs (excluding two-factor)"""
        try:
            self.logger.warning("Challenge required detected - this will be handled by your scripts")
            
            # Don't attempt to handle automatically since you mentioned 
            # you'll handle challenges in your scripts
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling challenge required: {e}")
            return False
    
    def handle_generic_popup(self):
        """Handle generic popup dialogs"""
        try:
            # Try to find and click close button
            close_selectors = [
                "//button[@aria-label='Close']",
                "//button[contains(@class, 'close')]",
                "//span[contains(@class, 'close')]",
                "//button[text()='×']"
            ]
            
            for selector in close_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            # Try pressing ESC key
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling generic popup: {e}")
            return False
    
    def handle_close_buttons(self):
        """Handle close buttons"""
        return self.handle_generic_popup()
    
    def handle_overlay(self):
        """Handle overlay dialogs"""
        try:
            # Try clicking on overlay to dismiss
            overlay_selectors = [
                "//div[contains(@class, 'overlay')]",
                "//div[contains(@class, 'backdrop')]"
            ]
            
            for selector in overlay_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        element.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling overlay: {e}")
            return False
    
    # URL Change Handlers
    
    def handle_onetap_save_info(self, old_url, new_url):
        """Handle onetap save info page redirect"""
        self.logger.info(f"Onetap save info page detected: {old_url} -> {new_url}")
        # The dialog handler will automatically handle the button click
        # Just log the event here
    
    def handle_challenge_redirect(self, old_url, new_url):
        """Handle challenge redirect (excluding two-factor)"""
        self.logger.warning(f"Challenge redirect detected: {old_url} -> {new_url}")
        self.logger.info("Challenge handling will be done by your scripts")
        
        # Call callback to notify about challenge
        if self.callback_function:
            self.callback_function('challenge_detected', {
                'old_url': old_url,
                'new_url': new_url,
                'timestamp': datetime.now().isoformat(),
                'message': 'Challenge detected - external handling required'
            })
    
    def handle_blocked_page(self, old_url, new_url):
        """Handle blocked page"""
        self.logger.warning(f"Blocked page detected: {old_url} -> {new_url}")
        # Try to go back or refresh
        try:
            self.driver.back()
            time.sleep(2)
        except:
            pass
    
    def handle_error_page(self, old_url, new_url):
        """Handle error page"""
        self.logger.warning(f"Error page detected: {old_url} -> {new_url}")
        # Try to refresh
        try:
            self.driver.refresh()
            time.sleep(3)
        except:
            pass
    


def callbackEventHandler(event_type, data):
    """Example callback function"""
    print(f"Observer Event: {event_type}")
    print(f"Data: {json.dumps(data, indent=2)}")
