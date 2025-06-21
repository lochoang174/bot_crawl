from services.database import get_db_manager
from models.url_model import UrlModel
from bson import ObjectId
from models.status_enum import UrlStatus

COLLECTION = "url"

class UrlRepository:
    def __init__(self):
        db = get_db_manager()
        if not db.connect():
            raise Exception("Failed to connect to the database")
        
        self.collection = get_db_manager().get_collection(COLLECTION)
        if self.collection is None:
            raise Exception(f"Failed to get collection: {COLLECTION}")

    def create(self, url: str, status: UrlStatus = UrlStatus.PENDING, vm: int = 0):
        # Check if the URL already exists in the database
        if self.exists(url):
            print(f"⚠️ URL đã tồn tại trong database: {url}")
            return None  # Skip adding the URL if it already exists

        model = UrlModel(url=url, status=status, vm=vm)
        result = self.collection.insert_one(model.to_dict())
        return str(result.inserted_id)

    def exists(self, url: str) -> bool:
        """Check if a URL already exists in the database."""
        return self.collection.find_one({"url": url}) is not None

    def get_by_id(self, id: str):
        data = self.collection.find_one({"_id": ObjectId(id)})
        return UrlModel(**data) if data else None

    def update_status(self, id: str, status: str):
        return self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}}).modified_count

    def delete(self, id: str):
        return self.collection.delete_one({"_id": ObjectId(id)}).deleted_count

    def find_by_status(self, status: str):
        return [UrlModel(**doc) for doc in self.collection.find({"status": status})]