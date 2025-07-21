import os
import queue
import sys
import threading
import time
from concurrent import futures

import grpc

from scraper.scraper_management import LinkedInScraperManager
from services.edit_profile import LinkedInProfileViewer

sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))
from proto import bot_pb2, bot_pb2_grpc

# Bot status will now be RUNNING or STOPPED
active_bots = {}

def _run_scraper_task(bot_id: str, log_queue: queue.Queue, scraper: LinkedInScraperManager, company_names: list):
    """
    The scraping task that runs in a separate thread.
    It now checks for the stop signal more frequently.
    """
    try:
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="🚀 Initializing LinkedIn Scraper..."))
        if not scraper.initialize_driver():
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ Driver initialization failed."))
            return

        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="Attempting login..."))
        if not scraper.login():
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ Login failed."))
            return
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ Login successful! Starting scraping..."))

        for index, company_name in enumerate(company_names):
            # This outer check is still valuable to stop between companies
            if scraper.is_stopped():
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🛑 Scraping stopped before processing company: {company_name}."))
                break

            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"\n🏢 Processing company: {company_name} (#{index + 1}/{len(company_names)})"))
            
            # --- MODIFICATION: Pass the scraper instance to the viewer ---
            edit_profile = LinkedInProfileViewer(scraper.driver,  company_name=company_name)

            # This inner loop is still useful, as the blocking functions will now break out of their own internal loops.
          
                # Now, if STOP is called, this function will return early instead of blocking for minutes.
            detailed_profiles = scraper.scrape_my_connect_profiles()

            if scraper.is_stopped(): break

            if detailed_profiles:
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✅ Collected {len(list(detailed_profiles))} profiles from My Network"))
            else:
                
                log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ No more profiles to collect for this company. Moving to next."))
                break # Exit inner loop to go to the next company

            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="🔄 Viewing and editing profile..."))
            # This function will also now return early if a stop is signaled.
            edit_profile.view_and_edit_profile()
            
            if scraper.is_stopped(): break

            # time.sleep(5)

        if not scraper.is_stopped():
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ All scraping tasks completed."))
        else:
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ Scraping task was stopped by command."))

    except Exception as e:
        import traceback
        error_message = f"❌ Unhandled error in scraper thread: {e}\n{traceback.format_exc()}"
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=error_message))
    finally:
        # This thread is ending. Always clean up its resources.
        print(f"[{bot_id}] Scraper task thread finished. Cleaning up resources.")
        scraper.cleanup()
        if bot_id in active_bots:
            # This thread is dead, so remove it from active_bots.
            # A new START command will create a new thread.
            del active_bots[bot_id]
            print(f"[{bot_id}] Bot removed from active list.")

