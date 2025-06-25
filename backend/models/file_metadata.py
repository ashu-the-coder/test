from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, Union, Dict, Any
from datetime import datetime

class FileMetadata(BaseModel):
    filename: str
    user: Union[str, Dict[str, Any]] = Field(description="Username as string or user object")
    size: Optional[int] = None
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    content_type: Optional[str] = None
    file_hash: str
    transaction_hash: str
    user_type: Optional[str] = "individual"  # "individual" or "enterprise"
    enterprise_id: Optional[str] = None  # Only for enterprise users
    user_id: Optional[str] = None  # Normalized user identifier

    @root_validator(pre=True)
    def process_user_data(cls, values):
        """Process user data and extract necessary fields"""
        user = values.get('user')
        
        # Extract enterprise_id if user is a dict
        if isinstance(user, dict):
            if 'enterprise_id' in user:
                values['enterprise_id'] = user['enterprise_id']
                values['user_type'] = 'enterprise'
            
            # Extract username/user_id
            if 'username' in user:
                values['user_id'] = user['username'].lower()
            elif 'user_id' in user:
                values['user_id'] = user['user_id'].lower()
        else:
            # For string users (B2C)
            values['user_id'] = str(user).lower()
            values['user_type'] = 'individual'
            
        return values
    
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