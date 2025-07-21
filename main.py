import time
from scraper.scraper_management import LinkedInScraperManager
from services.driver_management import ChromeDriverManager
from services.edit_profile import LinkedInProfileViewer
from repositories.url_repository import UrlRepository
from repositories.profile_repository import ProfileRepository

def test_multiple_accounts():
    """Test với nhiều tài khoản"""
    ACCOUNT_LIST = [ 
        {
            "LINKEDIN_EMAIL": "ClarieBarbourclf38421z@cwhats.us",
            "LINKEDIN_PASSWORD": "Truong3979"
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

def my_connect_scraper():
    """Hàm main để chạy scraper"""
    ACCOUNT_LIST = [
        {
            "LINKEDIN_EMAIL": "heidivitaleqxo77592s@teom.us",
            "LINKEDIN_PASSWORD": "Truong3979"
        },
    ]
    
    # Array of company names
    company_names = ["Vietnam", "VNG"]
   
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
        
        # scraper.driver.get("https://www.linkedin.com/mynetwork")
        # time.sleep(3)
        # edit_profile = LinkedInProfileViewer(scraper.driver, company_name="hello")
        # edit_profile.view_and_edit_profile()

        
        for index, company_name in enumerate(company_names):  # Iterate through the company names with index
            print(f"\n🏢 Đang xử lý công ty: {company_name}")
            edit_profile = LinkedInProfileViewer(scraper.driver, company_name=company_name)
            
            while True:  # Recursive loop
                # Scrape my connect profiles
                detailed_profiles = scraper.scrape_my_connect_profiles()
                
                if detailed_profiles:
                    print(f"✅ Hoàn tất! Thu thập được {len(list(detailed_profiles))} profiles chi tiết từ My Network")
                else:
                    print("❌ Không thu thập được thông tin nào từ My Network")
                
                # Click the close modal button and edit profile
                print("🔄 Đang đóng modal và chỉnh sửa profile...")
                edit_profile.view_and_edit_profile()
                
                # Add a delay to avoid overwhelming the server
                time.sleep(5)
                
                # Check if this is the last company in the array
                if index == len(company_names) - 1:
                    print(f"🏢 Công ty cuối cùng: {company_name}. Tiếp tục thu thập profiles...")
                    continue  # Continue scraping profiles for the last company
                
                print(f"🏢 Đã hoàn thành xử lý công ty: {company_name}")
                break 
        
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng chương trình theo yêu cầu của người dùng.")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()
        
def test_scraper():
    url_repo = UrlRepository()
    profile_repo = ProfileRepository()

    # Update status to 'pending' for URLs not in 'profile_details'
    url_repo.update_status_to_pending_if_not_in_profiles(profile_repo)
        
        
        
if __name__ == "__main__":
    # driver = ChromeDriverManager().create_undetected_driver_with_session()
    # driver.get("https://bot.sannysoft.com")
    # my_connect_scraper()
    # test_scraper()
    # test_multiple_accounts()