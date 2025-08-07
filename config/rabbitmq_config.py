"""
Cấu hình RabbitMQ
"""
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv('RABBITMQ_URL')
if not RABBITMQ_URL:
    raise ValueError("RABBITMQ_URL environment variable is not set")

# Cấu hình queue
FACE_INDEXING_QUEUE =  os.getenv('FACE_INDEXING_QUEUE')

# Cấu hình retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds 