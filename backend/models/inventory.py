from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class InventoryUpdate(BaseModel):
    """
    Model for updating inventory levels.
    """
    product_id: str = Field(..., description="ID of the product for inventory update")
    location: str = Field(..., description="Location identifier where inventory is stored")
    change_in_quantity: float = Field(..., description="Amount to add or remove from inventory")
    operation: Literal["add", "remove"] = Field(..., description="Operation type: 'add' to increase inventory or 'remove' to decrease")
    notes: Optional[str] = Field(None, description="Additional notes about the inventory change")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_12345",
                "location": "warehouse-a",
                "change_in_quantity": 100.0,
                "operation": "add",
                "notes": "Received new shipment"
            }
        }

class InventoryItem(BaseModel):
    """
    Model for inventory item data.
    """
    id: str = Field(..., description="Unique identifier for the inventory record")
    product_id: str = Field(..., description="ID of the product")
    enterprise_id: str = Field(..., description="ID of the enterprise that owns this inventory")
    location: str = Field(..., description="Location identifier where inventory is stored")
    quantity: float = Field(..., description="Current quantity available at this location")
    last_updated: datetime = Field(..., description="Timestamp when inventory was last updated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "inv_12345",
                "product_id": "prod_12345",
                "enterprise_id": "ent_12345",
                "location": "warehouse-a",
                "quantity": 500.0,
                "last_updated": "2025-06-25T14:30:00"
            }
        }

class InventoryAuditLog(BaseModel):
    """
    Model for tracking inventory changes in the audit log.
    """
    id: str = Field(..., description="Unique identifier for the audit log entry")
    inventory_id: str = Field(..., description="ID of the inventory record")
    product_id: str = Field(..., description="ID of the product")
    enterprise_id: str = Field(..., description="ID of the enterprise")
    location: str = Field(..., description="Location where inventory changed")
    previous_quantity: float = Field(..., description="Quantity before the change")
    new_quantity: float = Field(..., description="Quantity after the change")
    change_amount: float = Field(..., description="Amount added or removed")
    operation: str = Field(..., description="Type of operation performed (add/remove)")
    timestamp: datetime = Field(..., description="When the inventory change occurred")
    user_id: str = Field(..., description="ID of the user who made the change")
    notes: Optional[str] = Field(None, description="Additional notes about the inventory change")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "log_12345",
                "inventory_id": "inv_12345",
                "product_id": "prod_12345",
                "enterprise_id": "ent_12345",
                "location": "warehouse-a",
                "previous_quantity": 400.0,
                "new_quantity": 500.0,
                "change_amount": 100.0,
                "operation": "add",
                "timestamp": "2025-06-25T14:30:00",
                "user_id": "user_12345",
                "notes": "Received new shipment"
            }
        }
