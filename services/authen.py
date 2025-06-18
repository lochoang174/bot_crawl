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
    
    def smart_login(self, email: str, password: str) -> bool:
        """Đăng nhập thông minh - xử lý cả trang chọn tài khoản"""
        try:
            print("🚀 Đang thử truy cập LinkedIn...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(4)
            
            if self.is_logged_in():
                print("🎉 Đã đăng nhập từ session cũ! Không cần nhập lại email/password")
                return True
            
            print("🔐 Chưa đăng nhập, tiến hành đăng nhập thủ công...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Xử lý trang chọn tài khoản
            try:
                another_account_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(@class, 'signin-other-account')]//p[normalize-space()='Sign in using another account']"
                    ))
                )
                print("🔍 Đã phát hiện trang chọn tài khoản. Đang click để hiển thị form đăng nhập...")
                another_account_button.click()
                time.sleep(2)
            except TimeoutException:
                print("👍 Form đăng nhập đã hiển thị sẵn.")
                pass
            
            return self._perform_login(email, password)
            
        except Exception as e:
            print(f"❌ Lỗi trong quá trình đăng nhập thông minh: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _perform_login(self, email: str, password: str) -> bool:
        """Thực hiện việc đăng nhập"""
        print(f"Đang tiến hành đăng nhập với tài khoản: {email}...")
        try:
            # Nhập email
            print("Đang tìm ô nhập email...")
            email_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            email_field.clear()
            email_field.click()
            HumanBehaviorSimulator.human_type(email_field, email)
            print("Đã nhập email.")
            HumanBehaviorSimulator.random_delay(0.5, 1)

            # Nhập password
            print("Đang tìm ô nhập mật khẩu...")
            password_field = self.wait.until(
                EC.element_to_be_clickable((By.ID, "password"))
            )
            password_field.clear()
            password_field.click()
            HumanBehaviorSimulator.human_type(password_field, password)
            print("Đã nhập mật khẩu.")
            HumanBehaviorSimulator.random_delay(0.5, 1)

            # Click nút đăng nhập
            print("Đang tìm nút 'Sign in'...")
            sign_in_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            sign_in_button.click()
            
            print("Đã nhấn nút đăng nhập, đang chờ xác nhận...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "global-nav-typeahead"))
            )
            print("Đăng nhập thành công! ✅")
            return True

        except TimeoutException:
            print("Lỗi: Không tìm thấy các thành phần để đăng nhập trong thời gian quy định.")
            self.driver.save_screenshot("linkedin_login_error.png")
            print("Đã lưu ảnh chụp màn hình lỗi vào file 'linkedin_login_error.png'")
            return False
        except Exception as e:
            print(f"Lỗi không xác định trong quá trình đăng nhập: {e}")
            self.driver.save_screenshot("linkedin_login_exception.png")
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
