from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class AuditLog(BaseModel):
    """Model for audit trail records"""
    id: Optional[str] = None
    entity_type: str = Field(..., description="Type of entity being modified (batch, product, inventory, etc.)")
    entity_id: str = Field(..., description="ID of the entity that was modified")
    field_changed: str = Field(..., description="Name of the field that was changed")
    old_value: Any = Field(..., description="Previous value of the field")
    new_value: Any = Field(..., description="New value of the field")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the change occurred")
    changed_by: str = Field(..., description="Username of the user who made the change")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "batch",
                "entity_id": "batch_12345",
                "field_changed": "status",
                "old_value": "produced",
                "new_value": "in_storage",
                "timestamp": "2025-06-01T10:30:00",
                "changed_by": "enterprise_user"
            }
        }
