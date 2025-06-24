from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductCreate(BaseModel):
    """Model for creating a new product."""
    enterprise_id: str = Field(..., description="ID of the enterprise that owns this product")
    product_name: str = Field(..., description="Name of the product")
    product_type: str = Field(..., description="Type or category of the product")
    unit: str = Field(..., description="Unit of measurement for the product (e.g., kg, piece)")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit code")
    barcode: Optional[str] = Field(None, description="Barcode/UPC/EAN")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enterprise_id": "ent_12345",
                "product_name": "Premium Widget",
                "product_type": "Hardware",
                "unit": "piece",
                "description": "High-quality widget for industrial applications",
                "sku": "PRW-001",
                "barcode": "123456789012"
            }
        }

class Product(BaseModel):
    """Model for product data."""
    id: str = Field(..., description="Unique identifier for the product")
    enterprise_id: str = Field(..., description="ID of the enterprise that owns this product")
    product_name: str = Field(..., description="Name of the product")
    product_type: str = Field(..., description="Type or category of the product")
    unit: str = Field(..., description="Unit of measurement for the product (e.g., kg, piece)")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit code")
    barcode: Optional[str] = Field(None, description="Barcode/UPC/EAN")
    creation_date: datetime = Field(..., description="Date when the product was added")
    ipfs_hash: Optional[str] = Field(None, description="IPFS hash of product metadata")
    blockchain_record: Optional[str] = Field(None, description="Blockchain transaction hash for product registration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod_12345",
                "enterprise_id": "ent_12345",
                "product_name": "Premium Widget",
                "product_type": "Hardware",
                "unit": "piece",
                "description": "High-quality widget for industrial applications",
                "sku": "PRW-001",
                "barcode": "123456789012",
                "creation_date": "2025-06-25T10:30:00",
                "ipfs_hash": "QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx",
                "blockchain_record": "0x1234567890abcdef1234567890abcdef12345678"
            }
        }
