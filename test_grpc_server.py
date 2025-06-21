import time
import grpc
from concurrent import futures
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))
from proto import bot_pb2
from proto import bot_pb2_grpc

# Trạng thái các bot đang chạy
active_bots = {}

class BotServiceServicer(bot_pb2_grpc.BotServiceServicer):
    def StreamBotLogs(self, request_iterator, context):
        try:
            for command in request_iterator:
                bot_id = command.bot_id
                cmd_type = command.type
                print(f"📥 Received command: {cmd_type} for bot_id={bot_id}")

                if cmd_type == bot_pb2.BotCommand.START:
                    if bot_id in active_bots and active_bots[bot_id]:
                        yield bot_pb2.BotLog(
                            bot_id=bot_id,
                            message=f"[{bot_id}] ⚠️ Bot is already running."
                        )
                        continue
                    
                    active_bots[bot_id] = True
                    for i in range(30):
                        # Nếu bị STOP giữa chừng → thoát
                        if not active_bots.get(bot_id):
                            yield bot_pb2.BotLog(
                                bot_id=bot_id,
                                message=f"[{bot_id}] 🛑 Bot was stopped manually at step {i+1}"
                            )
                            break

                        message = f"[{bot_id}] running... step {i+1}/30"
                        print(f"⏱️ Sending: {message}")
                        yield bot_pb2.BotLog(bot_id=bot_id, message=message)
                        time.sleep(1)

                    if active_bots.get(bot_id):
                        yield bot_pb2.BotLog(
                            bot_id=bot_id,
                            message=f"[{bot_id}] ✅ Finished all 30 steps"
                        )

                    active_bots[bot_id] = False

                elif cmd_type == bot_pb2.BotCommand.STOP:
                    if active_bots.get(bot_id):
                        active_bots[bot_id] = False
                        yield bot_pb2.BotLog(
                            bot_id=bot_id,
                            message=f"[{bot_id}] ❌ STOP command received, stopping bot."
                        )
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
