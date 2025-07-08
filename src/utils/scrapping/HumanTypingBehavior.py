import random
import time
import string
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException


class HumanTypingBehavior:
    """
    A class to simulate human-like typing behavior with typos, pauses, and corrections
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.action_chains = ActionChains(driver)
        
        # Common typos mapping (adjacent keys on QWERTY keyboard)
        self.typo_mapping = {
            'a': ['s', 'q', 'w', 'z'],
            'b': ['v', 'g', 'h', 'n'],
            'c': ['x', 'd', 'f', 'v'],
            'd': ['s', 'e', 'r', 'f', 'c', 'x'],
            'e': ['w', 'r', 'd', 's'],
            'f': ['d', 'r', 't', 'g', 'v', 'c'],
            'g': ['f', 't', 'y', 'h', 'b', 'v'],
            'h': ['g', 'y', 'u', 'j', 'n', 'b'],
            'i': ['u', 'o', 'k', 'j'],
            'j': ['h', 'u', 'i', 'k', 'm', 'n'],
            'k': ['j', 'i', 'o', 'l', 'm'],
            'l': ['k', 'o', 'p'],
            'm': ['n', 'j', 'k'],
            'n': ['b', 'h', 'j', 'm'],
            'o': ['i', 'p', 'l', 'k'],
            'p': ['o', 'l'],
            'q': ['w', 'a', 's'],
            'r': ['e', 't', 'f', 'd'],
            's': ['a', 'w', 'e', 'd', 'x', 'z'],
            't': ['r', 'y', 'g', 'f'],
            'u': ['y', 'i', 'j', 'h'],
            'v': ['c', 'f', 'g', 'b'],
            'w': ['q', 'e', 's', 'a'],
            'x': ['z', 's', 'd', 'c'],
            'y': ['t', 'u', 'h', 'g'],
            'z': ['a', 's', 'x']
        }
        
        # Common typing patterns
        self.fast_sequences = ['the', 'and', 'that', 'for', 'you', 'not', 'but', 'can', 'out', 'get']
        self.slow_sequences = ['@', '#', '$', '%', '&', '*', '(', ')', '_', '+', '=', '{', '}', '[', ']']
        

    def get_typing_speed(self, char, previous_char=None):
        """
        Get realistic typing speed based on character and context
        """
        base_speed = random.uniform(0.08, 0.25)  # Base typing speed
        
        # Adjust speed based on character type
        if char.isalpha():
            # Common letter combinations are typed faster
            if previous_char and (previous_char + char).lower() in ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'ha', 'to']:
                base_speed *= 0.6
            # Vowels after consonants are typically faster
            elif previous_char and previous_char.lower() in 'bcdfghjklmnpqrstvwxyz' and char.lower() in 'aeiou':
                base_speed *= 0.8
        elif char.isdigit():
            base_speed *= 1.2  # Numbers are typically slower
        elif char in self.slow_sequences:
            base_speed *= 1.8  # Special characters are much slower
        elif char == ' ':
            base_speed *= 0.7  # Spaces are quick
        
        return base_speed
    

    def should_make_typo(self, char, position, text_length):
        """
        Determine if a typo should be made based on various factors
        """
        # Base typo probability (2-8%)
        base_prob = random.uniform(0.02, 0.08)
        
        # Increase probability based on position (middle of text has more typos)
        if 0.2 < position / text_length < 0.8:
            base_prob *= 1.3
        
        # Decrease probability for common sequences
        if char.lower() in 'aeiou' or char == ' ':
            base_prob *= 0.6
        
        # Increase probability for less common characters
        if char in string.punctuation or char.isdigit():
            base_prob *= 1.5
        
        return random.random() < base_prob
    

    def get_typo_char(self, intended_char):
        """
        Get a realistic typo character based on keyboard layout
        """
        char_lower = intended_char.lower()
        
        if char_lower in self.typo_mapping:
            # 80% chance to use adjacent key typo
            if random.random() < 0.8:
                return random.choice(self.typo_mapping[char_lower])
            else:
                # 20% chance for other types of typos
                typo_type = random.choice(['double', 'skip', 'case'])
                if typo_type == 'double':
                    return intended_char + intended_char
                elif typo_type == 'skip':
                    return ''  # Skip the character
                elif typo_type == 'case':
                    return intended_char.swapcase()
        
        # Default random typo
        return random.choice(string.ascii_lowercase)
    

    def should_pause(self, position, text_length):
        """
        Determine if typing should pause (thinking/reading)
        """
        # Base pause probability
        base_prob = 0.05
        
        # Increase probability at certain positions
        if position / text_length in [0.25, 0.5, 0.75]:  # Quarter, half, three-quarter points
            base_prob *= 3
        
        # Increase probability after punctuation
        return random.random() < base_prob
    
    def human_like_type(self, element, text, clear_field=True, typing_speed='normal'):
        """
        Type text into element with human-like behavior
        
        Args:
            element: WebElement to type into
            text: Text to type
            clear_field: Whether to clear the field first
            typing_speed: 'slow', 'normal', or 'fast'
        
        Returns:
            bool: Success status
        """
        try:
            # Wait for element to be present and clickable
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(EC.element_to_be_clickable(element))
            
            # Click on the element first
            element.click()
            time.sleep(random.uniform(0.1, 0.3))
            
            # Clear field if requested
            if clear_field:
                element.clear()
                time.sleep(random.uniform(0.05, 0.15))
            
            # Adjust base typing speed
            speed_multipliers = {
                'slow': 1.5,
                'normal': 1.0,
                'fast': 0.6
            }
            speed_multiplier = speed_multipliers.get(typing_speed, 1.0)
            
            typed_text = ""
            i = 0
            
            while i < len(text):
                char = text[i]
                previous_char = typed_text[-1] if typed_text else None
                
                # Determine if we should make a typo
                if self.should_make_typo(char, i, len(text)):
                    # Make a typo
                    typo_char = self.get_typo_char(char)
                    
                    if typo_char:  # If not empty (skip typo)
                        # Type the typo
                        element.send_keys(typo_char)
                        typed_text += typo_char
                        
                        # Pause before realizing mistake
                        correction_delay = random.uniform(0.3, 1.2)
                        time.sleep(correction_delay)
                        
                        # Correct the typo
                        if len(typo_char) > 1:  # Double character typo
                            element.send_keys(Keys.BACKSPACE * len(typo_char))
                            typed_text = typed_text[:-len(typo_char)]
                        else:
                            element.send_keys(Keys.BACKSPACE)
                            typed_text = typed_text[:-1]
                        
                        # Small pause after correction
                        time.sleep(random.uniform(0.1, 0.3))
                
                # Type the correct character
                element.send_keys(char)
                typed_text += char
                
                # Calculate typing delay
                typing_delay = self.get_typing_speed(char, previous_char) * speed_multiplier
                
                # Add some random variation
                typing_delay += random.uniform(-0.02, 0.02)
                
                # Ensure minimum delay
                typing_delay = max(0.01, typing_delay)
                
                time.sleep(typing_delay)
                
                # Random pauses (thinking/reading)
                if self.should_pause(i, len(text)):
                    pause_duration = random.uniform(0.5, 2.0)
                    time.sleep(pause_duration)
                
                i += 1
            
            # Final pause after typing
            time.sleep(random.uniform(0.2, 0.8))
            
            return True
            
        except (TimeoutException, ElementNotInteractableException) as e:
            print(f"Error typing into element: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while typing: {e}")
            return False
    

    def simulate_form_filling(self, form_data, delay_between_fields=None):
        """
        Fill multiple form fields with human-like behavior
        
        Args:
            form_data: Dictionary with element locators and text values
            delay_between_fields: Delay between filling fields
        """
        for locator, text in form_data.items():
            try:
                # Find the element
                if isinstance(locator, tuple):
                    element = self.driver.find_element(*locator)
                else:
                    element = locator  # Assume it's already a WebElement
                
                # Type with human behavior
                success = self.human_like_type(element, text)
                
                if success:
                    # Random delay between fields
                    if delay_between_fields is None:
                        delay = random.uniform(0.5, 2.0)
                    else:
                        delay = delay_between_fields
                    
                    time.sleep(delay)
                else:
                    print(f"Failed to type into field: {locator}")
                    
            except Exception as e:
                print(f"Error filling form field {locator}: {e}")
    

    def simulate_search_behavior(self, search_element, query, submit=True):
        """
        Simulate realistic search behavior with partial typing and corrections
        
        Args:
            search_element: Search input element
            query: Search query to type
            submit: Whether to submit the search
        """
        # Sometimes start typing something else first (simulation of changing mind)
        if random.random() < 0.3:  # 30% chance
            false_start = random.choice(['face', 'inst', 'what', 'how'])
            self.human_like_type(search_element, false_start, clear_field=False)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Clear and start over
            search_element.clear()
            time.sleep(random.uniform(0.2, 0.5))
        
        # Type the actual query
        self.human_like_type(search_element, query, clear_field=False)
        
        # Sometimes pause before submitting
        if submit:
            time.sleep(random.uniform(0.3, 1.0))
            search_element.send_keys(Keys.RETURN)


# # Usage example
# def example_usage():
#     """
#     Example of how to use the HumanTypingBehavior class
#     """
#     # Initialize your driver (replace with your gologin setup)
#     driver = webdriver.Chrome()  # or your gologin driver
    
#     try:
#         # Navigate to Instagram
#         driver.get("https://www.instagram.com")
        
#         # Initialize human typing behavior
#         human_typing = HumanTypingBehavior(driver)
        
#         # Example 1: Type into username field
#         username_field = driver.find_element(By.NAME, "username")
#         human_typing.human_like_type(username_field, "your_username", typing_speed='normal')
        
#         # Example 2: Type into password field
#         password_field = driver.find_element(By.NAME, "password")
#         human_typing.human_like_type(password_field, "your_password", typing_speed='slow')
        
#         # Example 3: Fill multiple form fields
#         form_data = {
#             (By.NAME, "username"): "test_user",
#             (By.NAME, "password"): "test_password"
#         }
#         human_typing.simulate_form_filling(form_data)
        
#         # Example 4: Search behavior
#         search_field = driver.find_element(By.XPATH, "//input[@placeholder='Search']")
#         human_typing.simulate_search_behavior(search_field, "nature photography")
        
#     finally:
#         driver.quit()


# if __name__ == "__main__":
#     example_usage()