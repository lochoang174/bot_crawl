import time
from scraper.scraper_management import LinkedInScraperManager
from services.driver_management import ChromeDriverManager
import time


def main():
    """Hàm main để chạy scraper"""
    ACCOUNT_LIST = [
     
        {
            "LINKEDIN_EMAIL": "EmmyWhiteheadvaq35799d@bizdir.us",
            "LINKEDIN_PASSWORD": "lamtruongphu2003"
        }
    ]
    
    COMPANY_URL = "https://www.linkedin.com/company/tiger-tribe-heineken/people/"
    
    # Sử dụng tài khoản đầu tiên
    account = ACCOUNT_LIST[0]
    scraper = LinkedInScraperManager()
    
    try:
        print("🚀 Khởi tạo LinkedIn Scraper...")
        
        if not scraper.initialize_driver():
            print("❌ Không thể khởi tạo driver")
            return
        
        if not scraper.login(account["LINKEDIN_EMAIL"], account["LINKEDIN_PASSWORD"]):
            print("❌ Đăng nhập thất bại")
            return
        
        print("✅ Đăng nhập thành công! Bắt đầu scraping...")
        scraper.search_people("anh")
        # Scrape company profiles
        # detailed_profiles = scraper.scrape_company_profiles(COMPANY_URL)
        
        # if detailed_profiles:
        #     print(f"\n✅ Hoàn tất! Thu thập được {len(detailed_profiles)} profiles chi tiết")
        # else:
        #     print("❌ Không thu thập được thông tin nào")
        
        # print("\nTrình duyệt sẽ được giữ mở để bạn kiểm tra...")
        # print("Nhấn Ctrl+C trong terminal để thoát và đóng trình duyệt.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng chương trình theo yêu cầu của người dùng.")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    # driver = ChromeDriverManager().create_undetected_driver_with_session()
    # driver.get("https://bot.sannysoft.com")
    # test_multiple_accounts()
    main()