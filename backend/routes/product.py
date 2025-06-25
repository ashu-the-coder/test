from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List
import uuid
from datetime import datetime
import pymongo
import os
from models.product import Product, ProductCreate
from routes.auth import get_current_active_user
from utils.mongodb import get_mongo_connection

# Setup MongoDB client
try:
    client, db = get_mongo_connection()
    
    # Create products collection if not exists
    if "products" not in db.list_collection_names():
        db.create_collection("products")
except Exception as e:
    print(f"Error in product route connecting to MongoDB: {str(e)}")
    # Let FastAPI handle the exception

# Setup router
router = APIRouter()

@router.post("/add", response_model=Dict[str, str])
async def add_product(product_data: ProductCreate = Body(...), current_user=Depends(get_current_active_user)):
    """
    Add a new product for an enterprise.
    """
    # Verify enterprise exists
    enterprise = db.enterprises.find_one({"id": product_data.enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    
    # Check if product with same name already exists for this enterprise
    existing = db.products.find_one({
        "enterprise_id": product_data.enterprise_id,
        "product_name": product_data.product_name
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Product with this name already exists for this enterprise")
    
    # Create new product document
    product_id = f"prod_{uuid.uuid4().hex[:8]}"
    creation_date = datetime.now()
    
    product = Product(
        id=product_id,
        creation_date=creation_date,
        **product_data.dict()
    )
    
    # Insert product into database
    db.products.insert_one(product.dict())
    
    # Optional: Update IPFS and blockchain records
    # This would be implemented in a background task
    # For now, we'll just return the product ID
    
    return {"product_id": product_id, "message": "Product added successfully"}


@router.get("/list/{enterprise_id}", response_model=List[Product])
async def list_products(enterprise_id: str, current_user=Depends(get_current_active_user)):
    """
    List all products for an enterprise.
    """
    # Verify enterprise exists
    enterprise = db.enterprises.find_one({"id": enterprise_id})
    if not enterprise:
        raise HTTPException(status_code=404, detail="Enterprise not found")
    
    # Get all products for this enterprise
    products = list(db.products.find({"enterprise_id": enterprise_id}))
    
    return [Product(**product) for product in products]


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str, current_user=Depends(get_current_active_user)):
    """
    Get product details by ID.
    """
    # Find product by ID
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Return product data
    return Product(**product)


@router.put("/{product_id}", response_model=Dict[str, str])
async def update_product(
    product_id: str, 
    update_data: Dict[str, Any] = Body(...),
    current_user=Depends(get_current_active_user)
):
    """
    Update product details.
    """
    # Find product by ID
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Protected fields that cannot be updated
    protected_fields = ["id", "enterprise_id", "creation_date"]
    
    # Remove protected fields from update data
    for field in protected_fields:
        if field in update_data:
            del update_data[field]
    
    # Update product in database
    result = db.products.update_one(
        {"id": product_id},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return {"message": "Product updated successfully"}
    else:
        return {"message": "No changes applied"}


@router.delete("/{product_id}", response_model=Dict[str, str])
async def delete_product(product_id: str, current_user=Depends(get_current_active_user)):
    """
    Delete a product.
    """
    # Find product by ID
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete product from database
    db.products.delete_one({"id": product_id})
    
    return {"message": "Product deleted successfully"}
