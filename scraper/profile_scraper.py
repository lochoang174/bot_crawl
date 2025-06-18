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
from services.human_behavior import HumanBehaviorSimulator 
import json
from scraper.data_manager import DataManager
class LinkedInProfileScraper:
    """Scraper cho thông tin profile cá nhân"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
    
    def scrape_profile_details(self, profile_url: str) -> Dict:
        """Trích xuất thông tin chi tiết từ một profile"""
        print(f"\n🔍 Scraping: {profile_url}")
        self.driver.get(profile_url)
        HumanBehaviorSimulator.random_delay(5, 8)

        profile_data = {'url': profile_url}

        try:
            # Chờ cho container chính được tải
            main_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5"))
            )
            
            # Trích xuất thông tin
            profile_data['name'] = self._get_element_text(main_container, By.TAG_NAME, "h1")
            profile_data['headline'] = self._get_element_text(main_container, By.CSS_SELECTOR, "div.text-body-medium.break-words")
            profile_data['location'] = self._get_element_text(main_container, By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light.break-words")
            profile_data['current_company'] = self._get_element_text(main_container, By.XPATH, "//button[starts-with(@aria-label, 'Current company:')]//span[contains(@class, 'hoverable-link-text')]")
            profile_data['education'] = self._get_element_text(main_container, By.XPATH, "//button[starts-with(@aria-label, 'Education:')]//span[contains(@class, 'hoverable-link-text')]")
            
            print("  ✅ Đã trích xuất thông tin:")
            print(json.dumps(profile_data, indent=4, ensure_ascii=False))

        except TimeoutException:
            print(f"  ❌ Lỗi: Timeout khi chờ trang {profile_url} tải.")
            profile_data['error'] = 'Page load timeout'
        except Exception as e:
            print(f"  ❌ Lỗi không xác định khi scrape profile {profile_url}: {e}")
            profile_data['error'] = str(e)
            
        return profile_data
    
    def _get_element_text(self, container, by, value) -> Optional[str]:
        """Lấy text của element một cách an toàn"""
        try:
            if by == By.XPATH:
                return container.find_element(by, "." + value).text.strip()
            return container.find_element(by, value).text.strip()
        except NoSuchElementException:
            return None
    
    def get_all_profile_details(self, profiles_list: List[Dict]) -> List[Dict]:
        """Lấy thông tin chi tiết từ danh sách profiles"""
        all_profiles_data = []
        total_profiles = len(profiles_list)
        
        for i, profile in enumerate(profiles_list):
            print(f"\n{'='*20} [ Đang xử lý profile {i+1}/{total_profiles} ] {'='*20}")
            profile_url = profile['url']
            
            detailed_data = self.scrape_profile_details(profile_url)
            all_profiles_data.append(detailed_data)
            
            # Lưu backup sau mỗi 10 profiles
            if (i + 1) % 10 == 0 and i + 1 < total_profiles:
                print(f"\n--- Tự động lưu tiến trình sau {i+1} profiles ---")
                DataManager.save_profiles_to_file(all_profiles_data, "linkedin_detailed_profiles_backup.json")
                
        return all_profiles_data

