import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from utils.scrappingHelpers import simulate_human_scrolling
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def browse_explore_page(driver):
    print("🧭 Navigating to Instagram Explore Page...")
    driver.get("https://www.instagram.com/explore/")
    time.sleep(4)

    # Step 1: Simulate human scrolling on explore
    simulate_human_scrolling(driver, scroll_count=random.randint(4, 7), scroll_distance=500, scroll_pause=2)

    try:
        # Step 2: Find post links
        # Find the main content area
        main_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main[role='main']"))
        )

        post_links = main_element.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        print(f"🖼️ Found {len(post_links)} explore posts.")

        # Step 3: Pick random 2–5 to view
        to_view = random.sample(post_links, min(len(post_links), random.randint(2, 5)))

        for i, post in enumerate(to_view):
            try:
                print(f"\n🔍 Opening post {i+1}/{len(to_view)}")

                # Scroll the post into view
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post)
                time.sleep(random.uniform(0.5, 1.5))

                # Click to open
                post.click()
                time.sleep(random.uniform(3.5, 6.5))  # Simulate reading/viewing

                print("🔙 Going back to explore")
                driver.back()
                time.sleep(random.uniform(2.5, 4))

                # Scroll again after viewing a post
                simulate_human_scrolling(driver, scroll_count=random.randint(1, 3), scroll_distance=400, scroll_pause=1.5)

            except Exception as e:
                print(f"⚠️ Failed to open/view post: {e}")
                driver.back()
                time.sleep(2)

    except NoSuchElementException:
        print("❌ No posts found on explore page.")

    print("🏠 Returning to Instagram home page.")
    driver.get("https://www.instagram.com/")
    time.sleep(3)
