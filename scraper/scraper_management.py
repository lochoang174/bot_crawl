import random
import time
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
class LinkedInScraperManager:
    """Class chính quản lý toàn bộ quá trình scraping"""
    
    def __init__(self, profile_name: str = "linkedin_profile", id: str = None):
        self.driver_manager = ChromeDriverManager(id,profile_name)
        self.driver = None
        self.authenticator = None
        self.company_scraper = None
        self.profile_scraper = None
        self.my_connect_scraper = None
        self.stop = False
        self.id = id
     
    def set_stop(self):
        """Thiết lập trạng thái dừng"""
        self.stop = True
        if self.my_connect_scraper:
            self.my_connect_scraper.stop = True
        print(f"🔴 Trạng thái dừng đã được thiết lập: {self.stop}") 

    def is_stopped(self) -> bool:
        """Kiểm tra trạng thái dừng"""
        return self.stop
        
    def initialize_driver(self) -> bool:
        """Khởi tạo driver và các scraper"""
        self.driver = self.driver_manager.create_edge_driver_with_session()
        if not self.driver:
            return False
        
        self.authenticator = LinkedInAuthenticator(self.driver)
        self.company_scraper = LinkedInCompanyScraper(self.driver)
        self.profile_scraper = LinkedInProfileScraper(self.driver)
        self.my_connect_scraper = LinkedInMyNetworkScraper(self.driver)
        return True
    
    def login(self, email: str, password: str) -> bool:
        """Đăng nhập LinkedIn"""
        if not self.authenticator:
            print("❌ Driver chưa được khởi tạo")
            return False
        return self.authenticator.smart_login(email, password)
    
    def scrape_company_profiles(self, company_url: str) -> List[Dict]:
        """Scrape tất cả profiles từ một công ty"""
        if not self.company_scraper:
            print("❌ Company scraper chưa được khởi tạo")
            return []
        
        # Lấy danh sách URL
        profile_urls = self.company_scraper.expand_and_collect_all_urls(company_url)
        if not profile_urls:
            print("❌ Không thu thập được URL profile nào")
            return []
        
        # Lưu danh sách URL
        DataManager.save_profiles_to_file(profile_urls, "collected_profile_urls.json")
        
        # Lấy thông tin chi tiết
        detailed_profiles = self.profile_scraper.get_all_profile_details(profile_urls)
        
        if detailed_profiles:
            DataManager.save_profiles_to_file(detailed_profiles, "linkedin_detailed_profiles_final.json")
        
        return detailed_profiles
    
    def scrape_my_connect_profiles(self, bot_id: str) -> List[Dict]:
        if not self.my_connect_scraper:
            print("❌ My Connect scraper chưa được khởi tạo")
            return []
        url_repo = UrlRepository()
        profile_repo = ProfileRepository()

        print("self.stop", self.stop)
        
        profile_urls = self.my_connect_scraper.expand_and_collect_all_urls(bot_id=bot_id, stop=self.stop)
        
        
        return profile_urls
        # for log in profile_urls:
        #     yield log
        #     print(log.message)

        # print(f"📊 Đã thu thập {profile_urls} profile URLs từ My Network")
        # if not profile_urls:
        #     print("❌ Không thu thập được URL profile nào từ My Network")
        #     return []
        url_repository = UrlRepository()
        
        urls_to_crawl = url_repository.get_urls_by_bot_id(1)
        
        detailed_profiles = self.profile_scraper.get_all_profile_details(urls_to_crawl, url_repo, profile_repo)
       
        return detailed_profiles
    
    def logout(self) -> bool:
        """Đăng xuất LinkedIn"""
        if not self.authenticator:
            return False
        return self.authenticator.logout()
    
    def cleanup(self):
        """Đóng driver"""
        if self.driver:
            print("🔐 Đang đóng trình duyệt...")
            self.driver.quit()
            self.driver = None
    def search_people(self, name: str):
        """
        Tìm kiếm người với tên được cung cấp và thu thập profile URLs qua nhiều trang
        """
        print(f"🔍 Bắt đầu tìm kiếm: {name}")
        
        # Bước 1: Nhập tên người cần tìm
        self.search.input_people_name(name)
        HumanBehaviorSimulator.random_wait_after_action()
        
        # Bước 2: Click tab "People/Người"
        self.search.click_people_tab()
        HumanBehaviorSimulator.random_wait_after_action()
        
        # Delay và di chuyển chuột tự nhiên
        print("📍 Mô phỏng hành vi người dùng...")
        HumanBehaviorSimulator.random_delay(2, 4)
        
        # Di chuyển chuột random trên trang
        self._simulate_natural_mouse_movement()
        
        all_profile_urls = []
        
        # Bước 3: Thu thập dữ liệu qua 10 trang
        for page in range(10):
            print(f"\n📄 Đang xử lý trang {page + 1}/10...")
            
            # Scroll xuống để load hết nội dung
            print("⬇️ Đang scroll xuống trang...")
            self._scroll_page_naturally()
            
            # Thu thập profile URLs từ trang hiện tại
            print("🎯 Thu thập profile URLs...")
            page_profiles = self.search.scrapper_a_tag()
            
            if page_profiles:
                all_profile_urls.extend(page_profiles)
                print(f"✅ Trang {page + 1}: Thu thập được {len(page_profiles)} profiles")
            else:
                print(f"⚠️ Trang {page + 1}: Không thu thập được profile nào")
            
            # Nếu chưa phải trang cuối, click Next
            if page < 9:  # Chỉ click Next 9 lần (trang 1->2, 2->3, ..., 9->10)
                print("➡️ Chuyển sang trang tiếp theo...")
                
                # Delay trước khi click Next
                HumanBehaviorSimulator.random_delay(1.5, 3)
                
                # Di chuyển chuột trước khi click
                self._move_mouse_before_click()
                
                # Click nút Next
                success = self.search.click_next_button()
                if not success:
                    print(f"❌ Không thể chuyển sang trang {page + 2}. Dừng thu thập.")
                    break
                
                # Delay sau khi click Next
                HumanBehaviorSimulator.random_wait_after_action()
                HumanBehaviorSimulator.random_delay(2, 4)
        
        # Bước 4: Tổng kết kết quả
        print(f"\n🎉 Hoàn thành thu thập!")
        print(f"📊 Tổng số profile URLs thu thập được: {len(all_profile_urls)}")
        
        # Loại bỏ duplicate URLs
        unique_profiles = self._remove_duplicate_profiles(all_profile_urls)
        print(f"🔄 Sau khi loại bỏ duplicate: {len(unique_profiles)} profiles unique")
        
        # Lưu kết quả vào file (tuỳ chọn)
        if unique_profiles:
            DataManager.save_profiles_to_file(unique_profiles, f"search_results_{name.replace(' ', '_')}.json")
            print(f"💾 Đã lưu kết quả vào file search_results_{name.replace(' ', '_')}.json")
        
        return unique_profiles


    def _remove_duplicate_profiles(self, profiles):
        """Loại bỏ profile URLs trùng lặp"""
        seen_urls = set()
        unique_profiles = []
        
        for profile in profiles:
            url = profile.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_profiles.append(profile)
        
        return unique_profiles
    def _simulate_natural_mouse_movement(self):
            """Mô phỏng di chuyển chuột tự nhiên trên trang"""
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                
                # Lấy kích thước window
                window_size = self.driver.get_window_size()
                width = window_size['width']
                height = window_size['height']
                
                # Di chuyển chuột đến 3-5 vị trí ngẫu nhiên
                actions = ActionChains(self.driver)
                
                for _ in range(random.randint(3, 5)):
                    x = random.randint(100, width - 100)
                    y = random.randint(100, height - 100)
                    
                    actions.move_by_offset(x - width//2, y - height//2)
                    actions.perform()
                    
                    time.sleep(random.uniform(0.3, 0.8))
                    
                    # Reset để tránh lỗi offset tích lũy
                    actions = ActionChains(self.driver)
                    
            except Exception as e:
                print(f"⚠️ Không thể mô phỏng di chuyển chuột: {e}")

    def _scroll_page_naturally(self):
        """Scroll trang một cách tự nhiên"""
        # Scroll xuống từng đoạn nhỏ
        for _ in range(random.randint(3, 6)):
            HumanBehaviorSimulator.human_scroll(self.driver)
            time.sleep(random.uniform(0.5, 1.2))
        
        # Scroll về đầu trang một chút
        self.driver.execute_script("window.scrollBy(0, -200);")
        time.sleep(random.uniform(0.3, 0.7))

    def _move_mouse_before_click(self):
        """Di chuyển chuột trước khi click để tự nhiên hơn"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Di chuyển chuột một chút
            actions = ActionChains(self.driver)
            actions.move_by_offset(random.randint(-50, 50), random.randint(-30, 30))
            actions.perform()
            
            time.sleep(random.uniform(0.2, 0.5))
            
        except Exception as e:
            print(f"⚠️ Không thể di chuyển chuột: {e}")
    