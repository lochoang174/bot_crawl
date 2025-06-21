from datetime import datetime
from models.status_enum import UrlStatus

class UrlModel:
    def __init__(self, url: str, status: UrlStatus = UrlStatus.PENDING, vm: int = 0, createAt: datetime = None, _id=None):
        self._id = _id
        self.url = url
        self.status = status
        self.vm = vm
        self.createAt = createAt or datetime.utcnow()

    def to_dict(self):
        return {
            "url": self.url,
            "status": self.status.value,
            "vm": self.vm,
            "createAt": self.createAt.isoformat()
        }