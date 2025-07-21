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
    """Quản lý việc tạo và cấu hình Driver (Chrome hoặc Edge) cho mỗi bot"""

    def __init__(self, bot_id: str, base_profile_dir: str = "profiles"):
        """
        Khởi tạo manager với profile riêng cho mỗi bot.
        :param bot_id: ID duy nhất của bot để tạo folder riêng.
        :param base_profile_dir: Thư mục gốc để lưu các folder session của bot.
        """
        self.bot_id = bot_id
        self.profile_path = os.path.abspath(os.path.join(base_profile_dir, f"bot_{bot_id}"))

        # Danh sách User-Agent phổ biến và mới nhất
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        ]

    def get_random_user_agent(self):
        """Lấy User-Agent ngẫu nhiên từ danh sách"""
        return random.choice(self.user_agents)

    def create_undetected_driver_with_session(self):
        """Tạo undetected ChromeDriver với session riêng cho bot"""
        print(f"[{self.bot_id}] Đang khởi tạo Undetected ChromeDriver với session...")

        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
            print(f"[{self.bot_id}] ✅ Tạo thư mục profile: {self.profile_path}")

        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--profile-directory=Default")

        # Thêm các option tránh detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        prefs = {
            "intl.accept_languages": "en,en_US",
            "translate.enabled": False,
            "translate_whitelists": {"vi": "en"},
        }
        options.add_experimental_option("prefs", prefs)

        try:
            driver = uc.Chrome(options=options)
            print(f"[{self.bot_id}] ✅ Khởi tạo driver thành công với session")
            return driver
        except Exception as e:
            print(f"[{self.bot_id}] ❌ Lỗi khi khởi tạo Chrome driver: {e}")
            return None

    def create_edge_driver_with_session(self):
        """Tạo Microsoft Edge Driver với session riêng cho bot"""
        print(f"[{self.bot_id}] Đang khởi tạo Microsoft Edge Driver với session...")

        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
            print(f"[{self.bot_id}] ✅ Tạo thư mục profile: {self.profile_path}")

        options = EdgeOptions()
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--profile-directory=Default")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            os.environ['DISPLAY'] = ':1'

            driver = webdriver.Edge(options=options)
            print(f"[{self.bot_id}] ✅ Khởi tạo Edge driver thành công với session")
            return driver
        except Exception as e:
            print(f"[{self.bot_id}] ❌ Lỗi khi khởi tạo Edge driver: {e}")
            return None