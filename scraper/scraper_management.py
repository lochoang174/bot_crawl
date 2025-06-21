from services.authen import LinkedInAuthenticator
from scraper.company_scraper import LinkedInCompanyScraper
from scraper.profile_scraper import LinkedInProfileScraper
from services.driver_management import ChromeDriverManager
from scraper.data_manager import DataManager
from typing import List, Dict
from scraper.my_network_scraper import LinkedInMyNetworkScraper

class LinkedInScraperManager:
    """Class chính quản lý toàn bộ quá trình scraping"""
    
    def __init__(self, profile_name: str = "linkedin_profile"):
        self.driver_manager = ChromeDriverManager(profile_name)
        self.driver = None
        self.authenticator = None
        self.company_scraper = None
        self.profile_scraper = None
        self.my_connect_scraper = None
    
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
    
    def scrape_my_connect_profiles(self) -> List[Dict]:
        if not self.my_connect_scraper:
            print("❌ My Connect scraper chưa được khởi tạo")
            return []
        
        profile_urls = self.my_connect_scraper.expand_and_collect_all_urls()
        if not profile_urls:
            print("❌ Không thu thập được URL profile nào từ My Network")
            return []
        
        # Lưu danh sách URL
        # DataManager.save_profiles_to_file(profile_urls, "my_connect_profile_urls.json")
        # Lấy thông tin chi tiết
        
        # detailed_profiles = self.profile_scraper.get_all_profile_details(profile_urls)
        # if detailed_profiles:
        #     DataManager.save_profiles_to_file(detailed_profiles, "my_connect_detailed_profiles_final.json") 
        # return detailed_profiles
    
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