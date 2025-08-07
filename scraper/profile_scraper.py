import queue
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from models.face_model import FaceVector
from proto import bot_pb2
from services.human_behavior import HumanBehaviorSimulator 
from typing import List, Dict, Optional
from services.human_behavior import HumanBehaviorSimulator 
import json
from scraper.data_manager import DataManager
from repositories.url_repository import UrlRepository
from repositories.profile_repository import ProfileRepository
from services.rabbitmq_client import RabbitMQClient
class LinkedInProfileScraper:
    """Scraper cho thông tin profile cá nhân"""
    
    def __init__(self, driver, manager):
        self.manager = manager  # Placeholder for manager instance
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.rabbit = RabbitMQClient()


    def scrape_profile_details(self, profile_url: str, url_repo: UrlRepository, profile_repo: ProfileRepository, log_queue: queue.Queue, bot_id: int) -> Dict:
        """
        Trích xuất thông tin chi tiết từ một profile và lưu vào database.
        """
        profile_data = {'url': profile_url}

        try:
            # Check for stop signal before starting
            if self.manager.is_stopped():
                print(f"[{self.manager.id}] ⏹️ Halting profile detail scraping due to stop signal.")
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⏹️ Halting profile detail scraping due to stop signal."))
                return profile_data

            # Update status to 'processing'
            url_repo.update_status_to_processing(profile_url)

            # Load the profile page
            self.driver.get(profile_url)
            HumanBehaviorSimulator.random_delay(5, 8)

            HumanBehaviorSimulator.scroll_to_bottom(self.driver, num_scrolls=random.randint(2, 5), scroll_delay_min=1, scroll_delay_max=3)
            HumanBehaviorSimulator.random_delay(2, 5) # Delay after scrolling

            # Check for stop signal after loading the page
            if self.manager.is_stopped():
                print(f"[{self.manager.id}] ⏹️ Halting profile detail scraping after loading page.")
                url_repo.update_status_to_pending(profile_url)
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⏹️ Halting profile detail scraping after loading page."))
                return profile_data

            # Extract profile details
            main_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5"))
            )
            profile_data['name'] = self._get_element_text(main_container, By.TAG_NAME, "h1")
            profile_data['headline'] = self._get_element_text(main_container, By.CSS_SELECTOR, "div.text-body-medium.break-words")
            profile_data['location'] = self._get_element_text(main_container, By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light.break-words")
            profile_data['current_company'] = self._get_element_text(main_container, By.XPATH, "//button[starts-with(@aria-label, 'Current company:')]//span[contains(@class, 'hoverable-link-text')]")
            profile_data['education'] = self._get_element_text(main_container, By.XPATH, "//button[starts-with(@aria-label, 'Education:')]//span[contains(@class, 'hoverable-link-text')]")
                
            try:
                avatar_img = self.driver.find_element(By.CSS_SELECTOR, "img.pv-top-card-profile-picture__image--show")
                profile_data['avatar_url'] = avatar_img.get_attribute("src")
            except NoSuchElementException:
                profile_data['avatar_url'] = None
                print("  ⚠️ Could not find avatar URL.")

                # Save profile details to the database (via RabbitMQ)
            face_vector = FaceVector(
                    url=profile_data.get('url'),
                    name=profile_data.get('name'),
                    headline=profile_data.get('headline'),
                    location=profile_data.get('location'),
                    current_company=profile_data.get('current_company'),
                    education=profile_data.get('education'),
                    vector=[], # Vector will be computed elsewhere
                    picture=profile_data.get('avatar_url'),
                )
                
            payload = {
                'pattern': 'create_face_vector',
                'data': face_vector.to_dict(),
            }
            self.rabbit.publish_message('face_queue', payload)
            print("  📤 Đã gửi message tới face_queue.")
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="📤 Đã gửi message tới face_queue."))

            # Update status to 'done'
            url_repo.update_status_to_done(profile_url)

            print("  ✅ Đã trích xuất và lưu thông tin profile:")
            print(json.dumps(profile_data, indent=4, ensure_ascii=False, default=str))
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ Đã trích xuất và lưu thông tin profile:"))
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=json.dumps(profile_data, indent=4, ensure_ascii=False, default=str)))

            return profile_data


        except TimeoutException:
            print(f"  ❌ Lỗi: Timeout khi chờ trang {profile_url} tải.")
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"❌ Lỗi: Timeout khi chờ trang {profile_url} tải."))
            profile_data['error'] = 'Page load timeout'
        except Exception as e:
            print(f"  ❌ Lỗi không xác định khi scrape profile {profile_url}: {e}")
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"❌ Lỗi không xác định khi scrape profile {profile_url}: {e}"))
            profile_data['error'] = str(e)
        finally:
            return profile_data
    
    def _get_element_text(self, container, by, value) -> Optional[str]:
        """Lấy text của element một cách an toàn"""
        try:
            if by == By.XPATH:
                return container.find_element(by, "." + value).text.strip()
            return container.find_element(by, value).text.strip()
        except NoSuchElementException:
            return None


    def get_all_profile_details(self, profiles_list: List[str], url_repo: UrlRepository, profile_repo: ProfileRepository, log_queue: queue.Queue, bot_id: int) -> List[Dict]:
        """
        Lấy thông tin chi tiết từ danh sách profile URLs theo từng batch ngẫu nhiên (20–30),
        nghỉ 2–3 phút sau batch đầu tiên và nghỉ 5–7 phút sau mỗi batch tiếp theo.
        """
        total_profiles = len(profiles_list)
        i = 0
        batch_count = 0

        while i < total_profiles:
            if self.manager.is_stopped():
                print(f"[{self.manager.id}] ⏹️ Halting profile scraping due to stop signal.")
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="⏹️ Halting profile scraping due to stop signal."))
                break

            # Determine random batch size (20 to 30)
            batch_size = 1
            batch_profiles = profiles_list[i:i+batch_size]

            print(f"\n🚀 Bắt đầu batch {batch_count + 1} với {len(batch_profiles)} profiles...")
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🚀 Bắt đầu batch {batch_count + 1} với {len(batch_profiles)} profiles..."))

            for j, profile_url in enumerate(batch_profiles):
                if self.manager.is_stopped():
                    print(f"[{self.manager.id}] ⏹️ Halting during batch {batch_count + 1}.")
                    url_repo.update_status_to_pending(profile_url)
                    log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⏹️ Halting during batch {batch_count + 1}."))
                    return

                print(f"\n{'='*20} [ Đang xử lý profile {i+j+1}/{total_profiles} ] {'='*20}")
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"Đang xử lý profile {i+j+1}/{total_profiles}"))
                print(f"🔗 URL: {profile_url}")
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🔗 URL: {profile_url}"))
                self.scrape_profile_details(profile_url, url_repo, profile_repo, log_queue, bot_id)

            batch_count += 1
            i += len(batch_profiles)

            if i >= total_profiles:
                print(f"✅ Đã hoàn thành việc scrape tất cả {total_profiles} profiles.")
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✅ Đã hoàn thành việc scrape tất cả {total_profiles} profiles."))
                break

            # Mimic human behavior during delay by accessing LinkedIn feed and scrolling
            print(f"\n⏳ Đang truy cập feed và cuộn để nghỉ trước batch tiếp theo...\n")
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="⏳ Đang truy cập feed và cuộn để nghỉ trước batch tiếp theo..."))
            self.driver.get("https://www.linkedin.com/feed/")
            start_time = time.time()
            scroll_direction = "down"  # Start by scrolling down
            last_scroll_position = 0

            while time.time() - start_time < random.uniform(30, 60):  # Scroll for 2–3 minutes
                if self.manager.is_stopped():
                    print(f"[{self.manager.id}] ⏹️ Halting during feed scrolling due to stop signal.")
                    log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="⏹️ Halting during feed scrolling due to stop signal."))
                    return

                current_scroll_position = self.driver.execute_script("return window.pageYOffset;")
                print(f"🔍 Current scroll position: {current_scroll_position}")
                

                # Randomize scroll distance and speed for slow scrolling
                scroll_distance = random.randint(200, 500)  # Smaller scroll distance for slower scrolling
                scroll_pause = random.uniform(3, 6)  # Longer pause between scrolls

                if scroll_direction == "down":
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")  # Scroll down
                    HumanBehaviorSimulator.random_delay(scroll_pause, scroll_pause + 2)  # Random delay
                    new_scroll_position = self.driver.execute_script("return window.pageYOffset;")
                    if new_scroll_position == current_scroll_position:  # Can't scroll down anymore
                        print("🔄 Reached the bottom, switching to scroll up.")
                        scroll_direction = "up"
                elif scroll_direction == "up":
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_distance});")  # Scroll up
                    HumanBehaviorSimulator.random_delay(scroll_pause, scroll_pause + 2)  # Random delay
                    new_scroll_position = self.driver.execute_script("return window.pageYOffset;")
                    if new_scroll_position == current_scroll_position:  # Can't scroll up anymore
                        print("🔄 Reached the top, switching to scroll down.")
                        scroll_direction = "down"

            print(f"\n✅ Đã hoàn thành việc cuộn feed. Tiếp tục batch tiếp theo...\n")
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ Đã hoàn thành việc cuộn feed. Tiếp tục batch tiếp theo..."))