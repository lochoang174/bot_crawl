import time
import grpc
from concurrent import futures
import sys
import os
import threading
import queue  # Import a thread-safe queue
from scraper.scraper_management import LinkedInScraperManager
from services.edit_profile import LinkedInProfileViewer
# ----------------------------------------------------

sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))
from proto import bot_pb2
from proto import bot_pb2_grpc

# Trạng thái các bot đang chạy
# Giờ đây sẽ lưu trữ cả scraper, queue và thread
# Đã thêm trạng thái của bot: RUNNING, STOPPED, PENDING
active_bots = {}

# Hàm này sẽ được chạy trong một thread riêng
def _run_scraper_task(bot_id: str, log_queue: queue.Queue, scraper: LinkedInScraperManager, account: dict, company_names: list):
    """
    Hàm thực hiện công việc scrape dữ liệu.
    Nó sẽ chạy trong một luồng riêng để không chặn server gRPC.
    """
    try:
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="🚀 Initializing LinkedIn Scraper..."))

        if not scraper.driver: # Chỉ initialize driver nếu chưa có
            if not scraper.initialize_driver():
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ Driver initialization failed."))
                return

        # Kiểm tra xem đã login chưa, nếu có thể thì bỏ qua login lại
        # (Đây là một điểm bạn cần cải thiện trong scraper thực tế của mình)
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="Attempting login..."))
        if not scraper.login(account["LINKEDIN_EMAIL"], account["LINKEDIN_PASSWORD"]):
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ Login failed."))
            scraper.cleanup() # Cleanup nếu login thất bại
            return
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ Login successful! Starting scraping..."))

        for index, company_name in enumerate(company_names):
            # if scraper.is_stopped():  # KIỂM TRA CỜ DỪNG TRƯỚC MỖI VÒNG LẶP LỚN
            #     log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🛑 Scraping stopped by command for company: {company_name}."))
            #     break
            print(f"\n[{bot_id}] 🏢 Processing company: {company_name} (#{index + 1}/{len(company_names)})")
                
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"\n🏢 Processing company: {company_name}"))
            edit_profile = LinkedInProfileViewer(scraper.driver, company_name=company_name)
            
            # Vòng lặp bên trong để xử lý đệ quy (hoặc cho đến khi không còn profile)
            # Giả định đây là vòng lặp lấy nhiều trang profile
            while not scraper.is_stopped(): # Luôn kiểm tra cờ dừng
                detailed_profiles = scraper.scrape_my_connect_profiles(bot_id=bot_id)
                
                if detailed_profiles:
                    log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✅ Collected {len(list(detailed_profiles))} profiles from My Network"))
                else:
                    log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ No more profiles to collect for this company."))
                    break # Thoát vòng lặp nội bộ nếu không còn profile
                
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="🔄 Closing modal and editing profile..."))
                edit_profile.view_and_edit_profile()
                
                time.sleep(5) # Khoảng dừng giữa các lần scrape
            
            if scraper.is_stopped(): # Thoát vòng lặp ngoài nếu đã nhận lệnh dừng
                break

        if not scraper.is_stopped(): # Chỉ báo hoàn thành nếu không bị dừng giữa chừng
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ All scraping tasks completed for this session."))

    except Exception as e:
        import traceback
        error_message = f"❌ Unhandled error in scraper thread: {e}\n{traceback.format_exc()}"
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=error_message))
    finally:
        # Quan trọng: Không cleanup ngay lập tức ở đây. 
        # Cleanup sẽ được gọi khi bot bị STOP hoặc khi server tắt
        # log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="Scraper task finished.")) 
        print(f"[{bot_id}] Scraper task thread ended (driver might still be active).")
        scraper.cleanup()
        # Đánh dấu bot là đã dừng trong active_bots để biết trạng thái
        if bot_id in active_bots:
            active_bots[bot_id]["status"] = "STOPPED" # Hoặc "COMPLETED" nếu nó hoàn thành xong

