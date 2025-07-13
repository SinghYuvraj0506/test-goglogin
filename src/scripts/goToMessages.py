import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.scrapping.HumanMouseBehavior import HumanMouseBehavior
from utils.scrapping.HumanTypingBehavior import HumanTypingBehavior
from utils.scrapping.BasicUtils import BasicUtils
from selenium.webdriver.common.keys import Keys

def search_and_message_users(driver, usernames_list, message_text, delay_between_messages=(30, 50)):
    """
    Search for usernames and send messages to them if available.
    
    Args:
        driver: Selenium WebDriver instance
        usernames_list: List of usernames to search for
        message_text: Message to send to each user
        delay_between_messages: Tuple of (min, max) seconds to wait between messages
    """
    human_mouse = HumanMouseBehavior(driver)
    human_typing = HumanTypingBehavior(driver)
    basicUtils = BasicUtils(driver)
    
    successful_messages = []
    failed_users = []

    # Go to Instagram home
    driver.get("https://www.instagram.com/")
    time.sleep(5)

    basicUtils.click_anchor_by_href("/direct/inbox/")

    # Check if we're on a valid user profile
    try:
        WebDriverWait(driver, 8).until(
                        EC.url_contains("/direct/inbox/")
                    )
    except TimeoutException:
        raise Exception("Page not clicked")
    
    print(f"🔍 Starting to search and message {len(usernames_list)} users...")

    time.sleep(4)

    for i, username in enumerate(usernames_list):
        print(f"\n📝 Processing user {i+1}/{len(usernames_list)}: @{username}")
        
        try:
            # Search for the username
            if search_user(driver, username, human_mouse, human_typing):
                print(f"✅ User @{username} found!")
                
                # Try to send message
                if send_message_to_user(driver, username, message_text, human_mouse, human_typing):
                    successful_messages.append(username)
                    print(f"✅ Message sent to @{username}")
                else:
                    failed_users.append(f"{username} (message failed)")
                    print(f"❌ Failed to send message to @{username}")
            else:
                failed_users.append(f"{username} (not found)")
                print(f"❌ User @{username} not found, skipping...")
                
        except Exception as e:
            failed_users.append(f"{username} (error: {str(e)})")
            print(f"❌ Error processing @{username}: {str(e)}")
        
        # Random delay between messages to avoid rate limiting
        if i < len(usernames_list) - 1:  # Don't wait after the last user
            delay = random.randint(delay_between_messages[0], delay_between_messages[1])
            print(f"⏱️ Waiting {delay} seconds before next user...")
            time.sleep(delay)
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"✅ Successfully messaged: {len(successful_messages)} users")
    print(f"❌ Failed/Not found: {len(failed_users)} users")
    
    if successful_messages:
        print(f"✅ Successful messages sent to: {', '.join(successful_messages)}")
    
    if failed_users:
        print(f"❌ Failed users: {', '.join(failed_users)}")
    
    return successful_messages, failed_users


def search_user(driver, username: str, human_mouse: HumanMouseBehavior, human_typing: HumanTypingBehavior):
    """
    Search for a specific username on Instagram.
    
    Args:
        driver: Selenium WebDriver instance
        username: Username to search for
        human_mouse: HumanMouseBehavior instance
        human_typing: HumanTypingBehavior instance
    
    Returns:
        bool: True if user found, False otherwise
    """
    try:
        time.sleep(2)

        # Click back if previous text exists
        back_button = (By.CSS_SELECTOR, "svg[aria-label='Back']")
        try:
            human_mouse.human_like_move_to_element(back_button, click=True)
            time.sleep(1.5)
        except Exception:
            pass  # No back button = no problem


        # Click search bar
        search_input = (By.CSS_SELECTOR, "input[placeholder*='Search']")
        human_mouse.human_like_move_to_element(search_input, click=True)
        human_typing.human_like_type(search_input, text=username, clear_field=True)
        time.sleep(2.5)


        try:
            # Wait for search results to appear and find the exact user
            user_result = (By.XPATH, f"//span[contains(text(),'{username}')]")
            human_mouse.human_like_move_to_element(user_result, click=True)
            time.sleep(5)

            # Check if we're on a valid user profile
            # for headless it repaints the page faster
            driver.get_screenshot_as_png()

            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, f"//a[@href='/{username}/' and @role='link']"))
                )
                return True
            except TimeoutException:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f"//span[contains(text(),'{username} · Instagram')]"))
                    )
                    return True
                except TimeoutException:
                    return False                    

        except TimeoutException:
            print(f"⚠️ No exact match found for @{username}")
            return False

    except Exception as e:
        print(f"❌ Error searching for @{username}: {str(e)}")
        return False
    

def send_message_to_user(driver, username, message_text, human_mouse:HumanMouseBehavior,  human_typing: HumanTypingBehavior):
    """
    Send a message to a user from their profile page.
    
    Args:
        driver: Selenium WebDriver instance
        username: Username to send message to
        message_text: Message content
        basicUtils: BasicUtils instance
        human_mouse: HumanMouseBehavior instance
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        # Find message input field
        message_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
        )
        human_mouse.human_like_move_to_element(message_input, click=True)
        human_typing.human_like_type(message_input, message_text)
        time.sleep(5)
        
        message_input.send_keys(Keys.RETURN)
        return True
            
    except Exception as e:
        print(f"❌ Error sending message to @{username}: {str(e)}")
        return False


def message_users_from_list(driver, usernames_list, message_text, delay_range=(30, 60)):
    """
    Main function to search and message a list of users.
    
    Args:
        driver: Selenium WebDriver instance
        usernames_list: List of usernames to message
        message_text: Message to send
        delay_range: Tuple of (min, max) seconds between messages
    
    Returns:
        tuple: (successful_messages, failed_users)
    """
    print("🚀 Starting Instagram messaging automation...")
    
    # Validate inputs
    if not usernames_list:
        print("❌ No usernames provided!")
        return [], []
    
    if not message_text.strip():
        print("❌ No message text provided!")
        return [], []
    
    # Remove duplicates and clean usernames
    clean_usernames = list(set([username.strip().replace('@', '') for username in usernames_list if username.strip()]))
    
    print(f"📝 Processing {len(clean_usernames)} unique usernames...")
    print(f"💬 Message: {message_text}")
    
    return search_and_message_users(driver, clean_usernames, message_text, delay_range)

