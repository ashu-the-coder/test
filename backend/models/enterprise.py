from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class AdminDetails(BaseModel):
    """Model for enterprise administrator details."""
    name: str = Field(..., description="Administrator's name")
    email: str = Field(..., description="Administrator's email")
    phone: Optional[str] = Field(None, description="Administrator's phone number")
    role: str = Field("admin", description="Administrator's role in the enterprise")

class EnterpriseCreate(BaseModel):
    """Model for creating a new enterprise."""
    enterprise_name: str = Field(..., description="Name of the enterprise")
    industry: str = Field(..., description="Industry sector of the enterprise")
    admin_details: AdminDetails = Field(..., description="Details of the enterprise administrator")
    address: Optional[str] = Field(None, description="Enterprise physical address")
    website: Optional[str] = Field(None, description="Enterprise website")
    description: Optional[str] = Field(None, description="Enterprise description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_name": "Acme Corp",
                "industry": "Manufacturing",
                "admin_details": {
                    "name": "John Doe",
                    "email": "john@acmecorp.com",
                    "phone": "+1234567890",
                    "role": "admin"
                },
                "address": "123 Business Ave, Industry Park, CA 90210",
                "website": "https://acmecorp.com",
                "description": "Leading manufacturer of innovative widgets"
            }
        }

class Enterprise(BaseModel):
    """Model for enterprise data."""
    id: str = Field(..., description="Unique identifier for the enterprise")
    enterprise_name: str = Field(..., description="Name of the enterprise")
    industry: str = Field(..., description="Industry sector of the enterprise")
    admin_details: AdminDetails = Field(..., description="Details of the enterprise administrator")
    address: Optional[str] = Field(None, description="Enterprise physical address")
    website: Optional[str] = Field(None, description="Enterprise website")
    description: Optional[str] = Field(None, description="Enterprise description")
    creation_date: datetime = Field(..., description="Date when the enterprise was registered")
    wallet_address: Optional[str] = Field(None, description="Enterprise blockchain wallet address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ent_12345",
                "enterprise_name": "Acme Corp",
                "industry": "Manufacturing",
                "admin_details": {
                    "name": "John Doe",
                    "email": "john@acmecorp.com",
                    "phone": "+1234567890",
                    "role": "admin"
                },
                "address": "123 Business Ave, Industry Park, CA 90210",
                "website": "https://acmecorp.com",
                "description": "Leading manufacturer of innovative widgets",
                "creation_date": "2025-06-25T10:30:00",
                "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
            }
        }
