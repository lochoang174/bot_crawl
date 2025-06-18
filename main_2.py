
def create_undetected_driver_with_session(profile_name="linkedin_profile"):
    """Tạo undetected ChromeDriver với profile để lưu session"""
    print("Đang khởi tạo Undetected ChromeDriver với session...")
    
    # Tạo thư mục profile nếu chưa có
    profile_path = os.path.abspath(profile_name)
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
        print(f"✅ Đã tạo thư mục profile: {profile_path}")
    
    options = uc.ChromeOptions()
    
    # Sử dụng profile để lưu session
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")

    options.add_argument("--profile-directory=Default")
    prefs = {
        "intl.accept_languages": "en,en_US",  # Ưu tiên tiếng Anh
        "translate.enabled": False, # Tắt hoàn toàn tính năng dịch

        "translate_whitelists": {"vi": "en"}, # Nếu phát hiện tiếng Việt, không dịch sang tiếng Anh
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

def is_logged_in_linkedin(driver):
    """Kiểm tra xem đã đăng nhập LinkedIn chưa"""
    try:
        print("🔍 Đang kiểm tra trạng thái đăng nhập...")
        
        # Kiểm tra URL hiện tại
        current_url = driver.current_url
        if "login" in current_url:
            print("❌ Đang ở trang login")
            return False
        
        # Thử tìm các element đặc trưng của LinkedIn khi đã đăng nhập
        try:
            # Kiểm tra thanh navigation
            WebDriverWait(driver, 5).until(
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

def smart_linkedin_login(email, password, profile_name="linkedin_profile"):
    """Đăng nhập thông minh - xử lý cả trang chọn tài khoản và chỉ nhập khi cần"""
    
    driver = create_undetected_driver_with_session(profile_name) # Sử dụng hàm tạo driver đã sửa ở dưới
    if not driver:
        return None
    
    try:
        print("🚀 Đang thử truy cập LinkedIn...")
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(4) # Tăng thời gian chờ một chút
        
        if is_logged_in_linkedin(driver):
            print("🎉 Đã đăng nhập từ session cũ! Không cần nhập lại email/password")
            return driver
        
        print("🔐 Chưa đăng nhập, tiến hành đăng nhập thủ công...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)
        
        # --- LOGIC MỚI ĐỂ XỬ LÝ TRANG CHỌN TÀI KHOẢN ---
        try:
            # Chờ tối đa 5 giây để tìm nút "Use another account"
            # XPath này tìm một button chứa link đến trang login đầy đủ
            another_account_button =WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'signin-other-account')]//p[normalize-space()='Sign in using another account']"
                ))
            )
            print("🔍 Đã phát hiện trang chọn tài khoản. Đang click để hiển thị form đăng nhập...")
            another_account_button.click()
            time.sleep(2) # Chờ form hiện ra
        except TimeoutException:
            # Không tìm thấy nút, nghĩa là form đăng nhập đã hiện sẵn. Tốt!
            print("👍 Form đăng nhập đã hiển thị sẵn.")
            pass
        # ---------------------------------------------------
        
        login_successful = login_to_linkedin(driver, email, password)
        
        if login_successful:
            print("✅ Đăng nhập thành công! Session đã được lưu cho lần sau.")
            return driver
        else:
            print("❌ Đăng nhập thất bại")
            driver.quit()
            return None
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình đăng nhập thông minh: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        return None

def login_to_linkedin(driver, email, password):
    """Hàm xử lý logic đăng nhập vào LinkedIn đã được tối ưu."""
    print(f"Đang tiến hành đăng nhập với tài khoản: {email}...")
    try:
        print("Đang tìm ô nhập email...")
        email_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        email_field.clear()
        email_field.click()
        human_type(email_field, email)
        print("Đã nhập email.")
        random_delay(0.5, 1)

        print("Đang tìm ô nhập mật khẩu...")
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_field.clear()
        password_field.click()
        human_type(password_field, password)
        print("Đã nhập mật khẩu.")
        random_delay(0.5, 1)

        print("Đang tìm nút 'Sign in'...")
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        sign_in_button.click()
        
        print("Đã nhấn nút đăng nhập, đang chờ xác nhận...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "global-nav-typeahead"))
        )
        print("Đăng nhập thành công! ✅")
        return True

    except TimeoutException:
        print("Lỗi: Không tìm thấy các thành phần để đăng nhập trong thời gian quy định.")
        driver.save_screenshot("linkedin_login_error.png")
        print("Đã lưu ảnh chụp màn hình lỗi vào file 'linkedin_login_error.png'")
        return False
    except Exception as e:
        print(f"Lỗi không xác định trong quá trình đăng nhập: {e}")
        driver.save_screenshot("linkedin_login_exception.png")
        return False
