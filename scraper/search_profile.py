from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from services.human_behavior import HumanBehaviorSimulator
from selenium.webdriver.common.by import By
 
class SearchPeople:
    def __init__(self,driver):
        self.driver = driver
    def input_people_name(self, name: str):
        try:
            # Đợi cho thanh input tìm kiếm xuất hiện
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.search-global-typeahead__input")
                )
            )

            # Di chuyển chuột đến thanh input để mô phỏng tự nhiên
            ActionChains(self.driver).move_to_element(search_input).perform()

            # Xóa nội dung cũ nếu có
            search_input.clear()

            # Mô phỏng gõ từng ký tự như người thật
            for char in name:
                search_input.send_keys(char)
                HumanBehaviorSimulator.random_typing_delay()

            # Nhấn Enter để tìm kiếm
            search_input.send_keys("\n")
            HumanBehaviorSimulator.random_wait_after_action()

        except (TimeoutException, NoSuchElementException) as e:
            print(f"[SearchPeople] Không thể tìm thấy ô tìm kiếm: {e}")

    def click_people_tab(self):
        try:
            # Đợi nút "Người" hoặc "People" xuất hiện và sẵn sàng click
            people_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'search-reusables__filter-pill-button') and (contains(., 'Người') or contains(., 'People'))]"
                ))
            )

            # Di chuyển chuột tới nút và click để mô phỏng hành vi người dùng
            ActionChains(self.driver).move_to_element(people_button).click().perform()
            HumanBehaviorSimulator.random_wait_after_action()

        except (TimeoutException, NoSuchElementException) as e:
            print(f"[SearchPeople] Không thể tìm thấy nút 'Người/People': {e}")
    def click_next_button(self):
        try:
            next_btn = next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[@aria-label='Next' or @aria-label='Tiếp theo']"                
                    ))
            )
            print("Đã click nút Next")

            next_btn.click()
            return next_btn
        except Exception as e:
            print("Không thể click nút Next:", e)
    def scrapper_a_tag(self):
        """Thu thập profile URLs từ trang hiện tại"""
        profile_urls = []

        try:
            # Chờ đến khi <ul role="list"> xuất hiện
            ul_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul[role='list'].list-style-none"))
            )

            # Tìm tất cả <li> trong <ul>
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
            print(f"🔍 Tìm thấy tổng cộng {len(li_elements)} thẻ <li> trong <ul role='list'>.")

            for li in li_elements:
                a_tags = li.find_elements(By.TAG_NAME, 'a.scale-down')
                for a in a_tags:
                    href = a.get_attribute("href")
                    name_and_title = a.text.strip().replace('\n', ' ')
                    if href and "/in/" in href and "linkedin.com" in href:
                        profile_urls.append({'url': href, 'text': name_and_title})

            # Loại bỏ duplicate trong trang hiện tại
            seen_urls = set()
            unique_profiles = []
            for profile in profile_urls:
                if profile['url'] not in seen_urls:
                    seen_urls.add(profile['url'])
                    print(f"📋 Profile: {profile}")  # Debug log
                    unique_profiles.append(profile)

            print(f"✅ Thu thập được {len(unique_profiles)} profile unique từ trang này.")
            return unique_profiles  # QUAN TRỌNG: Phải return dữ liệu
            
        except Exception as e:
            print(f"❌ Lỗi khi thu thập profile URLs: {e}")
            return []
