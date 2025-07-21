from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from services.human_behavior import HumanBehaviorSimulator 
from typing import List, Dict, Optional, Callable
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from scraper.data_manager import DataManager
from repositories.url_repository import UrlRepository
from models.status_enum import UrlStatus
from proto import bot_pb2
import random
class LinkedInMyNetworkScraper:
    def __init__(self, driver, manager):
        self.driver = driver
        self.manager = manager # <-- This gives access to is_stopped()
        self.url_repository = UrlRepository()  # Initialize the UrlRepository
        
    
    def scroll_to_show_more(self, timeout: int = 10) -> bool:
        try:
            print("🔍 Đang cuộn trang")
         
            modal = self.driver.find_element(By.CSS_SELECTOR, "#root > dialog > div > div")

            HumanBehaviorSimulator.scroll_to_bottom_modal_show_all(self.driver, modal)
            HumanBehaviorSimulator.random_delay(1, 3)
            
            return True
        except TimeoutException:
            print("❌ Không tìm thấy nút 'Show more results' trong thời gian chờ.")
            return False
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")
            return False


    def click_show_all_button(self):
        try:
            print("🔍 Đang tìm nút 'Show all'...")
            yield bot_pb2.BotLog(
                            bot_id=1,
                            message="🔍 Đang tìm nút 'Show all'..."
                        )
            show_all_button = self.wait.until(
                lambda d: d.find_element(By.XPATH, "//button[.//span[normalize-space()='Show all']]")
            )
            print("✅ Tìm thấy nút 'Show all'.")
            self.driver.execute_script("arguments[0].scrollIntoView();", show_all_button)
            show_all_button.click()
            print("✅ Đã click nút 'Show all'.")
        except TimeoutException:
            print("❌ Không tìm thấy nút 'Show all' trong thời gian chờ.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click 'Show all': {e}")


    def expand_and_collect_all_urls(self, isStop: bool) -> list[str]:
        # --- 1. INITIALIZE A LIST TO HOLD URLS ---
        # The function will now collect URLs here and return this list.
        collected_urls = []

        try:
            print(f"[{self.manager.id}] 🌐 Navigating to 'My Network' page...")
            self.driver.get("https://www.linkedin.com/mynetwork/")
            HumanBehaviorSimulator.random_delay(5, 8)
            
            # --- 2. USE THE CORRECT STOP CHECK ---
            # Check the manager's stop event before starting heavy work.
            if self.manager.is_stopped(): 
                print(f"[{self.manager.id}] ⏹️ Halting before starting URL collection due to stop signal.")
                return collected_urls

            # Step 1: Scroll the main page to load content
            scroll_attempts = random.randint(5, 7)
            print(f"[{self.manager.id}] 🔍 Scrolling main page {scroll_attempts} times...")
            for i in range(scroll_attempts):
                if self.manager.is_stopped(): return collected_urls # Check in loops
                print(f"[{self.manager.id}] ...scroll {i+1}/{scroll_attempts}")
                HumanBehaviorSimulator.scroll_main_to_bottom(self.driver)
                HumanBehaviorSimulator.random_delay(1, 2)

            # Step 2: Find all "Show all" buttons
            print(f"[{self.manager.id}] 🔍 Finding all 'Show all' buttons...")
            show_all_buttons = self.driver.find_elements(By.XPATH, "//button[.//span[normalize-space()='Show all']]")
            print(f"[{self.manager.id}] ✅ Found {len(show_all_buttons)} 'Show all' buttons.")

            bot_counter = 1
            max_bot_counter = 4
            # Step 3: Iterate through each button
            for index, button in enumerate(show_all_buttons):
                # --- 2. USE THE CORRECT STOP CHECK (again) ---
                if self.manager.is_stopped():
                    print(f"[{self.manager.id}] ⏹️ Halting before processing button {index + 1} due to stop signal.")
                    return collected_urls

                try:
                    print(f"\n[{self.manager.id}] 🚀 Processing 'Show all' button #{index + 1}...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    HumanBehaviorSimulator.random_delay(1, 2)
                    button.click()
                    print(f"[{self.manager.id}] ✅ Clicked 'Show all' button.")

                    # This is the inner loop for scrolling the modal
                    while not self.manager.is_stopped():
                        # --- 3. SCROLL AND COLLECT ---
                        # The scroll_to_show_more and _collect_profile_urls should also be in this class
                        if not self.scroll_to_show_more(timeout=7):
                            print(f"[{self.manager.id}] 🏁 Reached the end of the modal list.")
                            break # Exit the modal scroll loop

                        # --- 4. COLLECT URLS, DON'T SAVE ---
                        # This helper now just returns URLs from the current view
                        new_urls_found = self._collect_profile_urls()
                        if not new_urls_found:
                            print(f"[{self.manager.id}] ❌ No new profile URLs found in this modal.")
                            break
                        
                        # Add only new URLs to our main list
                        newly_added_count = 0
                       
                        for url in new_urls_found:
                            print("🔗 Đang xử lý URL:", url)
                            created_profile = self.url_repository.create(url, status=UrlStatus.PENDING, bot_id=bot_counter)  
                            if created_profile:
                                print(f"✅ Đã lưu profile URL {url} vào MongoDB.")
                            
                            bot_counter = bot_counter + 1 if bot_counter < max_bot_counter else 1

                            if url not in collected_urls:
                                collected_urls.append(url)
                                
                                newly_added_count += 1
                        
                        if newly_added_count == 0:
                            print(f"[{self.manager.id}] ⏳ No new profiles found in this scroll. Closing modal.")
                            break
                        else:
                             print(f"[{self.manager.id}] 👍 Found {newly_added_count} new profiles. Total collected: {len(collected_urls)}")


                    # Close the modal
                    print(f"[{self.manager.id}] 🚪 Closing modal...")
                    close_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                    self.driver.execute_script("arguments[0].click();", close_button)
                    HumanBehaviorSimulator.random_delay(2, 3)

                except Exception as e:
                    print(f"[{self.manager.id}] ❌ Error processing 'Show all' button #{index + 1}: {e}")
                    # Try to close a modal if it's stuck open
                    try:
                        self.driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']").click()
                    except:
                        pass # Ignore if no close button is found
                    continue

            print(f"[{self.manager.id}] ✅ Finished processing all 'Show all' buttons.")
            
            # --- 5. RETURN THE COLLECTED LIST ---
            # The function now successfully returns the list of URLs for the next step.
            return collected_urls

        except Exception as e:
            print(f"[{self.manager.id}] ❌ A critical error occurred in expand_and_collect_all_urls: {e}")
            return collected_urls
        
    def _collect_profile_urls(self) -> List[str]:
        """
        Collect profile URLs from the modal and return them as a list of strings.
        """
        try:
            profile_urls = []

            # Directly find the grid items without waiting
            grid_items = self.driver.find_element(By.CSS_SELECTOR, "#root > dialog > div > div > div > div > section > div > div > div")
            a_tags = grid_items.find_elements(By.TAG_NAME, "a")  # Find all <a> tags immediately

            # Collect URLs from the <a> tags
            for a in a_tags:
                profile_url = a.get_attribute("href")
                if profile_url:
                    profile_urls.append(profile_url)  # Append only the URL string

            # Remove duplicates by converting to a set and back to a list
            profile_urls = list(set(profile_urls))
            print(f"🔍 Tìm thấy tổng cộng {len(profile_urls)} profile URLs.")
            return profile_urls

        except Exception as e:
            print(f"❌ Lỗi khi thu thập danh sách profile cuối cùng: {e}")
            return []