def create_undetected_driver():
    """Tạo undetected ChromeDriver đã được tối ưu để pass các bài test"""
    options = uc.ChromeOptions()
    prefs = {
        "profile.default_content_setting_values.notifications": 1,
        "profile.default_content_setting_values.geolocation": 1,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=en-US,en")
    driver = uc.Chrome(options=options)
    driver.implicitly_wait(15)
    return driver

def human_type(element, text):
    """Mô phỏng hành vi gõ phím của người thật"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def random_delay(min_seconds=1, max_seconds=3):
    """Tạo delay ngẫu nhiên với human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_scroll(driver):
    """Scroll một cách tự nhiên như người thật"""
    scroll_pause_time = random.uniform(0.5, 1.5)
    scroll_distance = random.randint(300, 800)
    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    time.sleep(scroll_pause_time)

def login_to_linkedin(driver, email, password):
    """Hàm xử lý logic đăng nhập vào LinkedIn đã được tối ưu."""
    print(f"Đang tiến hành đăng nhập với tài khoản: {email}...")
    try:
        print("Đang tìm ô nhập email...")
        email_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        email_field.clear()
        email_field.click()
        human_type(email_field, email)
        print("Đã nhập email.")
        random_delay(0.5, 1)

        print("Đang tìm ô nhập mật khẩu...")
        password_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_field.clear()
        password_field.click()
        human_type(password_field, password)
        print("Đã nhập mật khẩu.")
        random_delay(0.5, 1)

        print("Đang tìm nút 'Sign in'...")
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        sign_in_button.click()
        
        print("Đã nhấn nút đăng nhập, đang chờ xác nhận...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "global-nav-typeahead"))
        )
        print("Đăng nhập thành công! ✅")
        return True

    except TimeoutException:
        print("Lỗi: Không tìm thấy các thành phần để đăng nhập trong thời gian quy định.")
        driver.save_screenshot("linkedin_login_error.png")
        print("Đã lưu ảnh chụp màn hình lỗi vào file 'linkedin_login_error.png'")
        return False
    except Exception as e:
        print(f"Lỗi không xác định trong quá trình đăng nhập: {e}")
        driver.save_screenshot("linkedin_login_exception.png")
        return False

def scroll_to_bottom(driver):
    """Scroll xuống cuối trang nhiều lần để trigger lazy loading"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_delay(2, 3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def click_show_more_button(driver, timeout=10):
    """Tìm và click nút "Show more results" một cách hiệu quả và đáng tin cậy."""
    try:
        show_more_button_xpath = "//button[.//span[normalize-space()='Show more results' or normalize-space()='Hiển thị thêm kết quả']]"
        print("🔍 Đang tìm nút 'Show more results'...")
        wait = WebDriverWait(driver, timeout)
        button = wait.until(
            EC.element_to_be_clickable((By.XPATH, show_more_button_xpath))
        )
        print("✅ Tìm thấy nút 'Show more results'.")
        try:
            ActionChains(driver).move_to_element(button).pause(0.5).click().perform()
            print("✅ Đã click nút bằng ActionChains.")
        except Exception:
            print("⚠️ ActionChains thất bại, thử click bằng JavaScript...")
            driver.execute_script("arguments[0].click();", button)
            print("✅ Đã click nút bằng JavaScript.")
        print("⏳ Đang chờ nội dung mới tải...")
        time.sleep(random.uniform(3, 5))
        return True
    except TimeoutException:
        print("❌ Không tìm thấy nút 'Show more results' hoặc nút không thể click trong thời gian chờ.")
        return False
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")
        return False

def save_profiles_to_file(profiles, filename="linkedin_profiles.json"):
    """Lưu danh sách profile vào file JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        print(f"✅ Đã lưu {len(profiles)} profiles vào {filename}")
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")


def logout_from_linkedin(driver):
    """
    Đăng xuất khỏi LinkedIn một cách an toàn.

    Args:
        driver: selenium webdriver instance đã đăng nhập.

    Returns:
        True nếu đăng xuất thành công, False nếu có lỗi.
    """


    print("\n🔄 Đang tiến hành đăng xuất khỏi LinkedIn...")

   
    wait = WebDriverWait(driver, 20)

    # Bước 1: Tìm và click vào nút "Me"
    print("🔍 Tìm và click vào icon 'Me' (menu người dùng)...")
    try:
        me_icon = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(@class, 'global-nav__primary-link-me-menu-trigger')]"
            ))
        )
    except TimeoutException:
        print("❌ Không tìm thấy icon 'Me'. Thử với ID mặc định...")
        me_icon = wait.until(EC.element_to_be_clickable((By.ID, "global-nav-dropdown-button")))
    
    me_icon.click()
    print("✅ Đã mở menu người dùng.")

    time.sleep(random.uniform(1, 2))  # Đợi menu mở ra

    # Bước 2: Click vào nút 'Đăng xuất' hoặc 'Sign Out'
    print("🔍 Tìm nút 'Đăng xuất' hoặc 'Sign Out'...")
    signout_xpath = "//a[contains(@href, '/m/logout/') or contains(text(), 'Sign Out') or contains(text(), 'Đăng xuất')]"

    sign_out_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, signout_xpath))
    )

    driver.execute_script("arguments[0].scrollIntoView();", sign_out_button)
    sign_out_button.click()
    print("✅ Đã click nút 'Sign Out'.")

  
    print("🎉 Đăng xuất thành công!")
    return True

