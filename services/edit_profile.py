from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import time
from selenium.webdriver.support.ui import Select

class LinkedInProfileViewer:
    def __init__(self, driver, company_name=str):
        """
        Initialize the LinkedInProfileViewer with a Selenium WebDriver instance.
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.company_name = company_name  
        
    def access_linkedin_home_page(self):
        """
        Navigate to the LinkedIn home page.
        """
        try:
            print("🌐 Đang truy cập trang chủ LinkedIn...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)  # Wait for the page to load
            print("✅ Đã truy cập trang chủ LinkedIn.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi truy cập trang chủ LinkedIn: {e}")

    def click_view_profile_button(self):
        """
        Click the 'View Profile' button on the LinkedIn home page.
        """
        try:
            print("🔍 Đang mở menu người dùng...")
            # Step 1: Click on the profile menu to open the dropdown
            menu_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'global-nav__primary-link-me-menu-trigger') or @data-view-name='navigation-settings']"
                ))
            )
            menu_button.click()
            time.sleep(1)  # Wait for the dropdown to appear

            print("🔍 Đang tìm nút 'View Profile'...")
            # Step 2: Wait for the View Profile link
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
            print(f"🔍 Tìm thấy {len(links)} liên kết có '/in/':")
            for i, link in enumerate(links, 1):
                print(f"{i}: {link.text} → {link.get_attribute('href')}")

            for link in links:
                if "View Profile" in link.text:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    link.click()
                    print("✅ Đã click nút 'View Profile'.")
                    return
        except TimeoutException:
            print("❌ Không tìm thấy hoặc không thể click nút 'View Profile' trong thời gian chờ.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click nút 'View Profile': {e}")

    def click_edit_profile_button(self):
        """
        Click the 'Edit intro' button on the LinkedIn profile page.
        """
        try:
            print("🔍 Đang tìm nút 'Edit intro'...")

            xpath = "//button[@aria-label='Edit intro']"


            # Wait for the element to appear in DOM
            edit_intro_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_intro_button)

            # Click the button
            edit_intro_button.click()

          
            
            print("✅ Đã click nút 'Edit intro'.")
        except TimeoutException:
            print("❌ Không tìm thấy hoặc không thể click nút 'Edit intro' trong thời gian chờ.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click nút 'Edit intro': {e}")
            
    def click_add_position_link(self):
        """
        After clicking 'Edit intro', click a specific link inside the profile edit page.
        """
        try:
            # Step 1: Ensure we're in the profile edit screen

            print("🔍 Đang tìm phần tử tiếp theo trong trang chỉnh sửa profile...")

            # Step 2: Wait for the element
            target_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#profile-edit-form-page-content > section > div > div:nth-child(5) > div:nth-child(2) > a"))
            )

            # Step 3: Scroll and click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_link)
            target_link.click()

            print("✅ Đã click vào liên kết sau chỉnh sửa profile.")
        except TimeoutException:
            print("❌ Không tìm thấy hoặc không thể click phần tử tiếp theo sau khi mở Edit Profile.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi thao tác sau Edit Profile: {e}")


    def add_position_and_select_random_title(self):
        """
        Click 'Add position', type 'dev' in job title input, and randomly select a suggestion.
        """
        try:

            print("🔍 Đang tìm ô nhập tiêu đề công việc...")
            title_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Ex: Retail Sales Manager']"))
            )

            # Step 1: Type "dev" to trigger suggestions
            title_input.clear()
            title_input.send_keys("dev")
            time.sleep(1.5)
            print("⌛ Đang chờ danh sách gợi ý công việc hiển thị...")

            # Step 2: Wait for dropdown to appear (usually under a UL with role="listbox")
            suggestions = self.wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='listbox'] div[role='option']"))
)
            # Step 3: Pick one at random and click
            if suggestions:
                chosen = random.choice(suggestions)
                print(f"🎯 Chọn công việc: {chosen.text}")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen)
                chosen.click()
                print("✅ Đã chọn một công việc ngẫu nhiên.")
            else:
                print("⚠️ Không có gợi ý công việc nào xuất hiện.")

        except TimeoutException:
            print("❌ Không thể tìm thấy ô nhập hoặc danh sách gợi ý.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")


    def type_company_name(self):
        """
        Type a company name into the 'Company or organization' input field with suggestion.
        """
        try:
            print(f"🔍 Đang tìm ô nhập 'Company or organization' để nhập: '{self.company_name}'")
            
            

            # Step 1: Find the input by placeholder
            company_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Ex: Microsoft']"))
            )

            # Step 2: Clear and type the company name
            company_input.clear()
            company_input.send_keys(self.company_name)
            time.sleep(2.5)  # Allow time for suggestions to appear

            # Step 3: Wait for suggestions to show
            suggestions = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='listbox'] div[role='option']"))
            )

            if suggestions:
                chosen = random.choice(suggestions)
                print(f"🏢 Chọn công ty ngẫu nhiên: {chosen.text}")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen)
                try:
                    chosen.click()
                except:
                    print("⚠️ Không click được, thử dùng bàn phím.")
                    company_input.send_keys(Keys.ARROW_DOWN)
                    company_input.send_keys(Keys.ENTER)

                print("✅ Đã chọn công ty.")
            else:
                print("⚠️ Không có gợi ý công ty nào được hiển thị.")
        except TimeoutException:
            print("❌ Không thể tìm thấy ô nhập 'Company or organization' hoặc danh sách gợi ý.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")

    
    def select_random_start_date(self):
        """
        Select a random start month (1–12) and year (2023–2025) for the job position.
        """
        try:
            print("📅 Đang chọn tháng bắt đầu ngẫu nhiên...")
            
            # Step 1: Select a random month
            month_select = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[data-test-month-select]"))
            )
            month_dropdown = Select(month_select)

            random_month_value = str(random.randint(1, 12))  # '1' to '12'
            month_dropdown.select_by_value(random_month_value)
            print(f"✅ Đã chọn tháng: {random_month_value}")

            # Step 2: Select a random year between 2023–2025
            print("📅 Đang chọn năm bắt đầu ngẫu nhiên...")
            year_select = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[data-test-year-select]"))
            )
            year_dropdown = Select(year_select)

            random_year = str(random.choice([2022,2023, 2024]))
            year_dropdown.select_by_value(random_year)
            print(f"✅ Đã chọn năm: {random_year}")

        except TimeoutException:
            print("❌ Không thể tìm thấy các trường chọn tháng hoặc năm.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi chọn tháng/năm: {e}")
            
    def click_save_button(self):
        """
        Click the 'Save' button to submit the position form.
        """
        try:
            print("💾 Đang tìm và click nút 'Save'...")

            save_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-view-name='profile-form-save']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            save_button.click()

            print("✅ Đã click nút 'Save'. Đang lưu thông tin...")
        except TimeoutException:
            print("❌ Không thể tìm thấy hoặc click nút 'Save'.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click nút 'Save': {e}")


    def click_skip_button(self):
        """
        Wait for and click the 'Skip' button after saving the position (if it appears).
        """
        try:
            print("⏳ Đang chờ nút 'Skip' hiển thị...")
            skip_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Skip']]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", skip_button)
            skip_button.click()

            print("✅ Đã click nút 'Skip'.")
        except TimeoutException:
            print("⚠️ Không tìm thấy nút 'Skip'. Có thể không xuất hiện sau khi lưu.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click 'Skip': {e}")

    def select_position_matching_company_name(self):
        """
        Clicks the styled dropdown, waits for options to load,
        and selects the one that includes self.company_name.
        """
        try:
            print("🔽 Đang mở dropdown vị trí...")

            # Step 1: Click the dropdown to open it
            dropdown_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select[data-test-text-entity-list-form-select]"))
            )
            dropdown_button.click()

            time.sleep(1)  # Short pause for options to render

            print(f"🔍 Đang tìm lựa chọn chứa: '{self.company_name}'")

            # Step 2: Find matching <option> that contains the name
            options = self.driver.find_elements(By.CSS_SELECTOR, "select[data-test-text-entity-list-form-select] > option")
            
            matched = False
            for option in options:
                text = option.text.strip()
                if self.company_name.strip().lower() in text.lower():
                    # Scroll and click (or use Select)
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                    option.click()
                    print(f"✅ Đã chọn: {text}")
                    matched = True
                    break

            if not matched:
                print(f"⚠️ Không tìm thấy lựa chọn chứa: '{self.company_name}'")

        except TimeoutException:
            print("❌ Dropdown không hiển thị đúng lúc.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi chọn vị trí: {e}")

            """
            Wait for the position <select> dropdown to load and select the option matching self.company_name.
            """
            try:
                # self.click_skip_button()
                print("🔽 Đang tìm và chọn công việc trong dropdown...")

                # Step 1: Wait for the <select> element to appear
                select_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[data-test-text-entity-list-form-select]"))
                )

                dropdown = Select(select_element)

                # Step 2: Get all options and find the one that matches exactly
                matched = False
                for option in dropdown.options:
                    if option.text.strip() == self.company_name:
                        dropdown.select_by_visible_text(option.text)
                        matched = True
                        print(f"✅ Đã chọn: {option.text}")
                        break

                if not matched:
                    print(f"⚠️ Không tìm thấy công việc phù hợp với: '{self.company_name}' trong danh sách.")

            except TimeoutException:
                print("❌ Không tìm thấy dropdown chọn vị trí.")
            except Exception as e:
                print(f"❌ Lỗi không mong muốn khi chọn vị trí trong dropdown: {e}")
                
    
    def click_final_save_button(self):
        """
        Click the final 'Save' button to confirm the selected position from the dropdown.
        """
        try:
            print("💾 Đang tìm và click nút 'Save' cuối cùng...")

            save_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-view-name='profile-form-save']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            save_button.click()

            print("✅ Đã click nút 'Save'.")
        except TimeoutException:
            print("❌ Không thể tìm thấy hoặc click nút 'Save' cuối.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click nút 'Save': {e}")

    def click_close_modal_button(self):
        """
        Wait for and click the 'Close' (Dismiss) button to close the modal after saving.
        """
        try:
            time.sleep(2)  # Đợi một chút để modal có thể hiển thị
            print("❎ Đang chờ nút 'Close' (Dismiss) hiển thị...")

            close_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-modal-close-btn]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", close_button)
            close_button.click()

            print("✅ Đã click nút 'Close'. Đã đóng biểu mẫu.")
        except TimeoutException:
            print("❌ Không tìm thấy hoặc không thể click nút 'Close' trong thời gian chờ.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn khi click nút 'Close': {e}")
            
    def view_and_edit_profile(self):
        skip_count = 0  # Initialize a counter to track the number of skips

        while True:  # Loop to handle the recursive behavior
            self.access_linkedin_home_page()
            self.click_view_profile_button()

            if skip_count < 2:
                self.click_edit_profile_button()
                self.click_add_position_link()
                self.add_position_and_select_random_title()
                self.type_company_name()
                self.select_random_start_date()
                self.click_save_button()

                # Check if the 'Skip' button is clickable
                try:
                    while True:  # Loop to handle multiple "Skip" buttons
                        time.sleep(2)  # Wait for the page to load
                        print("⏳ Đang chờ nút 'Skip' hiển thị...")
                        skip_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Skip']]"))
                        )
                        if skip_button:
                            self.click_skip_button()
                            skip_count += 1  # Increment the skip counter
                            print(f"🔄 Đã skip {skip_count} lần.")

                            # Instead of waiting for invisibility, check for the next clickable "Skip" button
                            try:
                                self.wait = WebDriverWait(self.driver, 3)  # Shorten the timeout
                                next_skip_button = self.wait.until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Skip']]"))
                                )
                                if next_skip_button:
                                    continue  # Continue to the next "Skip" button
                            except TimeoutException:
                                print("⚠️ Không tìm thấy nút 'Skip' tiếp theo. Tiếp tục quy trình.")
                                break  # Exit the loop if no more "Skip" buttons are found
                        else:
                            break  # Exit the loop if no more "Skip" buttons are found
                except TimeoutException:
                    print("⚠️ Không tìm thấy nút 'Skip'. Tiếp tục quy trình.")
                except Exception as e:
                    print(f"❌ Lỗi không mong muốn khi kiểm tra nút 'Skip': {e}")

            # If skip_count == 2, execute the specified actions and break the loop
            if skip_count == 2:
                print("🔄 Đã đạt giới hạn skip_count = 2. Thực hiện hành động cuối cùng và thoát.")
                self.click_edit_profile_button()
                self.select_position_matching_company_name()
                self.click_final_save_button()
                self.click_close_modal_button()
                self.click_close_modal_button()
                self.access_linkedin_home_page()
                
                
                break  # Exit the loop

            self.select_position_matching_company_name()
            self.click_final_save_button()
            self.click_close_modal_button()
            self.access_linkedin_home_page()

            print("🔄 Đã hoàn thành một chu kỳ. Tiếp tục với trạng thái hiện tại.")
            break

            