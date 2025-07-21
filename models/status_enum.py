from enum import Enum

class UrlStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"
    PROCESSING = "processing"