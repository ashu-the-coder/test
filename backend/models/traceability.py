from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TraceEventCreate(BaseModel):
    """
    Model for creating a new traceability event.
    
    IMPORTANT: All traceability events must have IPFS documentation to ensure 
    enterprise traceability compliance. The IPFS CID is mandatory and must be 
    provided during event creation. Blockchain registration will be handled 
    automatically.
    """
    batch_id: str = Field(..., description="ID of the batch this event relates to")
    event_type: str = Field(..., description="Type of the event (production, quality_check, packaging, shipping, etc.)")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the event (defaults to current time)")
    location: str = Field(..., description="Location where the event occurred")
    operator: Optional[str] = Field(None, description="Person who performed or recorded the event")
    temperature: Optional[float] = Field(None, description="Temperature during the event (if applicable)")
    humidity: Optional[float] = Field(None, description="Humidity during the event (if applicable)")
    notes: Optional[str] = Field(None, description="Additional notes about the event")
    ipfs_cid: str = Field(..., description="IPFS CID for event documentation (MANDATORY, must start with Qm or bafy)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "batch_12345",
                "event_type": "quality_check",
                "timestamp": "2025-06-25T14:30:00",
                "location": "Quality Control Lab 3",
                "operator": "Jane Doe",
                "temperature": 22.5,
                "humidity": 45.0,
                "notes": "All tests passed successfully",
                "ipfs_cid": "QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx"
            }
        }

class TraceEvent(BaseModel):
    """
    Model for traceability event data.
    
    Every traceability event must have both IPFS documentation and blockchain registration
    for enterprise compliance. Both ipfs_cid and blockchain_tx_hash are mandatory fields
    and will be verified during event creation.
    """
    id: str = Field(..., description="Unique identifier for the event")
    batch_id: str = Field(..., description="ID of the batch this event relates to")
    batch_number: str = Field(..., description="Human-readable batch number")
    product_id: str = Field(..., description="ID of the product")
    enterprise_id: str = Field(..., description="ID of the enterprise that owns this batch")
    event_type: str = Field(..., description="Type of the event")
    timestamp: datetime = Field(..., description="Timestamp of the event")
    location: str = Field(..., description="Location where the event occurred")
    operator: Optional[str] = Field(None, description="Person who performed or recorded the event")
    temperature: Optional[float] = Field(None, description="Temperature during the event (if applicable)")
    humidity: Optional[float] = Field(None, description="Humidity during the event (if applicable)")
    notes: Optional[str] = Field(None, description="Additional notes about the event")
    ipfs_cid: str = Field(..., description="IPFS CID for event documentation (MANDATORY)")
    blockchain_tx_hash: str = Field(..., description="Blockchain transaction hash for event verification (MANDATORY)")
    creation_date: datetime = Field(..., description="Date when the event record was created")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "trace_12345",
                "batch_id": "batch_12345",
                "batch_number": "PROD001-B001",
                "product_id": "prod_12345",
                "enterprise_id": "ent_12345",
                "event_type": "quality_check",
                "timestamp": "2025-06-25T14:30:00",
                "location": "Quality Control Lab 3",
                "operator": "Jane Doe",
                "temperature": 22.5,
                "humidity": 45.0,
                "notes": "All tests passed successfully",
                "ipfs_cid": "QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx",
                "blockchain_tx_hash": "0x1234567890abcdef1234567890abcdef12345678",
                "creation_date": "2025-06-25T14:35:00"
            }
        }
