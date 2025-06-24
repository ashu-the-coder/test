from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import pymongo
import os
import io
import qrcode
import base64
from models.batch import Batch, BatchCreate
from models.product import Product
from routes.auth import get_current_active_user
import ipfs_utils

# Get MongoDB connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xintete_storage")

# Setup MongoDB client
from pymongo import MongoClient
client = MongoClient(MONGODB_URL)
db = client.xinete_storage

# Create collections if not exist
if "batches" not in db.list_collection_names():
    db.create_collection("batches")

# Setup router
router = APIRouter()

# Helper functions
def generate_batch_number(product_code, sequence):
    """Generate a human-readable batch number."""
    current_date = datetime.now().strftime("%y%m%d")
    return f"{product_code}-{current_date}-{sequence:03d}"

def generate_qr_code(batch_id, verification_url=None, ipfs_cid=None):
    """Generate a QR code for a batch.
    
    If ipfs_cid is provided, the QR code will point to the IPFS view link.
    Otherwise, it will generate a data URL.
    """
    if not verification_url:
        # Default verification URL
        verification_url = f"https://xinete.io/verify/{batch_id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    # Create an in-memory bytes buffer
    buffer = io.BytesIO()
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(buffer, format="PNG")
    
    # Get the bytes value from the buffer
    qr_bytes = buffer.getvalue()
    
    # If IPFS CID is provided, upload the QR image to IPFS and return the IPFS view link
    if ipfs_cid:
        # Use the existing IPFS CID associated with this batch
        return ipfs_utils.get_ipfs_view_link(ipfs_cid)
    
    # Otherwise, encode to base64 for the URL (fallback method)
    qr_base64 = base64.b64encode(qr_bytes).decode('ascii')
    
    # Return a data URL
    return f"data:image/png;base64,{qr_base64}"

