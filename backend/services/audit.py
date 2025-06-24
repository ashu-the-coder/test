import os
from pymongo import MongoClient
from fastapi import HTTPException
from datetime import datetime
from models.audit import AuditLog

class AuditService:
    """Service for managing audit logs"""
    
    def __init__(self):
        # Connect to MongoDB
        self.mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://admin:%40dminXinetee%40123@100.123.165.22:27017"))
        self.db = self.mongo_client[os.getenv("MONGO_DB", "xinetee")]
        self.audit_collection = self.db[os.getenv("MONGO_AUDIT_COLLECTION", "audit_logs")]
    
    def log_change(self, 
                   entity_type: str, 
                   entity_id: str, 
                   field_changed: str, 
                   old_value, 
                   new_value, 
                   changed_by: str) -> str:
        """
        Log a change to the audit trail
        Returns the inserted ID
        """
        try:
            audit_entry = {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "field_changed": field_changed,
                "old_value": old_value,
                "new_value": new_value,
                "timestamp": datetime.utcnow(),
                "changed_by": changed_by
            }
            
            result = self.audit_collection.insert_one(audit_entry)
            return str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to log audit: {str(e)}")
    
    def get_entity_audit_trail(self, entity_type: str, entity_id: str):
        """
        Get audit trail for a specific entity
        """
        try:
            audit_logs = list(self.audit_collection.find(
                {"entity_type": entity_type, "entity_id": entity_id},
                {"_id": 0}  # Exclude MongoDB _id
            ).sort("timestamp", -1))  # Sort by timestamp, newest first
            
            return audit_logs
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")
            
    def get_audit_trail(self, 
                        entity_type: str = None, 
                        entity_id: str = None, 
                        changed_by: str = None, 
                        from_date: datetime = None, 
                        to_date: datetime = None,
                        limit: int = 100,
                        skip: int = 0):
        """
        Get audit trail with optional filters
        """
        try:
            # Build query based on provided filters
            query = {}
            if entity_type:
                query["entity_type"] = entity_type
            if entity_id:
                query["entity_id"] = entity_id
            if changed_by:
                query["changed_by"] = changed_by
                
            # Handle date range filtering
            if from_date or to_date:
                query["timestamp"] = {}
                if from_date:
                    query["timestamp"]["$gte"] = from_date
                if to_date:
                    query["timestamp"]["$lte"] = to_date
            
            # Execute query with pagination
            audit_logs = list(self.audit_collection.find(
                query,
                {"_id": 0}  # Exclude MongoDB _id
            ).sort("timestamp", -1).skip(skip).limit(limit))
            
            return audit_logs
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")
