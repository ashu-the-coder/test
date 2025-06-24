from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List
import uuid
from datetime import datetime
import pymongo
import os
from models.enterprise import Enterprise, EnterpriseCreate
from routes.auth import get_current_active_user

# Get MongoDB connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xintete_storage")

# Setup MongoDB client
from pymongo import MongoClient
client = MongoClient(MONGODB_URL)
db = client.xinete_storage

# Create enterprise collection if not exists
if "enterprises" not in db.list_collection_names():
    db.create_collection("enterprises")
    
# Setup router
router = APIRouter()

@router.post("/register", response_model=Dict[str, str])
async def register_enterprise(
    enterprise_data: EnterpriseCreate = Body(...),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Register a new enterprise in the platform.
    This is typically called after a user has registered through /auth/enterprise/register
    to create an additional enterprise record with more details.
    """
    # Check if enterprise with same name already exists
    existing = db.enterprises.find_one({"enterprise_name": enterprise_data.enterprise_name})
    if existing:
        raise HTTPException(status_code=400, detail="Enterprise with this name already exists")
    
    # Check if user already has an enterprise
    existing = db.enterprises.find_one({"admin_details.email": enterprise_data.admin_details.email})
    if existing:
        # If the enterprise record already exists, return it instead of creating a new one
        return {"enterprise_id": existing["id"], "message": "Enterprise record already exists"}
    
    # Create new enterprise document
    enterprise_id = f"ent_{uuid.uuid4().hex[:8]}"
    creation_date = datetime.now()
    
    enterprise = Enterprise(
        id=enterprise_id,
        creation_date=creation_date,
        **enterprise_data.dict()
    )
    
    # Insert enterprise into database
    db.enterprises.insert_one(enterprise.dict())
    
    return {"enterprise_id": enterprise_id, "message": "Enterprise registered successfully"}


@router.get("/profile/{enterprise_id}", response_model=Enterprise)
async def get_enterprise_profile(enterprise_id: str, current_user=Depends(get_current_active_user)):
    """
    Get enterprise profile by ID. Requires authentication.
    """
    # Find enterprise by ID
    enterprise = db.enterprises.find_one({"id": enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    
    # Return enterprise data
    return Enterprise(**enterprise)


@router.put("/profile/{enterprise_id}", response_model=Dict[str, str])
async def update_enterprise_profile(
    enterprise_id: str, 
    update_data: Dict[str, Any] = Body(...),
    current_user=Depends(get_current_active_user)
):
    """
    Update enterprise profile details. Requires authentication.
    """
    # Find enterprise by ID
    enterprise = db.enterprises.find_one({"id": enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    
    # Protected fields that cannot be updated
    protected_fields = ["id", "creation_date", "admin_details.email"]
    
    # Remove protected fields from update data
    for field in protected_fields:
        if field in update_data:
            del update_data[field]
    
    # Update enterprise in database
    result = db.enterprises.update_one(
        {"id": enterprise_id},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return {"message": "Enterprise profile updated successfully"}
    else:
        return {"message": "No changes applied"}

@router.get("/list", response_model=List[Enterprise])
async def list_enterprises(current_user=Depends(get_current_active_user)):
    """
    List all enterprises. Requires authentication.
    Admin only endpoint.
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can access this endpoint")
    
    # Get all enterprises
    enterprises = list(db.enterprises.find())
    
    return [Enterprise(**enterprise) for enterprise in enterprises]