def expand_and_collect_all_urls(driver, company_url):
    """Mở rộng danh sách nhân viên và thu thập tất cả URL profile."""
    try:
        print(f"🌐 Truy cập trang people của công ty: {company_url}")
        driver.get(company_url)
        random_delay(5, 8)
        print("\n🚀 Bắt đầu Giai đoạn 1: Mở rộng danh sách bằng cách click 'Show More'...")
        click_count = 0
        max_clicks = 99
        while click_count < max_clicks:
            was_button_clicked = click_show_more_button(driver, timeout=7)
            if was_button_clicked:
                click_count += 1
                print(f"👍 Đã click 'Show More' lần thứ {click_count}.")
                random_delay(2, 4)
            else:
                print("🏁 Hoàn tất mở rộng! Không còn nút 'Show More'.")
                break
        if click_count >= max_clicks:
            print(f"⚠️ Đã đạt giới hạn {max_clicks} lần click.")

        print("\n🚀 Bắt đầu Giai đoạn 2: Thu thập tất cả profile URLs...")
        print("...cuộn trang để đảm bảo tất cả profiles đều được tải...")
        scroll_to_bottom(driver)
        random_delay(3, 5)

        try:
            profile_urls = []
            ul_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.display-flex.list-style-none.flex-wrap'))
            )
            a_tags = ul_element.find_elements(By.TAG_NAME, 'a')
            print(f"🔍 Tìm thấy tổng cộng {len(a_tags)} thẻ <a> sau khi mở rộng.")

            for a in a_tags:
                href = a.get_attribute("href")
                name_and_title = a.text.strip().replace('\n', ' ')
                if href and "/in/" in href and "linkedin.com" in href:
                    profile_urls.append({'url': href, 'text': name_and_title})

            seen_urls = set()
            unique_profiles = []
            for profile in profile_urls:
                if profile['url'] not in seen_urls:
                    seen_urls.add(profile['url'])
                    unique_profiles.append(profile)
            
            print(f"✅ Thu thập được {len(unique_profiles)} profile unique.")
            return unique_profiles

        except Exception as e:
            print(f"❌ Lỗi khi thu thập danh sách profile cuối cùng: {e}")
            return []

    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng trong hàm expand_and_collect_all_urls: {e}")
        import traceback
        traceback.print_exc()
        return []

