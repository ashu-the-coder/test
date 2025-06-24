from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import pymongo
import os
from models.inventory import InventoryUpdate, InventoryItem, InventoryAuditLog
from routes.auth import get_current_active_user

# Get MongoDB connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xintete_storage")

# Setup MongoDB client
from pymongo import MongoClient
client = MongoClient(MONGODB_URL)
db = client.xinete_storage

# Create collections if not exist
if "inventory" not in db.list_collection_names():
    db.create_collection("inventory")
    # Create a compound index on product_id and location for faster lookups
    db.inventory.create_index([("product_id", pymongo.ASCENDING), ("location", pymongo.ASCENDING)], unique=True)

if "inventory_audit_logs" not in db.list_collection_names():
    db.create_collection("inventory_audit_logs")
    # Create an index for faster audit log queries
    db.inventory_audit_logs.create_index([("product_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])

# Setup router
router = APIRouter()

@router.patch("/update", response_model=Dict[str, Any])
async def update_inventory(
    update_data: InventoryUpdate = Body(...),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Update inventory levels for a product at a specific location.
    
    This endpoint updates the quantity of a product at a specified location
    and logs the change in the audit trail. The operation can be either 'add'
    to increase inventory or 'remove' to decrease inventory.
    
    Returns:
        A dictionary containing the updated inventory data and confirmation message.
    
    Raises:
        HTTPException 400: If trying to remove more inventory than available
        HTTPException 404: If the product is not found
    """
    # Verify product exists
    product = db.products.find_one({"id": update_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get enterprise ID from the user
    enterprise_id = current_user.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(status_code=400, detail="User not associated with an enterprise")
    
    # Check if inventory record exists for this product and location
    inventory = db.inventory.find_one({
        "product_id": update_data.product_id,
        "location": update_data.location,
        "enterprise_id": enterprise_id
    })
    
    # Current timestamp
    now = datetime.now()
    
    # Generate a unique ID for new inventory records
    inventory_id = None
    
    if inventory:
        # Record exists, update it
        previous_quantity = inventory["quantity"]
        
        # Calculate new quantity based on operation
        if update_data.operation == "add":
            new_quantity = previous_quantity + update_data.change_in_quantity
        else:  # remove
            if previous_quantity < update_data.change_in_quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough inventory. Current: {previous_quantity}, Attempting to remove: {update_data.change_in_quantity}"
                )
            new_quantity = previous_quantity - update_data.change_in_quantity
        
        # Update the inventory record
        db.inventory.update_one(
            {"id": inventory["id"]},
            {"$set": {
                "quantity": new_quantity,
                "last_updated": now
            }}
        )
        
        inventory_id = inventory["id"]
    else:
        # Record doesn't exist, create a new one
        if update_data.operation == "remove":
            raise HTTPException(
                status_code=400,
                detail="Cannot remove from non-existent inventory. Please add inventory first."
            )
        
        # For new records, the new quantity is simply the change amount (since we're adding)
        previous_quantity = 0
        new_quantity = update_data.change_in_quantity
        
        # Generate a unique ID
        inventory_id = f"inv_{uuid.uuid4().hex[:8]}"
        
        # Create new inventory record
        new_inventory = InventoryItem(
            id=inventory_id,
            product_id=update_data.product_id,
            enterprise_id=enterprise_id,
            location=update_data.location,
            quantity=new_quantity,
            last_updated=now
        )
        
        # Insert into database
        db.inventory.insert_one(new_inventory.dict())
    
    # Create audit log entry
    audit_log = InventoryAuditLog(
        id=f"log_{uuid.uuid4().hex[:8]}",
        inventory_id=inventory_id,
        product_id=update_data.product_id,
        enterprise_id=enterprise_id,
        location=update_data.location,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        change_amount=update_data.change_in_quantity,
        operation=update_data.operation,
        timestamp=now,
        user_id=current_user.get("id", "unknown"),
        notes=update_data.notes
    )
    
    # Insert audit log
    db.inventory_audit_logs.insert_one(audit_log.dict())
    
    # Get updated inventory
    updated_inventory = db.inventory.find_one({"id": inventory_id})
    
    return {
        "inventory": InventoryItem(**updated_inventory).dict(),
        "message": f"Inventory {update_data.operation}ed successfully",
        "product_name": product.get("product_name", "Unknown product"),
        "audit_log_id": audit_log.id
    }

@router.get("/{product_id}", response_model=List[InventoryItem])
async def get_live_inventory(
    product_id: str = Path(..., description="ID of the product to get inventory for"),
    location: Optional[str] = Query(None, description="Optional location filter"),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Get current inventory levels for a product.
    
    Returns the current inventory levels for a specific product, optionally filtered by location.
    If location is not provided, inventory across all locations will be returned.
    
    Returns:
        A list of inventory items for the specified product.
    
    Raises:
        HTTPException 404: If the product is not found
    """
    # Verify product exists
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get enterprise ID from the user
    enterprise_id = current_user.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(status_code=400, detail="User not associated with an enterprise")
    
    # Build query
    query = {
        "product_id": product_id,
        "enterprise_id": enterprise_id
    }
    
    # Add location filter if provided
    if location:
        query["location"] = location
    
    # Get inventory
    inventory_items = list(db.inventory.find(query))
    
    if not inventory_items and not location:
        # Return empty list but not an error - it's valid to have no inventory
        return []
    elif not inventory_items and location:
        # If a specific location was requested but not found
        return []
    
    # Convert to Pydantic models
    return [InventoryItem(**item) for item in inventory_items]

@router.get("/audit/{product_id}", response_model=List[InventoryAuditLog])
async def get_inventory_audit(
    product_id: str = Path(..., description="ID of the product to get audit logs for"),
    location: Optional[str] = Query(None, description="Optional location filter"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of audit logs to return"),
    offset: int = Query(0, ge=0, description="Number of audit logs to skip"),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Get inventory audit logs for a product.
    
    Returns a history of inventory changes for the specified product,
    optionally filtered by location.
    
    Returns:
        A list of audit log entries for the specified product.
    """
    # Get enterprise ID from the user
    enterprise_id = current_user.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(status_code=400, detail="User not associated with an enterprise")
    
    # Build query
    query = {
        "product_id": product_id,
        "enterprise_id": enterprise_id
    }
    
    # Add location filter if provided
    if location:
        query["location"] = location
    
    # Get audit logs
    audit_logs = list(
        db.inventory_audit_logs.find(query)
        .sort("timestamp", pymongo.DESCENDING)
        .skip(offset)
        .limit(limit)
    )
    
    # Convert to Pydantic models
    return [InventoryAuditLog(**log) for log in audit_logs]