def _run_detail_scraper_task(bot_id: str, log_queue: queue.Queue, scraper: LinkedInScraperManager):
    """
    The detailed scraping task that runs in a separate thread.
    It now checks for the stop signal more frequently.
    """
    try:
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="🚀 Initializing LinkedIn Scraper..."))
        if not scraper.initialize_driver():
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ Driver initialization failed."))
            return

        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="Attempting login..."))
        if not scraper.login():
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ Login failed."))
            return
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="✅ Login successful! Starting scraping..."))

        detailed_profiles = scraper.scrape_profile_details(bot_id= bot_id)

        if scraper.is_stopped():
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="🛑 Scraping stopped before processing profiles."))
            return

        if detailed_profiles:
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✅ Collected {len(detailed_profiles)} detailed profiles."))
        else:
            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message="❌ No profiles collected."))

    except Exception as e:
        import traceback
        error_message = f"❌ Unhandled error in detail scraper thread: {e}\n{traceback.format_exc()}"
        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=error_message))
    finally:
        # This thread is ending. Always clean up its resources.
        print(f"[{bot_id}] Detail scraper task thread finished. Cleaning up resources.")
        scraper.cleanup()
        if bot_id in active_bots:
            # This thread is dead, so remove it from active_bots.
            # A new START command will create a new thread.
            del active_bots[bot_id]
            print(f"[{bot_id}] Bot removed from active list.")

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
                        if bot_id in active_bots:
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ Bot {bot_id} is already running."))
                            continue
                        
                        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✨ Starting new bot {bot_id}..."))
                        
                        # Always create a new scraper and thread for a new START command.
                        # This simplifies state managemen
                        # t immensely.
                        scraper = LinkedInScraperManager(id=bot_id)
                    
                        company_names = ["Vietnam", "VNG", "FPT"]
                        
                        worker_thread = threading.Thread(
                            target=_run_scraper_task,
                            args=(bot_id, log_queue, scraper, company_names),
                            daemon=True # Daemon threads are abruptly stopped when the main program exits
                        )
                        # Store the new scraper and thread
                        active_bots[bot_id] = {"scraper": scraper, "thread": worker_thread}
                        worker_thread.start()

                    elif cmd_type == bot_pb2.BotCommand.STOP:
                        if bot_id in active_bots:
                            scraper = active_bots[bot_id]["scraper"]
                            # This now works because internal functions check the flag.
                            scraper.set_stop() 
                            print(f"🛑 Stop signal sent to bot {bot_id}.")
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🛑 Stop command received. Bot will stop shortly."))
                        else:
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ No running bot found to stop for bot_id={bot_id}."))
            
            except grpc.RpcError:
                print(f"Client disconnected for bot_id={bot_id if bot_id else 'unknown'}.")
                if bot_id and bot_id in active_bots:
                    print(f"Forcing stop for bot {bot_id} due to client disconnect.")
                    active_bots[bot_id]["scraper"].set_stop()
            finally:
                log_queue.put(None)

        command_thread = threading.Thread(target=command_handler)
        command_thread.start()

        while True:
            try:
                log = log_queue.get(timeout=1)
                if log is None:
                    break
                yield log
            except queue.Empty:
                if not context.is_active():
                    print("Client context is inactive. Stopping log stream.")
                    break
            except Exception as e:
                print(f"Error in StreamBotCrawlUrl loop: {e}")
                break

        command_thread.join()
        print(f"StreamBotCrawlUrl for bot_id={bot_id if bot_id else 'unknown'} completed.")
        
        
        command_thread.join()
        print(f"StreamBotCrawlDetail for bot_id={bot_id if bot_id else 'unknown'} completed.")
        
        if bot_id in active_bots:
            del active_bots[bot_id]
        
    def StreamBotCrawlDetail(self, request_iterator, context):
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
                        if bot_id in active_bots:
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ Bot {bot_id} is already running."))
                            continue
                        
                        log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"✨ Starting detail scraper for bot {bot_id}..."))
                        
                        # Always create a new scraper and thread for a new START command.
                        scraper = LinkedInScraperManager(id=bot_id)
                        
                        worker_thread = threading.Thread(
                            target=_run_detail_scraper_task,
                            args=(bot_id, log_queue, scraper),
                            daemon=True # Daemon threads are abruptly stopped when the main program exits
                        )
                        # Store the new scraper and thread
                        active_bots[bot_id] = {"scraper": scraper, "thread": worker_thread}
                        worker_thread.start()

                    elif cmd_type == bot_pb2.BotCommand.STOP:
                        if bot_id in active_bots:
                            scraper = active_bots[bot_id]["scraper"]
                            # This now works because internal functions check the flag.
                            scraper.set_stop() 
                            print(f"🛑 Stop signal sent to bot {bot_id}.")
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"🛑 Stop command received. Bot will stop shortly."))
                        else:
                            log_queue.put(bot_pb2.BotLog(bot_id=bot_id, message=f"⚠️ No running bot found to stop for bot_id={bot_id}."))
            
            except grpc.RpcError:
                print(f"Client disconnected for bot_id={bot_id if bot_id else 'unknown'}.")
                if bot_id and bot_id in active_bots:
                    print(f"Forcing stop for bot {bot_id} due to client disconnect.")
                    active_bots[bot_id]["scraper"].set_stop()
            finally:
                log_queue.put(None)
        
        command_thread = threading.Thread(target=command_handler)
        command_thread.start()
        
        while True:
            try:
                log = log_queue.get(timeout=1)
                if log is None:
                    break
                yield log
            except queue.Empty:
                if not context.is_active():
                    print("Client context is inactive. Stopping log stream.")
                    break
            except Exception as e:
                print(f"Error in StreamBotCrawlDetail loop: {e}")
                break
        
        command_thread.join()
        print(f"StreamBotCrawlDetail for bot_id={bot_id if bot_id else 'unknown'} completed.")
        

        if bot_id in active_bots:
            del active_bots[bot_id]
                
# ... (serve function remains the same, but the shutdown logic can be simplified) ...

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bot_pb2_grpc.add_BotServiceServicer_to_server(BotServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC server started on port 50051")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down gRPC server...")
        # Signal all running bots to stop
        for bot_id, bot_data in list(active_bots.items()):
            print(f"Signaling stop for bot {bot_id} on server shutdown.")
            bot_data["scraper"].set_stop()
            bot_data["thread"].join(timeout=10) # Wait for thread to finish cleanup

        server.stop(0)
    finally:
        print("gRPC server stopped.")


if __name__ == '__main__':
    serve()