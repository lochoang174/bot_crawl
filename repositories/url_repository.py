from services.database import get_db_manager
from models.url_model import UrlModel
from bson import ObjectId

COLLECTION = "url"

class UrlRepository:
    def __init__(self):
        self.collection = get_db_manager().get_collection(COLLECTION)
        if self.collection is None:
            raise Exception(f"Failed to get collection: {COLLECTION}")

    def create(self, url: str, status: str = "new", vm: int = 0):
        model = UrlModel(url=url, status=status, vm=vm)
        result = self.collection.insert_one(model.to_dict())
        return str(result.inserted_id)

    def get_by_id(self, id: str):
        data = self.collection.find_one({"_id": ObjectId(id)})
        return UrlModel(**data) if data else None

    def update_status(self, id: str, status: str):
        return self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}}).modified_count

    def delete(self, id: str):
        return self.collection.delete_one({"_id": ObjectId(id)}).deleted_count

    def find_by_status(self, status: str):
        return [UrlModel(**doc) for doc in self.collection.find({"status": status})] 