def scrape_profile_details(driver, profile_url):
    """
    Truy cập URL của một profile và trích xuất thông tin chi tiết từ thẻ div.ph5.
    Hàm này được thiết kế để chống lỗi, nếu một trường không tìm thấy, nó sẽ tiếp tục
    với các trường khác mà không làm dừng chương trình.
    """
    print(f"\n scraping: {profile_url}")
    driver.get(profile_url)
    # Tăng thời gian chờ để đảm bảo trang profile tải đầy đủ
    random_delay(5, 8)

    profile_data = {'url': profile_url}

    try:
        # Chờ cho container chính (div.ph5) được tải
        wait = WebDriverWait(driver, 20)
        main_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5"))
        )
        
        # Hàm helper để lấy text của element một cách an toàn
        def get_element_text(container, by, value):
            try:
                # Dùng dấu "." ở đầu XPath để tìm kiếm trong container thay vì cả trang
                if by == By.XPATH:
                    return container.find_element(by, "." + value).text.strip()
                return container.find_element(by, value).text.strip()
            except NoSuchElementException:
                return None

        # 1. Tên Profile (lấy từ thẻ h1)
        profile_data['name'] = get_element_text(main_container, By.TAG_NAME, "h1")
        
        # 2. Headline (thẻ div với class đặc trưng)
        profile_data['headline'] = get_element_text(main_container, By.CSS_SELECTOR, "div.text-body-medium.break-words")
        
        # 3. Vị trí
        profile_data['location'] = get_element_text(main_container, By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light.break-words")
        
        # 4. Công ty & Trường học (dùng XPath với aria-label là cách ổn định nhất)
        profile_data['current_company'] = get_element_text(main_container, By.XPATH, "//button[starts-with(@aria-label, 'Current company:')]//span[contains(@class, 'hoverable-link-text')]")
        profile_data['education'] = get_element_text(main_container, By.XPATH, "//button[starts-with(@aria-label, 'Education:')]//span[contains(@class, 'hoverable-link-text')]")
        
        # 5. Số lượng connections (tìm li có chứa chữ "connections")
        # profile_data['connections'] = get_element_text(main_container, By.XPATH, "//li[contains(., 'connections')]")
        
        print("  ✅ Đã trích xuất thông tin:")
        # In ra dict vừa lấy được để dễ theo dõi
        print(json.dumps(profile_data, indent=4, ensure_ascii=False))

    except TimeoutException:
        print(f"  ❌ Lỗi: Timeout khi chờ trang {profile_url} tải.")
        profile_data['error'] = 'Page load timeout'
    except Exception as e:
        print(f"  ❌ Lỗi không xác định khi scrape profile {profile_url}: {e}")
        profile_data['error'] = str(e)
        
    return profile_data

def get_all_profile_details(driver, profiles_list):
    """
    Nhận vào danh sách các đối tượng profile (chứa URL) và lặp qua từng URL
    để cào data chi tiết.
    """
    all_profiles_data = []
    total_profiles = len(profiles_list)
    
    for i, profile in enumerate(profiles_list):
        print(f"\n{'='*20} [ Đang xử lý profile {i+1}/{total_profiles} ] {'='*20}")
        # profile là một dict dạng {'url': '...', 'text': '...'}
        profile_url = profile['url']
        
        # Gọi hàm cào data chi tiết
        detailed_data = scrape_profile_details(driver, profile_url)
        
        all_profiles_data.append(detailed_data)
        
        # Lưu file sau mỗi 10 profiles để phòng trường hợp bị lỗi giữa chừng
        if (i + 1) % 10 == 0 and i + 1 < total_profiles:
            print(f"\n--- Tự động lưu tiến trình sau {i+1} profiles ---")
            save_profiles_to_file(all_profiles_data, "linkedin_detailed_profiles_backup.json")
            
    return all_profiles_data
def test():
    ACCOUNT_LIST = [
   
        {
            "LINKEDIN_EMAIL": "ReevaMckinneyvcz96680h@cwhats.us",
            "LINKEDIN_PASSWORD": "lamtruongphu2003"
        }
    ]

    COMPANY_URL = "https://www.linkedin.com/company/tiger-tribe-heineken/people/"

    for account in ACCOUNT_LIST:
        email = account["LINKEDIN_EMAIL"]
        password = account["LINKEDIN_PASSWORD"]

        print(f"\n🔐 Đăng nhập với tài khoản: {email}")
        driver = smart_linkedin_login(email, password)  # 👉 Hàm này cần tự tạo driver mới và trả về

        if driver:
            try:
                time.sleep(4)
                print("✅ Đăng nhập thành công! Truy cập công ty...")
                driver.get(COMPANY_URL)
                time.sleep(3)

                # 👉 TODO: Thêm hành động scrape hoặc tương tác tại đây nếu cần

                logout_from_linkedin(driver)
                print("🔁 Đã đăng xuất. Đóng trình duyệt hiện tại...\n")
                time.sleep(2)

            except Exception as e:
                print(f"❌ Lỗi khi thực hiện với {email}: {e}")
            finally:
                driver.quit()  # 💡 Quan trọng: đóng browser sau khi dùng xong

        else:
            print(f"❌ Không thể đăng nhập với {email}, bỏ qua.\n")

        # Nghỉ một chút để tránh bị rate-limit
        time.sleep(5)

def main():
    # Thông tin đăng nhập
    ACCOUNT_LIST = [
        {
            "LINKEDIN_EMAIL": "CandidaPierredgq33321h@liii.us",
            "LINKEDIN_PASSWORD": "lamtruongphu2003"
        },
        {
            "LINKEDIN_EMAIL": "ReevaMckinneyvcz96680h@cwhats.us",
            "LINKEDIN_PASSWORD": "lamtruongphu2003"
        }
    ]
    COMPANY_URL = "https://www.linkedin.com/company/tiger-tribe-heineken/people/"
    
    driver = None
    
    try:
    
       
        # print("Đang khởi tạo Undetected ChromeDriver...")
        driver = smart_linkedin_login(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
        time.sleep(4)
        # logout_from_linkedin(driver)
        # driver = create_undetected_driver()
        # print("Đang truy cập https://www.linkedin.com/login...")
        # driver.get("https://www.linkedin.com/login")
        
        # # Đăng nhập
        # login_successful = login_to_linkedin(driver, LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
        
        # if not login_successful:
        #     print("❌ Đăng nhập thất bại. Thoát chương trình.")
        #     return
        
        # --- BƯỚC 1: Lấy danh sách URL ---
        list_of_profile_urls = expand_and_collect_all_urls(driver, COMPANY_URL)
        
        if not list_of_profile_urls:
            print("❌ Không thu thập được URL profile nào. Dừng chương trình.")
            return
            
        # Lưu danh sách URL ra file để backup
        save_profiles_to_file(list_of_profile_urls, "collected_profile_urls.json")
        
        # # --- BƯỚC 2 (MỚI): Cào data chi tiết từ mỗi URL ---
        print("\n\n" + "="*50)
        print("🚀 BẮT ĐẦU CÀO DATA CHI TIẾT TỪ CÁC PROFILES")
        print("="*50 + "\n")
        
        # Truyền driver và danh sách URL vào hàm mới
        detailed_profiles = get_all_profile_details(driver, list_of_profile_urls)

        print("\n\n" + "="*50)
        print("✅ HOÀN TẤT THU THẬP DATA CHI TIẾT!")
        print("="*50 + "\n")
        
        if detailed_profiles:
            # Lưu kết quả cuối cùng ra file
            save_profiles_to_file(detailed_profiles, "linkedin_detailed_profiles_final.json")
        else:
            print("❌ Không thu thập được thông tin chi tiết nào.")

        print("\nTrình duyệt sẽ được giữ mở để bạn kiểm tra...")
        print("Nhấn Ctrl+C trong terminal để thoát và đóng trình duyệt.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng chương trình theo yêu cầu của người dùng.")
        
    except Exception as e:
        print(f"❌ Lỗi không xác định trong hàm main: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔐 Đang đóng trình duyệt...")
            driver.quit()