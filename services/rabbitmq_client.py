"""
RabbitMQ client wrapper
"""
import logging
import time
import json
import pika
from pika.exceptions import AMQPConnectionError
from config.rabbitmq_config import (
    RABBITMQ_URL,
    FACE_INDEXING_QUEUE,
    MAX_RETRIES,
    RETRY_DELAY
)

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """Class wrapper cho RabbitMQ client"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._initialize_connection()
        
    def _initialize_connection(self):
        """Khởi tạo RabbitMQ connection với retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                self.connection = pika.BlockingConnection(
                    pika.URLParameters(RABBITMQ_URL)
                )
                self.channel = self.connection.channel()
                
                # Khai báo các queue
                self.channel.queue_declare(
                    queue=FACE_INDEXING_QUEUE,
                    durable=True
                )
                
                # self.channel.queue_declare(
                #     queue=CRAWL_QUEUE,
                #     durable=True
                # )
                
                # self.channel.queue_declare(
                #     queue=MAIN_QUEUE,
                #     durable=True
                # )
                
                logger.info("Kết nối RabbitMQ thành công")
                break
                
            except AMQPConnectionError as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Không thể kết nối tới RabbitMQ (lần {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                    time.sleep(RETRY_DELAY)
                else:
                    raise Exception(f"Không thể kết nối tới RabbitMQ sau {MAX_RETRIES} lần thử")
    
    def publish_message(self, queue_name: str, message: dict):
        """
        Gửi message đến queue
        
        Args:
            queue_name (str): Tên queue đích
            message (dict): Message cần gửi
        """
        self.channel.basic_publish(
            exchange='',  # Default exchange
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        logger.info(f"Đã gửi message đến queue {queue_name}")
        
    def start_consuming(self, queue_name: str, callback):
        """
        Bắt đầu lắng nghe messages từ queue
        
        Args:
            queue_name (str): Tên queue cần lắng nghe
            callback: Callback function để xử lý message
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback
        )
        
        logger.info(f"Bắt đầu lắng nghe messages từ queue: {queue_name}")
        self.channel.start_consuming()
        
    def close(self):
        """Đóng kết nối RabbitMQ"""
        if self.connection and self.connection.is_open:
            self.connection.close()
        logger.info("Đã đóng kết nối RabbitMQ") 