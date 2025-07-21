from typing import List, Dict, Optional
import json
import os
class DataManager:
    """Quản lý việc lưu và load dữ liệu"""
    
    @staticmethod
    def save_profiles_to_file(profiles: List[Dict], filename: str = "linkedin_profiles.json"):
        """Lưu danh sách profile vào file JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            print(f"✅ Đã lưu {len(profiles)} profiles vào {filename}")
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {e}")
    
    @staticmethod
    def load_profiles_from_file(filename: str) -> List[Dict]:
        """Load danh sách profile từ file JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
            print(f"✅ Đã load {len(profiles)} profiles từ {filename}")
            return profiles
        except Exception as e:
            print(f"❌ Lỗi khi load file: {e}")
            return []

