import time
from scraper.scraper_management import LinkedInScraperManager
from services.driver_management import ChromeDriverManager
import time

    



def test_multiple_accounts():
    """Test với nhiều tài khoản"""
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
        
        scraper = LinkedInScraperManager()
        
        try:
            print(f"\n🔐 Đăng nhập với tài khoản: {email}")
            
            if not scraper.initialize_driver():
                print(f"❌ Không thể khởi tạo driver cho {email}")
                continue
            
            if scraper.login(email, password):
                print("✅ Đăng nhập thành công! Truy cập công ty...")
                scraper.driver.get(COMPANY_URL)
                time.sleep(3)
                company =scraper.company_scraper
                company.expand_and_collect_all_urls("https://www.linkedin.com/company/itviec/people/")
                time.sleep(5)  # Nghỉ giữa các tài khoản

                scraper.logout()
                print("🔁 Đã đăng xuất.")
            else:
                print(f"❌ Không thể đăng nhập với {email}")
                
        except Exception as e:
            print(f"❌ Lỗi khi thực hiện với {email}: {e}")
        finally:
            scraper.cleanup()
            time.sleep(5)  # Nghỉ giữa các tài khoản


def main():
    """Hàm main để chạy scraper"""
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
        
        # Scrape company profiles
        detailed_profiles = scraper.scrape_company_profiles(COMPANY_URL)
        
        if detailed_profiles:
            print(f"\n✅ Hoàn tất! Thu thập được {len(detailed_profiles)} profiles chi tiết")
        else:
            print("❌ Không thu thập được thông tin nào")
        
        print("\nTrình duyệt sẽ được giữ mở để bạn kiểm tra...")
        print("Nhấn Ctrl+C trong terminal để thoát và đóng trình duyệt.")
        
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

    test_multiple_accounts()