import json
import os
import random
import time

import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import utils
from services.human_behavior import HumanBehaviorSimulator


class LinkedInAuthenticator:
    """Xử lý việc đăng nhập và đăng xuất LinkedIn"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
    
    def is_logged_in(self) -> bool:
        """Kiểm tra xem đã đăng nhập LinkedIn chưa"""
        try:
            print("🔍 Đang kiểm tra trạng thái đăng nhập...")
            
            # Kiểm tra URL hiện tại
            current_url = self.driver.current_url
            if "login" in current_url:
                print("❌ Đang ở trang login")
                return False
            
            # Thử tìm các element đặc trưng của LinkedIn khi đã đăng nhập
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.ID, "global-nav-typeahead")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='feed-tab']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-container")),
                    )
                )
                print("✅ Đã đăng nhập LinkedIn!")
                return True
            except TimeoutException:
                print("❌ Chưa đăng nhập hoặc trang chưa load xong")
                return False
                
        except Exception as e:
            print(f"⚠️ Lỗi khi kiểm tra trạng thái đăng nhập: {e}")
            return False
    
    def smart_login(self) -> bool:
        """Đăng nhập thông minh - xử lý cả trang chọn tài khoản"""
        try:
            print("🚀 Đang thử truy cập LinkedIn...")
            self.driver.get("https://www.linkedin.com/")
            
            # Wait for the page to load
            utils.wait_for_page_load(self.driver)

            cookie_dict = json.dumps(utils.read_cookie_file("../cookie.json"))
            if cookie_dict:
                print("🔐 Đang tải cookie từ file...")
                cookies = json.loads(cookie_dict)
                for cookie in cookies:
                    if cookie.get('sameSite') is None or cookie['sameSite'] == 'no_restriction':
                        cookie['sameSite'] = 'None'  # Đặt sameSite thành None để tránh lỗi
                    self.driver.add_cookie(cookie)
                print("✅ Cookie đã được tải thành công.")
            else:
                print("❌ Không tìm thấy cookie, sẽ đăng nhập thủ công.")
            
            self.driver.get("https://www.linkedin.com/feed/")
            
            # Wait for the page to load
            utils.wait_for_page_load(self.driver)
            
            if self.is_logged_in():
                print("🎉 Đã đăng nhập từ session cũ! Không cần nhập lại email/password")
                return True
            
            print("🔐 Chưa đăng nhập, tiến hành đăng nhập thủ công...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for the login page to load
            utils.wait_for_page_load(self.driver)
                        
        except Exception as e:
            print(f"❌ Lỗi trong quá trình đăng nhập thông minh: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def logout(self) -> bool:
        """Đăng xuất khỏi LinkedIn"""
        print("\n🔄 Đang tiến hành đăng xuất khỏi LinkedIn...")
        
        try:
            # Tìm và click vào nút "Me"
            print("🔍 Tìm và click vào icon 'Me' (menu người dùng)...")
            try:
                me_icon = self.wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(@class, 'global-nav__primary-link-me-menu-trigger')]"
                    ))
                )
            except TimeoutException:
                print("❌ Không tìm thấy icon 'Me'. Thử với ID mặc định...")
                me_icon = self.wait.until(EC.element_to_be_clickable((By.ID, "global-nav-dropdown-button")))
            
            me_icon.click()
            print("✅ Đã mở menu người dùng.")
            time.sleep(random.uniform(1, 2))

            # Click vào nút đăng xuất
            print("🔍 Tìm nút 'Đăng xuất' hoặc 'Sign Out'...")
            signout_xpath = "//a[contains(@href, '/m/logout/') or contains(text(), 'Sign Out') or contains(text(), 'Đăng xuất')]"
            
            sign_out_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, signout_xpath))
            )
            
            self.driver.execute_script("arguments[0].scrollIntoView();", sign_out_button)
            sign_out_button.click()
            print("✅ Đã click nút 'Sign Out'.")
            print("🎉 Đăng xuất thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi đăng xuất: {e}")
            return False
