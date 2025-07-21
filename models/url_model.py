from datetime import datetime
from models.status_enum import UrlStatus

class UrlModel:
    def __init__(self, url: str, status: UrlStatus = UrlStatus.PENDING,  bot_id: int = 0, createAt: datetime = None, _id=None):
        self._id = _id
        self.url = url
        self.status = status
        self.bot_id = bot_id
        self.createAt = createAt or datetime.utcnow()

    def to_dict(self):
        return {
            "url": self.url,
            "status": self.status.value,
            "bot_id": self.bot_id,
            "createAt": self.createAt.isoformat()
        }