from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.twofactorCheck import handle_two_factor_authentication
from utils.scrappingHelpers import simulate_human_typing
from utils.helpers import get_config
from utils.blockHandlers import check_and_handle_dialogs, handle_save_info_dialog

def insta_login(driver):
    """
    Logs into Instagram using the provided Selenium driver.

    Args:
        driver: An instance of a Selenium WebDriver.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    try:
        # Step 1: Go to Instagram login page
        driver.get("https://www.instagram.com/?hl=en")

        # check for some dialogs
        check_and_handle_dialogs(driver)

        # Use WebDriverWait to wait for elements to be present
        wait = WebDriverWait(driver, 15)

        # Step 2: Fill in credentials from environment variables
        config = get_config()
        username = config.get("insta_username")
        password = config.get("insta_password")

        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        simulate_human_typing(username_input, username)
        simulate_human_typing(password_input, password)
        
        password_input.send_keys(Keys.RETURN)

        # Handle 2FA if required
        if not handle_two_factor_authentication(driver):
            return False
        
        # Handle Save info dialog
        if not handle_save_info_dialog(driver):
            return False
        
        # check for some dialogs
        check_and_handle_dialogs(driver)

        # Step 3: Wait for successful login and handle potential pop-ups
        # Wait for the home feed to load by checking for the profile icon
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/{}/']".format(username))))
        
        print("✅ Login successful!")

        return True

    except TimeoutException as e:
        print(f"❌ Error during login: A timeout occurred. The page might be slow to load or an element was not found in time.")
        print(f"Details: {e}")
        return False
    except NoSuchElementException as e:
        print(f"❌ Error during login: Could not find a required element on the page.")
        print(f"Details: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during login: {e}")
        return False


