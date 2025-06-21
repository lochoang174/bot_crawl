import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import os
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
class ChromeDriverManager:
    """Quản lý việc tạo và cấu hình Chrome Driver"""
    
    def __init__(self, profile_name: str = "linkedin_profile"):
        self.profile_name = profile_name
        self.profile_path = os.path.abspath(profile_name)
        
        # Danh sách User-Agent phổ biến và mới nhất
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    def get_random_user_agent(self):
        """Lấy User-Agent ngẫu nhiên từ danh sách"""
        return random.choice(self.user_agents)
    def create_undetected_driver_with_session(self):
        """Tạo undetected ChromeDriver với profile để lưu session"""
        print("Đang khởi tạo Undetected ChromeDriver với session...")
        
        # Tạo thư mục profile nếu chưa có
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
            print(f"✅ Đã tạo thư mục profile: {self.profile_path}")
        
        options = uc.ChromeOptions()
        
        # Sử dụng profile để lưu session
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--profile-directory=Default")
        # user_agent = self.get_random_user_agent()
        # options.add_argument(f"--user-agent={user_agent}")
        # print(f"🔧 Sử dụng User-Agent: {user_agent}")
        prefs = {
            "intl.accept_languages": "en,en_US",
            "translate.enabled": False,
            "translate_whitelists": {"vi": "en"},
        }
        options.add_experimental_option("prefs", prefs)
        
        # Các option khác để tránh detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = uc.Chrome(options=options)
            print("✅ Khởi tạo driver thành công với session profile")
            return driver
        except Exception as e:
            print(f"❌ Lỗi khi khởi tạo driver: {e}")
            return None

    def create_edge_driver_with_session(self):
            print("Đang khởi tạo Microsoft Edge Driver với session...")

            if not os.path.exists(self.profile_path):
                os.makedirs(self.profile_path)
                print(f"✅ Đã tạo thư mục profile: {self.profile_path}")

            options = EdgeOptions()

            # Sử dụng user profile (Edge dùng chung format với Chrome)
            options.add_argument(f"--user-data-dir={self.profile_path}")
            options.add_argument("--profile-directory=Default")
            
            # Thêm các tùy chọn giống như bạn dùng cho Chrome
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            try:
                driver = webdriver.Edge(options=options)
                print("✅ Khởi tạo Edge driver thành công với session profile")
                return driver
            except Exception as e:
                print(f"❌ Lỗi khi khởi tạo Edge driver: {e}")
                return None