class BotServiceServicer(bot_pb2_grpc.BotServiceServicer):
    def StreamBotCrawlUrl(self, request_iterator, context):
        log_queue = queue.Queue()
        bot_id = None 

        def command_handler():
            nonlocal bot_id
            try:
                for command in request_iterator:
                    bot_id = command.bot_id
                    cmd_type = command.type
                    print(f"📥 Received command: {bot_pb2.BotCommand.CommandType.Name(cmd_type)} for bot_id={bot_id}")

                    if cmd_type == bot_pb2.BotCommand.START:
                        if bot_id in active_bots and active_bots[bot_id]["status"] == "RUNNING":
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ Bot {bot_id} is already running."))
                            continue
                        
                        scraper = None
                        if bot_id in active_bots and active_bots[bot_id]["status"] == "STOPPED":
                            # Bot đã tồn tại và đã dừng, có thể khởi động lại
                            scraper = active_bots[bot_id]["scraper"]
                            # Reset stop event để cho phép nó chạy lại
                            scraper.cleanup() 
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🔄 Resuming bot {bot_id}..."))
                        else:
                            # Bot mới hoàn toàn
                            scraper = LinkedInScraperManager(id=bot_id)
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✨ Starting new bot {bot_id}..."))

                        account = {
                            "LINKEDIN_EMAIL": "edwardwilson3512a47@gualues.com",
                            "LINKEDIN_PASSWORD": "Truong3979"
                        }
                        company_names = ["Vietnam", "VNG", "FPT"] # Thêm 1 công ty để thấy quá trình
                        
                        worker_thread = threading.Thread(
                            target=_run_scraper_task,
                            args=(bot_id, log_queue, scraper, account, company_names)
                        )
                        active_bots[bot_id] = {"scraper": scraper, "thread": worker_thread, "status": "RUNNING"}
                        worker_thread.start()

                    elif cmd_type == bot_pb2.BotCommand.STOP:
                        if bot_id in active_bots and active_bots[bot_id]["status"] == "RUNNING":
                            scraper = active_bots[bot_id]["scraper"]
                            scraper.set_stop()  # Gửi tín hiệu dừng
                            active_bots[bot_id]["status"] = "STOPPED" # Cập nhật trạng thái
                            print(f"🛑 Stop signal sent to bot {bot_id}. Status set to STOPPED.")
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🛑 Stop command received. Bot will stop shortly."))
                            # KHÔNG XÓA bot_id khỏi active_bots để có thể khởi động lại
                            # KHÔNG cleanup ở đây, việc cleanup sẽ do hàm bên trong _run_scraper_task xử lý khi nó kết thúc hoặc khi client ngắt kết nối
                        elif bot_id in active_bots and active_bots[bot_id]["status"] == "STOPPED":
                             log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ Bot {bot_id} is already stopped."))
                        else:
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ No running bot found to stop for bot_id={bot_id}."))
            
            except grpc.RpcError as e:
                # Client ngắt kết nối
                print(f"Client disconnected for bot_id={bot_id if bot_id else 'unknown'}. Error: {e}")
                if bot_id and bot_id in active_bots and active_bots[bot_id]["status"] == "RUNNING":
                    # Nếu client ngắt kết nối khi bot đang chạy, hãy ra lệnh dừng bot đó
                    print(f"Forcing stop for bot {bot_id} due to client disconnect.")
                    print(" Stopping scraper:" + active_bots[bot_id]["scraper"])
                    active_bots[bot_id]["scraper"].set_stop()
                    active_bots[bot_id]["status"] = "STOPPED"
                    # Có thể cân nhắc gọi cleanup ở đây nếu muốn giải phóng tài nguyên ngay lập tức
                    # active_bots[bot_id]["scraper"].cleanup() 
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id if bot_id else "unknown", message=f"Client disconnected. Bot will stop if running."))

            finally:
                # Đặt một tin nhắn đặc biệt vào queue để báo hiệu command_handler đã kết thúc
                # Điều này giúp StreamBotCrawlUrl biết khi nào nên dừng việc gửi log
                log_queue.put(None)

        command_thread = threading.Thread(target=command_handler)
        command_thread.start()

        # Vòng lặp chính của luồng gRPC: chỉ lấy log từ queue và gửi cho client
        while True:
            try:
                # Chờ log từ worker thread hoặc command_handler
                log = log_queue.get(timeout=1) 
                
                # Nếu nhận được tín hiệu kết thúc từ command_handler (tức client đã ngắt kết nối)
                if log is None:
                    print("Command handler finished (client disconnected). Closing log stream.")
                    break # Thoát vòng lặp gửi log
                
                yield log

            except queue.Empty:
                # Nếu queue rỗng, kiểm tra xem client còn kết nối không
                if not context.is_active():
                    print("Client context is inactive. Stopping log stream.")
                    # Khi client ngắt kết nối, luồng command_handler sẽ tự động xử lý việc dừng bot
                    break # Thoát vòng lặp gửi log
                
                # Nếu context vẫn active nhưng không có log, tiếp tục vòng lặp

            except Exception as e:
                print(f"Error in StreamBotCrawlUrl loop: {e}")
                break # Thoát vòng lặp nếu có lỗi không mong muốn

        # Đảm bảo luồng command_handler kết thúc trước khi hàm StreamBotCrawlUrl trả về
        command_thread.join()
        print(f"StreamBotCrawlUrl for bot_id={bot_id if bot_id else 'unknown'} completed.")
    def StreamBotCrawlDetail(self, request_iterator, context):
        for command in request_iterator:
                bot_id = command.bot_id
                cmd_type = command.type
                print(bot_id)
                print(cmd_type)
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bot_pb2_grpc.add_BotServiceServicer_to_server(BotServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC server started on port 50051")
    server.start()
    
    try:
        while True:
            time.sleep(86400) # Giữ server chạy
    except KeyboardInterrupt:
        print("\nShutting down gRPC server...")
        # Cleanup tất cả các bot đang hoạt động khi server tắt
        for bot_id, bot_data in active_bots.items():
            if bot_data["scraper"]:
                print(f"Cleaning up bot {bot_id} on server shutdown.")
                bot_data["scraper"].set_stop() # Đảm bảo worker thread dừng
                bot_data["thread"].join(timeout=5) # Chờ worker thread kết thúc
                if bot_data["scraper"].driver: # Chỉ cleanup nếu driver còn tồn tại
                    bot_data["scraper"].cleanup()
        server.stop(0)
    finally:
        print("gRPC server stopped.")

if __name__ == '__main__':
    serve()