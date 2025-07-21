import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from services.human_behavior import HumanBehaviorSimulator 
from typing import List, Dict, Optional

import json
import os
class LinkedInCompanyScraper:
    """Scraper cho thông tin công ty và nhân viên"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
    
    def click_show_more_button(self, timeout: int = 10) -> bool:
        """Tìm và click nút 'Show more results'"""
        try:
            show_more_button_xpath = "//button[.//span[normalize-space()='Show more results' or normalize-space()='Hiển thị thêm kết quả']]"
            print("🔍 Đang tìm nút 'Show more results'...")
            wait = WebDriverWait(self.driver, timeout)
            button = wait.until(
                EC.element_to_be_clickable((By.XPATH, show_more_button_xpath))
            )
            print("✅ Tìm thấy nút 'Show more results'.")
            try:
                ActionChains(self.driver).move_to_element(button).pause(0.5).click().perform()
                print("✅ Đã click nút bằng ActionChains.")
            except Exception:
                print("⚠️ ActionChains thất bại, thử click bằng JavaScript...")
                self.driver.execute_script("arguments[0].click();", button)
                print("✅ Đã click nút bằng JavaScript.")
            print("⏳ Đang chờ nội dung mới tải...")
            time.sleep(random.uniform(3, 5))
            return True
        except TimeoutException:
            print("❌ Không tìm thấy nút 'Show more results' hoặc nút không thể click trong thời gian chờ.")
            return False
        except Exception as e:
            print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")
            return False
    
    def expand_and_collect_all_urls(self, company_url: str) -> List[Dict]:
        """Mở rộng danh sách nhân viên và thu thập tất cả URL profile"""
        try:
            print(f"🌐 Truy cập trang people của công ty: {company_url}")
            self.driver.get(company_url)
            HumanBehaviorSimulator.random_delay(5, 8)
            
            print("\n🚀 Bắt đầu Giai đoạn 1: Mở rộng danh sách bằng cách click 'Show More'...")
            click_count = 0
            max_clicks = 99
            
            while click_count < max_clicks:
                was_button_clicked = self.click_show_more_button(timeout=7)
                if was_button_clicked:
                    click_count += 1
                    print(f"👍 Đã click 'Show More' lần thứ {click_count}.")
                    HumanBehaviorSimulator.random_delay(2, 4)
                else:
                    print("🏁 Hoàn tất mở rộng! Không còn nút 'Show More'.")
                    break
            
            if click_count >= max_clicks:
                print(f"⚠️ Đã đạt giới hạn {max_clicks} lần click.")

            print("\n🚀 Bắt đầu Giai đoạn 2: Thu thập tất cả profile URLs...")
            print("...cuộn trang để đảm bảo tất cả profiles đều được tải...")
            HumanBehaviorSimulator.scroll_to_bottom(self.driver)
            HumanBehaviorSimulator.random_delay(3, 5)

            return self._collect_profile_urls()

        except Exception as e:
            print(f"❌ Lỗi nghiêm trọng trong hàm expand_and_collect_all_urls: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _collect_profile_urls(self) -> List[Dict]:
        """Thu thập các URL profile từ trang"""
        try:
            profile_urls = []
            ul_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.display-flex.list-style-none.flex-wrap'))
            )
            a_tags = ul_element.find_elements(By.TAG_NAME, 'a')
            print(f"🔍 Tìm thấy tổng cộng {len(a_tags)} thẻ <a> sau khi mở rộng.")

            for a in a_tags:
                href = a.get_attribute("href")
                name_and_title = a.text.strip().replace('\n', ' ')
                if href and "/in/" in href and "linkedin.com" in href:
                    profile_urls.append({'url': href, 'text': name_and_title})

            # Loại bỏ duplicate
            seen_urls = set()
            unique_profiles = []
            for profile in profile_urls:
                if profile['url'] not in seen_urls:
                    seen_urls.add(profile['url'])
                    unique_profiles.append(profile)
            
            print(f"✅ Thu thập được {len(unique_profiles)} profile unique.")
            return unique_profiles

        except Exception as e:
            print(f"❌ Lỗi khi thu thập danh sách profile cuối cùng: {e}")
            return []


