import json
import random
import time
import threading # <-- ADD THIS IMPORT
from services.authen import LinkedInAuthenticator
from scraper.company_scraper import LinkedInCompanyScraper
from scraper.profile_scraper import LinkedInProfileScraper
from services.driver_management import ChromeDriverManager
from scraper.data_manager import DataManager
from typing import List, Dict
from scraper.my_network_scraper import LinkedInMyNetworkScraper
from services.human_behavior import HumanBehaviorSimulator 
from repositories.url_repository import UrlRepository
from repositories.profile_repository import ProfileRepository
from utils.read_cookie import read_cookie_file

class LinkedInScraperManager:
    """Class chính quản lý toàn bộ quá trình scraping"""
    
    def __init__(self, profile_name: str = "linkedin_profile", id: str = None):
        self.driver_manager = ChromeDriverManager(id, profile_name)
        self.driver = None
        self.authenticator = None
        self.company_scraper = None
        self.profile_scraper = None
        self.my_connect_scraper = None
        # self.search = None # You might want to initialize this to None too
        self.id = id
        
        # --- MODIFICATION: Use threading.Event for thread-safe signaling ---
        self._stop_event = threading.Event()
     
    def set_stop(self):
        """Sets the event to signal the thread to stop."""
        print(f"[{self.id}] 🔴 Stop signal received. Setting stop event.")
        self._stop_event.set()

    def is_stopped(self) -> bool:
        """Checks if the stop event has been set."""
        return self._stop_event.is_set()
    
    def reset_stop(self):
        """Resets the stop event to allow running again."""
        self._stop_event.clear()
        
    def initialize_driver(self) -> bool:
        """Khởi tạo driver và các scraper"""
        self.driver = self.driver_manager.create_edge_driver_with_session()
        self.driver.execute_script("window.open('https://bot.sannysoft.com', '_blank');")

            # ✅ Chuyển sang tab mới
        self.driver.switch_to.window(self.driver.window_handles[-1])
        if not self.driver:
            return False
        
        # --- MODIFICATION: Pass the manager instance 'self' to each sub-scraper ---
        # This allows them to check self.manager.is_stopped()
        self.authenticator = LinkedInAuthenticator(self.driver)
        # self.company_scraper = LinkedInCompanyScraper(self.driver, self)
        self.profile_scraper = LinkedInProfileScraper(self.driver, self)
        self.my_connect_scraper = LinkedInMyNetworkScraper(self.driver, self)
        return True
    
    def login(self) -> bool:
        """Đăng nhập LinkedIn"""
        if not self.authenticator:
            print("❌ Driver chưa được khởi tạo")
            return False
        return self.authenticator.smart_login()
    
    def scrape_company_profiles(self, company_url: str) -> List[Dict]:
        """Scrape tất cả profiles từ một công ty"""
        if self.is_stopped(): return []
        if not self.company_scraper:
            print("❌ Company scraper chưa được khởi tạo")
            return []
        
        # This method inside LinkedInCompanyScraper must be modified to check for the stop signal
        profile_urls = self.company_scraper.expand_and_collect_all_urls(company_url)
        if not profile_urls or self.is_stopped():
            return []
        
        DataManager.save_profiles_to_file(profile_urls, "collected_profile_urls.json")
        
        # This method inside LinkedInProfileScraper must also be modified
        detailed_profiles = self.profile_scraper.get_all_profile_details(profile_urls)
        
        if detailed_profiles:
            DataManager.save_profiles_to_file(detailed_profiles, "linkedin_detailed_profiles_final.json")
        
        return detailed_profiles
    
    def scrape_my_connect_profiles(self) -> List[Dict]:
        """
        Scrapes profiles from "My Network". This is now a clear, interruptible two-step process.
        """
        if self.is_stopped(): return []
        if not self.my_connect_scraper:
            print(f"[{self.id}] ❌ My Connect scraper chưa được khởi tạo")
            return []

        print(f"[{self.id}] 🕸️ Starting to collect profile URLs from My Network...")
        
        # STEP 1: Collect URLs from the network page.
        # The 'expand_and_collect_all_urls' method inside LinkedInMyNetworkScraper MUST be
        # modified to periodically check self.manager.is_stopped() during its scrolling/looping.
        profile_urls = self.my_connect_scraper.click_and_visit_all_profiles(self.is_stopped())

        # Check if the process was stopped during URL collection or if nothing was found.
        if self.is_stopped():
            print(f"[{self.id}] 🛑 Process stopped during URL collection.")
            return []
        if not profile_urls:
            print(f"[{self.id}] ❌ No profile URLs were collected from My Network.")
            return []

        print(f"[{self.id}] ✅ Collected {len(profile_urls)} profile URLs. Now fetching details...")
        
        return profile_urls
        
        # STEP 2: Scrape the details for the collected URLs.
        # The 'get_all_profile_details' method inside LinkedInProfileScraper MUST be
        # modified to check self.manager.is_stopped() before scraping each profile.
        # You will also need to pass your repository instances here if they are needed.
        
        
        # url_repo = UrlRepository()
        # profile_repo = ProfileRepository()
        # detailed_profiles = self.profile_scraper.get_all_profile_details(profile_urls, url_repo, profile_repo)

        # if self.is_stopped():
        #     print(f"[{self.id}] 🛑 Process stopped during detail scraping.")
        #     # Return whatever was collected so far
        #     return detailed_profiles 
            
        # print(f"[{self.id}] 🎉 Finished scraping {len(detailed_profiles)} detailed profiles.")
        # return detailed_profiles
        
    def scrape_profile_details(self, bot_id: int) -> Dict:
        """Scrapes detailed profile information from the given profile URL."""
        if self.is_stopped():
            print(f"[{bot_id}] 🛑 Process stopped before scraping profile details.")
            return {}
        url_repository = UrlRepository()
        urls_to_crawl = url_repository.get_urls_by_bot_id(bot_id=bot_id)
        
        url_repo = UrlRepository()
        profile_repo = ProfileRepository()
        detailed_profiles = self.profile_scraper.get_all_profile_details(urls_to_crawl, url_repo, profile_repo)
        
        return detailed_profiles
    
    def search_people(self, name: str):
        """
        Tìm kiếm người với tên được cung cấp và thu thập profile URLs qua nhiều trang
        """
        if self.is_stopped(): return []
        print(f"🔍 Bắt đầu tìm kiếm: {name}")
        
        self.search.input_people_name(name)
        HumanBehaviorSimulator.random_wait_after_action()
        
        self.search.click_people_tab()
        HumanBehaviorSimulator.random_wait_after_action()
        
        all_profile_urls = []
        
        for page in range(10):
            # --- MODIFICATION: The most important check, at the start of each major iteration ---
            if self.is_stopped():
                print(f"[{self.id}] 🛑 Stop signal detected. Halting search on page {page + 1}.")
                break # Exit the loop

            print(f"\n📄 Đang xử lý trang {page + 1}/10...")
            self._scroll_page_naturally()
            page_profiles = self.search.scrapper_a_tag()
            
            if page_profiles:
                all_profile_urls.extend(page_profiles)
            
            if page < 9:
                success = self.search.click_next_button()
                if not success:
                    print(f"❌ Không thể chuyển sang trang {page + 2}. Dừng thu thập.")
                    break
                HumanBehaviorSimulator.random_delay(2, 4)
        
        print(f"\n🎉 Hoàn thành thu thập! Tổng số URLs: {len(all_profile_urls)}")
        unique_profiles = self._remove_duplicate_profiles(all_profile_urls)
        
        if unique_profiles:
            DataManager.save_profiles_to_file(unique_profiles, f"search_results_{name.replace(' ', '_')}.json")
        
        return unique_profiles

    def cleanup(self):
        """Đóng driver"""
        if self.driver:
            print(f"[{self.id}] 🔐 Closing browser...")
            try:
                self.driver.quit()
            except Exception as e:
                print(f"[{self.id}] ⚠️ Error during driver cleanup: {e}")
            finally:
                self.driver = None

    # Helper methods like _remove_duplicate_profiles, _simulate_natural_mouse_movement etc. remain the same.
    # They are short-lived and don't need stop checks.
    # ... (paste your helper methods here) ...