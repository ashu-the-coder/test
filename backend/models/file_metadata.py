from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class FileMetadata(BaseModel):
    filename: str
    user: str = Field(description="Username as string")
    size: Optional[int]
    upload_date: datetime
    content_type: Optional[str]
    file_hash: str
    transaction_hash: str

    @validator('user')
    def validate_user(cls, v):
        if isinstance(v, dict):
            return v.get('username', '')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "example.txt",
                "user": "user123",
                "size": 1024,
                "upload_date": "2023-01-01T00:00:00",
                "content_type": "text/plain",
                "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "transaction_hash": "0x1234..."
            }
        }