@router.post("/create", response_model=Dict[str, str])
async def create_batch(
    batch_data: BatchCreate = Body(...),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Create a new batch for a product with mandatory IPFS and blockchain registration.
    
    This endpoint requires a valid IPFS CID to be provided in the request body.
    The batch will be registered on the blockchain automatically, which is also mandatory.
    If either the IPFS CID is invalid or the blockchain registration fails, the entire
    batch creation will fail.
    
    Returns:
        A dictionary containing the batch_id, batch_number, QR code URL, and verification URL.
    
    Raises:
        HTTPException 400: If IPFS CID is missing or invalid format
        HTTPException 500: If blockchain registration fails
    """
    # Verify product exists
    product = db.products.find_one({"id": batch_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Validate IPFS CID - ensure it's properly formatted (starts with Qm for CIDv0 or bafy for CIDv1)
    if not batch_data.ipfs_cid:
        raise HTTPException(status_code=400, detail="IPFS CID is required for batch creation")
        
    if not (batch_data.ipfs_cid.startswith("Qm") or batch_data.ipfs_cid.startswith("bafy")):
        raise HTTPException(status_code=400, detail="Invalid IPFS CID format. Must start with 'Qm' or 'bafy'")
    
    # Get enterprise ID from the product
    enterprise_id = product.get("enterprise_id")
    
    # Generate batch ID
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    
    # Generate batch number if not provided
    batch_number = batch_data.batch_number
    if not batch_number:
        # Find the latest batch number for this product
        latest_batch = db.batches.find_one(
            {"product_id": batch_data.product_id},
            sort=[("creation_date", pymongo.DESCENDING)]
        )
        sequence = 1
        if latest_batch:
            try:
                # Try to extract the sequence from the latest batch number
                last_sequence = int(latest_batch.get("batch_number", "").split("-")[-1])
                sequence = last_sequence + 1
            except (ValueError, IndexError):
                sequence = 1
        
        # Get product code for batch number
        product_code = product.get("sku") or "PROD"
        batch_number = generate_batch_number(product_code, sequence)
    
    # Current timestamp
    creation_date = datetime.now()
    
    # Set timestamp to now if not provided
    production_date = batch_data.production_date or creation_date
    
    # Prepare batch document
    batch = Batch(
        id=batch_id,
        batch_number=batch_number,
        product_id=batch_data.product_id,
        enterprise_id=enterprise_id,
        production_date=production_date,
        expiry_date=batch_data.expiry_date,
        initial_quantity=batch_data.initial_quantity,
        current_quantity=batch_data.initial_quantity,
        creation_date=creation_date,
        status="produced",
        batch_notes=batch_data.batch_notes,
        ipfs_cid=batch_data.ipfs_cid
    )
    
    # Generate QR code with IPFS view link
    verification_url = f"https://xinete.io/verify/{batch_id}"
    # Use the provided IPFS CID to generate an IPFS view link for the QR code
    qr_code_url = generate_qr_code(batch_id, verification_url, batch_data.ipfs_cid)
    batch.qr_code_url = qr_code_url
    batch.verification_url = verification_url
    
    # Process blockchain transaction - this is now mandatory
    try:
        # Import here to avoid circular imports
        from services.blockchain import BlockchainService
        blockchain_service = BlockchainService()
        
        # Register batch in blockchain
        tx_hash = await blockchain_service.register_batch(
            batch_id=batch_id,
            product_id=batch_data.product_id,
            ipfs_cid=batch_data.ipfs_cid
        )
        
        if not tx_hash:
            raise HTTPException(status_code=500, detail="Failed to get blockchain transaction hash")
            
        # Update batch with blockchain tx hash
        batch.blockchain_tx_hash = tx_hash
    except Exception as e:
        # Since blockchain integration is mandatory, fail the request if blockchain registration fails
        raise HTTPException(
            status_code=500, 
            detail=f"Blockchain registration is required but failed: {str(e)}"
        )
    
    # Insert batch into database
    db.batches.insert_one(batch.dict())
    
    # Generate IPFS view link
    ipfs_view_link = ipfs_utils.get_ipfs_view_link(batch.ipfs_cid)
    
    return {
        "batch_id": batch_id,
        "batch_number": batch_number,
        "qr_code_url": qr_code_url,
        "verification_url": verification_url,
        "ipfs_view_link": ipfs_view_link,
        "ipfs_cid": batch.ipfs_cid,
        "blockchain_tx_hash": batch.blockchain_tx_hash,
        "message": "Batch created successfully"
    }

@router.get("/list/{enterprise_id}", response_model=List[Batch])
async def list_batches(
    enterprise_id: str,
    product_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    List all batches for an enterprise, with optional filters.
    """
    # Build query
    query = {"enterprise_id": enterprise_id}
    if product_id:
        query["product_id"] = product_id
    if status:
        query["status"] = status
    
    # Get batches
    batches = list(db.batches.find(query).sort("creation_date", -1).skip(offset).limit(limit))
    
    return [Batch(**batch) for batch in batches]

@router.get("/{batch_id}", response_model=Batch)
async def get_batch(
    batch_id: str,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Get batch details by ID.
    """
    batch = db.batches.find_one({"id": batch_id})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return Batch(**batch)

@router.put("/{batch_id}/status", response_model=Dict[str, str])
async def update_batch_status(
    batch_id: str,
    status: str = Body(..., embed=True),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Update batch status.
    """
    # Verify batch exists
    batch = db.batches.find_one({"id": batch_id})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Update batch status
    db.batches.update_one(
        {"id": batch_id},
        {"$set": {"status": status}}
    )
    
    return {"message": f"Batch status updated to {status}"}

@router.put("/{batch_id}/quantity", response_model=Dict[str, str])
async def update_batch_quantity(
    batch_id: str,
    quantity: float = Body(..., embed=True),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Update batch current quantity.
    """
    # Verify batch exists
    batch = db.batches.find_one({"id": batch_id})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    
    # Update batch quantity
    db.batches.update_one(
        {"id": batch_id},
        {"$set": {"current_quantity": quantity}}
    )
    
    return {"message": f"Batch quantity updated to {quantity}"}
