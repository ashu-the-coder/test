from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FileMetadata(BaseModel):
    filename: str
    size: Optional[int]
    upload_date: datetime
    content_type: Optional[str]
    file_hash: str
    transaction_hash: str

class User(BaseModel):
    username: str = Field(..., description="Unique username")
    wallet_address: str = Field(..., description="Wallet address for ownership verification")
    files: List[FileMetadata] = Field(default_factory=list, description="List of user's files and metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user123",
                "wallet_address": "0x1234567890abcdef...",
                "files": [
                    {
                        "filename": "example.txt",
                        "size": 1024,
                        "upload_date": "2023-01-01T00:00:00",
                        "content_type": "text/plain",
                        "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "transaction_hash": "0x1234..."
                    }
                ]
            }
        }
