"""
Model cho face vector
"""
from datetime import datetime
from typing import List, Optional


class FaceVector:
    """Model cho face vector"""

    def __init__(
        self,
        url: str,
        name: str,
        picture:str,
        headline: Optional[str],
        location: Optional[str],
        current_company: Optional[str],
        vector: List[float],
        education: Optional[str] = None,
        created_at: Optional[str] = None
    ) -> None:
        self.url = url
        self.name = name
        self.headline = headline
        self.location = location
        self.current_company = current_company
        self.education = education
        self.vector = vector
        self.picture = picture
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Chuyển object thành dictionary để lưu vào Elasticsearch"""
        return {
            "url": self.url,
            "name": self.name,
            "picture":self.picture,
            "headline": self.headline,
            "location": self.location,
            "current_company": self.current_company,
            "education": self.education,
            "vector": self.vector,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FaceVector":
        """Tạo object từ dictionary Elasticsearch"""
        return cls(
            url=data.get("url", ""),
            name=data.get("name", ""),
            headline=data.get("headline"),
            location=data.get("location"),
            current_company=data.get("current_company"),
            education=data.get("education"),
            vector=data.get("vector", []),
            created_at=data.get("created_at")
        )

    def __repr__(self) -> str:
        return f"<FaceVector name={self.name} url={self.url}>"
