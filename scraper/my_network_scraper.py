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
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
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


    def expand_and_collect_all_urls(self, stop: bool, bot_id: str = ""):
        try:
            # Log the start of the process
            yield bot_pb2.BotLog(
                bot_id=bot_id,
                message="🌐 Truy cập trang kết nối của bạn..."
            )
            print("🌐 Truy cập trang kết nối của bạn...")
            self.driver.get("https://www.linkedin.com/mynetwork")
            HumanBehaviorSimulator.random_delay(5, 8)

             # Step 1: Scroll a fixed number of times (5 to 7)
            scroll_attempts = random.randint(5, 7)
            print(f"🔍 Đang cuộn trang {scroll_attempts} lần...")
            for _ in range(scroll_attempts):
                HumanBehaviorSimulator.scroll_main_to_bottom(self.driver)
                HumanBehaviorSimulator.random_delay(1, 2)

            # Step 2: Save all "Show all" buttons into a dictionary
            print("🔍 Đang tìm tất cả các nút 'Show all'...")
            show_all_buttons = self.driver.find_elements(By.XPATH, "//button[.//span[normalize-space()='Show all']]")
            buttons_dict = {index: button for index, button in enumerate(show_all_buttons)}
            print(f"✅ Đã lưu {len(buttons_dict)} nút 'Show all' vào dictionary.")

            # Initialize the vm counter
            vm_counter = 1
            max_vm = 4

            # Step 3: Iterate through each "Show all" button and process it
            for index, button in buttons_dict.items():
                if stop:  # Check if stop is True
                    print("⏹️ Dừng quá trình xử lý các nút 'Show all' do yêu cầu dừng.")
                    return

                try:
                    print(f"\n🚀 Đang xử lý nút 'Show all' thứ {index + 1}...")
                    self.driver.execute_script("arguments[0].scrollIntoView();", button)
                    HumanBehaviorSimulator.random_delay(1, 2)
                    button.click()
                    print("✅ Đã click nút 'Show all'.")

                    # Scroll the modal and collect profile URLs
                    scroll_count = 0
                    last_profile_count = 0
                    same_count_duration = 0

                    while True:
                        print("Stop: "+stop)
                        if stop:  # Check if stop is True
                            print("⏹️ Dừng quá trình cuộn modal do yêu cầu dừng.")
                            return

                        if not self.scroll_to_show_more(timeout=7):
                            print("❌ Không thể cuộn thêm nữa.")
                            break
                        scroll_count += 1
                        print(f"👍 Đã scroll lần thứ {scroll_count}.")

                        # Collect profile URLs and save them to MongoDB
                        new_profile_urls = self._collect_profile_urls()
                        for profile in new_profile_urls:
                            
                            created_profile = self.url_repository.create(profile['url'], status=UrlStatus.PENDING, bot_id=vm_counter)
                            if created_profile:
                                print(f"✅ Đã lưu profile URL {profile['url']} vào MongoDB.")
                            
                            # Increment vm_counter and reset if it exceeds max_vm
                            vm_counter = vm_counter + 1 if vm_counter < max_vm else 1

                        # Check if profile count remains the same
                        if len(new_profile_urls) == last_profile_count:
                            same_count_duration += 1
                            if same_count_duration == 1:
                                print("⏳ Không có profile mới. Đóng modal và tiếp tục.")
                                break
                        else:
                            same_count_duration = 0
                            last_profile_count = len(new_profile_urls)

                    # Close the modal
                    close_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                    self.driver.execute_script("arguments[0].scrollIntoView();", close_button)
                    HumanBehaviorSimulator.random_delay(1, 2)
                    close_button.click()
                    print("✅ Đã đóng modal.")
                    HumanBehaviorSimulator.random_delay(2, 3)

                except Exception as e:
                    print(f"❌ Lỗi khi xử lý nút 'Show all' thứ {index + 1}: {e}")
                    continue

            print("✅ Hoàn thành việc xử lý tất cả các nút 'Show all'.")
            return []

        except Exception as e:
            yield bot_pb2.BotLog(
                bot_id=bot_id,
                message=f"❌ Lỗi trong quá trình mở rộng danh sách: {e}"
            )
            print(f"❌ Lỗi trong quá trình mở rộng danh sách: {e}")
            return []

    def _collect_profile_urls(self) -> List[Dict]:
        try:
            profile_urls = []

            # Directly find the grid items without waiting
            grid_items = self.driver.find_element(By.CSS_SELECTOR, "#root > dialog > div > div > div > div > section > div > div > div")
            a_tags = grid_items.find_elements(By.TAG_NAME, "a")  # Find all <a> tags immediately

            # Collect URLs from the <a> tags
            for a in a_tags:
                profile_url = a.get_attribute("href")
                if profile_url:
                    profile_urls.append({"url": profile_url})

            # Remove duplicates by converting to a dictionary and back to a list
            profile_urls = list({profile['url']: profile for profile in profile_urls}.values())
            print(f"🔍 Tìm thấy tổng cộng {len(profile_urls)} profile URLs.")
            return profile_urls

        except Exception as e:
            print(f"❌ Lỗi khi thu thập danh sách profile cuối cùng: {e}")
            return []
