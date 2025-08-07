from enum import Enum

class UrlStatus(str, Enum):
    PENDING = "pending"
    DONE = "completed"
    FAILED = "failed"
    PROCESSING = "processing"