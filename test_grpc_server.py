import time
import grpc
from concurrent import futures
import sys
import os
from scraper.my_network_scraper import LinkedInMyNetworkScraper
from scraper.scraper_management import LinkedInScraperManager
from services.edit_profile import LinkedInProfileViewer

sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))
from proto import bot_pb2
from proto import bot_pb2_grpc

# Trạng thái các bot đang chạy
active_bots = {}

class BotServiceServicer(bot_pb2_grpc.BotServiceServicer):
    def StreamBotCrawlUrl(self, request_iterator, context):
        print("request_iterator:", request_iterator)
        try:
            for command in request_iterator:
                print(f"📥 Received command: {command}")
                bot_id = command.bot_id
                cmd_type = command.type
                print(f"📥 Received command: {cmd_type} for bot_id={bot_id}")
                account = {
                    "LINKEDIN_EMAIL": "edwardwilson3512a47@gualues.com",
                    "LINKEDIN_PASSWORD": "Truong3979"
                }
                company_names = ["Vietnam", "VNG"]  
                if cmd_type == bot_pb2.BotCommand.START:
                    try:
                        scraper = LinkedInScraperManager(id=bot_id)
                        active_bots[bot_id] = scraper
                        print("🚀 Khởi tạo LinkedIn Scraper...")

                        if not scraper.initialize_driver():
                            print("❌ Không thể khởi tạo driver")
                            return

                        if not scraper.login(account["LINKEDIN_EMAIL"], account["LINKEDIN_PASSWORD"]):
                            print("❌ Đăng nhập thất bại")
                            return

                        print("✅ Đăng nhập thành công! Bắt đầu scraping...")

                        # Stream logs from expand_and_collect_all_urls
                        # for log in scraper.my_connect_scraper.expand_and_collect_all_urls(bot_id=bot_id):
                        #     yield log

                        # print("✅ Đăng nhập thành công! Bắt đầu scraping...")
        
                        
                        
                        for index, company_name in enumerate(company_names):  # Iterate through the company names with index
                            print(f"\n🏢 Đang xử lý công ty: {company_name}")
                            edit_profile = LinkedInProfileViewer(scraper.driver, company_name=company_name)
                            
                            while True:  # Recursive loop
                                # Scrape my connect profiles
                                detailed_profiles = scraper.scrape_my_connect_profiles(bot_id=bot_id)
                                
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

                elif cmd_type == bot_pb2.BotCommand.STOP:
                    print(f"🛑 Received stop command for bot_id={bot_id}")
                    if active_bots.get(bot_id):
                        scraper = active_bots[bot_id]
                        scraper.set_stop()
                        print(f"🛑 Bot {bot_id} has been stopped.")
                        scraper.cleanup()
                    else:
                        yield bot_pb2.BotLog(
                            bot_id=bot_id,
                            message=f"[{bot_id}] ⚠️ No running bot found to stop."
                        )

        except Exception as e:
            print(f"❌ Error in StreamBotLogs: {e}")
            yield bot_pb2.BotLog(
                bot_id="unknown",
                message=f"❌ Error occurred: {str(e)}"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bot_pb2_grpc.add_BotServiceServicer_to_server(BotServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
