from datetime import datetime

class UrlModel:
    def __init__(self, url: str, status: str = "new", vm: int = 0, createAt: datetime = None, _id=None):
        self._id = _id
        self.url = url
        self.status = status
        self.vm = vm
        self.createAt = createAt or datetime.utcnow()

    def to_dict(self):
        return {
            "url": self.url,
            "status": self.status,
            "vm": self.vm,
            "createAt": self.createAt
        } 