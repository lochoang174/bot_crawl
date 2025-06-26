from services.database import get_db_manager
from typing import Dict

PROFILE_COLLECTION = "profile_details"

class ProfileRepository:
    def __init__(self):
        db = get_db_manager()
        if not db.connect():
            raise Exception("Failed to connect to the database")
        
        self.collection = get_db_manager().get_collection(PROFILE_COLLECTION)
        if self.collection is None:
            raise Exception(f"Failed to get collection: {PROFILE_COLLECTION}")

    def save_profile(self, profile_data: Dict):
        """
        Save profile details to the database.
        """
        try:
            result = self.collection.insert_one(profile_data)
            print(f"✅ Đã lưu thông tin profile vào database với ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Lỗi khi lưu thông tin profile vào database: {e}")
            return None