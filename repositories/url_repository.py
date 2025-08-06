from services.database import get_db_manager
from models.url_model import UrlModel
from bson import ObjectId
from models.status_enum import UrlStatus
from typing import List
from repositories.profile_repository import ProfileRepository

COLLECTION = "urls"

class UrlRepository:
    def __init__(self):
        db = get_db_manager()
        if not db.connect():
            raise Exception("Failed to connect to the database")
        
        self.collection = get_db_manager().get_collection(COLLECTION)
        if self.collection is None:
            raise Exception(f"Failed to get collection: {COLLECTION}")

    def create(self, url: str, status: UrlStatus = UrlStatus.PENDING, bot_id: int = 0):
        # Check if the URL already exists in the database
        if self.exists(url):
            # print(f"⚠️ URL đã tồn tại trong database: {url}")
            return None  # Skip adding the URL if it already exists
        
        model = UrlModel(url=url, status=status, bot_id=bot_id)
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

    def get_urls_by_bot_id(self, bot_id: int) -> List[str]:
        """
        Retrieve all URLs from the database where bot_id matches the given parameter
        and status is 'pending'.
        
        :param bot_id: The bot_id to filter URLs by.
        :return: A list of URLs with the specified bot_id and status 'pending'.
        """
        try:
            # Make sure UrlStatus.PENDING == "pending"
            results_cursor = self.collection.find({"bot_id": 1, "status": "pending"})
            results = list(results_cursor)  # Convert cursor to reusable list

            for doc in results:
                print(doc)

            urls = [doc["url"] for doc in results if "url" in doc]
            print(f"✅ Tìm thấy {len(urls)} URLs với bot_id = 1 và status = 'pending'.")
            return urls

        except Exception as e:
            print(f"❌ Lỗi khi truy vấn URLs với bot_id = {bot_id} và status = 'pending': {e}")
            return []
        
    def update_status_to_processing(self, url: str):
        """
        Update the status of a URL to 'processing'.
        """
        try:
            result = self.collection.update_one({"url": url}, {"$set": {"status": UrlStatus.PROCESSING}})
            if result.modified_count > 0:
                print(f"✅ Đã cập nhật status của URL '{url}' thành 'processing'.")
            else:
                print(f"⚠️ Không tìm thấy URL '{url}' để cập nhật status thành 'processing'.")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật status của URL '{url}' thành 'processing': {e}")

    def update_status_to_done(self, url: str):
        """
        Update the status of a URL to 'done'.
        """
        try:
            result = self.collection.update_one({"url": url}, {"$set": {"status": UrlStatus.DONE}})
            if result.modified_count > 0:
                print(f"✅ Đã cập nhật status của URL '{url}' thành 'done'.")
            else:
                print(f"⚠️ Không tìm thấy URL '{url}' để cập nhật status thành 'done'.")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật status của URL '{url}' thành 'done': {e}")
            
    def update_status_to_pending(self, url: str):
        """
        Update the status of a URL to 'pending'.
        """
        try:
            result = self.collection.update_one({"url": url}, {"$set": {"status": UrlStatus.PENDING}})
            if result.modified_count > 0:
                print(f"✅ Đã cập nhật status của URL '{url}' thành 'pending'.")
            else:
                print(f"⚠️ Không tìm thấy URL '{url}' để cập nhật status thành 'pending'.")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật status của URL '{url}' thành 'pending': {e}")

    def update_status_to_pending_if_not_in_profiles(self, profile_repo: ProfileRepository):
        """
        Update the status of URLs in the 'url' collection to 'pending' if they do not exist
        in the 'profile_details' collection.
        
        :param profile_repo: An instance of ProfileRepository to check profile existence.
        """
        try:
            # Find all URLs in the 'url' collection with status 'processing' or 'done'
            urls_to_check = self.collection.find({"status": {"$in": ["processing", "done"]}})
            
            for url_doc in urls_to_check:
                url = url_doc.get("url")
                if not url:
                    continue
                
                # Check if the profile exists in the 'profile_details' collection
                profile_exists = profile_repo.collection.find_one({"url": url}) is not None
                
                if not profile_exists:
                    # Update the status to 'pending' if the profile does not exist
                    result = self.collection.update_one({"url": url}, {"$set": {"status": "pending"}})
                    if result.modified_count > 0:
                        print(f"✅ Đã cập nhật status của URL '{url}' thành 'pending'.")
                    else:
                        print(f"⚠️ Không thể cập nhật status của URL '{url}' thành 'pending'.")
                else:
                    print(f"✅ Profile đã tồn tại trong 'profile_details' cho URL '{url}'.")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật status thành 'pending': {e}")