from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List
import uuid
from datetime import datetime
import pymongo
import os
from models.enterprise import Enterprise, EnterpriseCreate
from routes.auth import get_current_active_user
from urllib.parse import urlparse

# Function to extract database name from MongoDB URI
def extract_db_name_from_uri(uri):
    """
    Parse MongoDB URI to extract database name, handling cases with
    authentication credentials and query parameters properly.
    
    Returns the database name or a default value if not found
    """
    default_db = "xinete_storage"
    
    if not uri:
        return default_db
        
    try:
        # Parse the URI
        parsed = urlparse(uri)
        
        # Extract path and remove leading slash
        path = parsed.path
        if path.startswith('/'):
            path = path[1:]
            
        # If path has query parameters, extract just the DB name
        if '?' in path:
            path = path.split('?')[0]
            
        # Return the extracted database name or default
        return path if path else default_db
    except Exception as e:
        print(f"Error parsing MongoDB URI: {e}")
        return default_db

# Get MongoDB connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL", os.getenv("MONGO_URI", "mongodb://localhost:27017/xinete_storage"))
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_DB = os.getenv("MONGODB_DB", os.getenv("MONGO_DB", ""))

# Setup MongoDB client
from pymongo import MongoClient

# Connect to MongoDB with authentication
try:
    # If the connection string already includes auth, use it directly
    if "@" in MONGODB_URL:
        print(f"Using MongoDB connection string with embedded authentication")
        client = MongoClient(MONGODB_URL)
    # If separate username and password provided, use them
    elif MONGODB_USERNAME and MONGODB_PASSWORD:
        # Parse the connection string to add auth credentials
        if "://" in MONGODB_URL:
            protocol, rest = MONGODB_URL.split("://", 1)
            auth_url = f"{protocol}://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{rest}"
            print(f"Connecting to MongoDB with authentication")
            client = MongoClient(auth_url)
        else:
            client = MongoClient(MONGODB_URL)
            db_name = extract_db_name_from_uri(MONGODB_URL)
            client[db_name].authenticate(MONGODB_USERNAME, MONGODB_PASSWORD)
    else:
        print(f"Connecting to MongoDB without authentication")
        client = MongoClient(MONGODB_URL)

    # Get database reference - prioritize explicit DB name if provided
    db_name = MONGODB_DB if MONGODB_DB else extract_db_name_from_uri(MONGODB_URL)
    print(f"Enterprise route using database: {db_name}")
    db = client[db_name]
    
    # Test connection
    client.admin.command('ping')
    print("Enterprise route successfully connected to MongoDB")
except Exception as e:
    print(f"Enterprise route failed to connect to MongoDB: {str(e)}")
    raise

# Create enterprise collection if not exists
try:
    if "enterprises" not in db.list_collection_names():
        db.create_collection("enterprises")
except Exception as e:
    print(f"Error checking/creating collections: {str(e)}")
    # Continue even if this fails, as the collection might be created elsewhere
    
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

@router.get("/profile", response_model=Dict[str, Any])
async def get_current_enterprise_profile(current_user=Depends(get_current_active_user)):
    """
    Get current enterprise profile based on JWT token. Requires authentication.
    This endpoint is used by the enterprise dashboard.
    """
    # Extract enterprise ID from JWT token
    try:
        from routes.auth import get_token_data
        token_data = get_token_data(current_user)
        enterprise_id = token_data.get("enterprise_id")
        
        if not enterprise_id:
            raise HTTPException(status_code=400, detail="No enterprise ID found in token")
            
        # Find enterprise by ID
        enterprise = db.enterprises.find_one({"enterprise_id": enterprise_id})
        if not enterprise:
            # Try with _id if not found with enterprise_id
            enterprise = db.enterprises.find_one({"_id": enterprise_id})
            
        if not enterprise:
            raise HTTPException(status_code=404, detail="Enterprise not found")
        
        # Count products and batches
        product_count = db.products.count_documents({"enterprise_id": enterprise_id})
        batch_count = db.batches.count_documents({"enterprise_id": enterprise_id})
        
        # Convert MongoDB _id to string if needed
        if enterprise.get("_id"):
            enterprise["id"] = str(enterprise["_id"])
            del enterprise["_id"]
            
        # Add counts to response
        enterprise["productCount"] = product_count
        enterprise["batchCount"] = batch_count
        
        return enterprise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enterprise profile: {str(e)}")
