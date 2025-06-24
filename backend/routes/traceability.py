from fastapi import APIRouter, HTTPException, Depends, Body, Query, File, UploadFile
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import pymongo
import os
from models.traceability import TraceEvent, TraceEventCreate
from routes.auth import get_current_active_user

# Get MongoDB connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xintete_storage")

# Setup MongoDB client
from pymongo import MongoClient
client = MongoClient(MONGODB_URL)
db = client.xinete_storage

# Create collections if not exist
if "trace_events" not in db.list_collection_names():
    db.create_collection("trace_events")

# Setup router
router = APIRouter()

@router.post("/add", response_model=Dict[str, str])
async def add_trace_event(
    event_data: TraceEventCreate = Body(...),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Add a new traceability event for a batch with mandatory IPFS and blockchain registration.
    
    This endpoint requires a valid IPFS CID to be provided in the request body.
    The event will be registered on the blockchain automatically, which is also mandatory.
    If either the IPFS CID is invalid or the blockchain registration fails, the entire
    event creation will fail.
    
    Users can either:
    1. Upload a document via the /trace/upload endpoint first and use the returned IPFS CID
    2. Provide a pre-existing valid IPFS CID directly
    
    Returns:
        A dictionary containing the event_id and a success message.
    
    Raises:
        HTTPException 400: If IPFS CID is missing or invalid format
        HTTPException 500: If blockchain registration fails
    """
    # Verify batch exists
    batch = db.batches.find_one({"id": event_data.batch_id})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    # Validate IPFS CID - ensure it's properly formatted (starts with Qm for CIDv0 or bafy for CIDv1)
    if not event_data.ipfs_cid:
        raise HTTPException(status_code=400, detail="IPFS CID is required for traceability events")
        
    if not (event_data.ipfs_cid.startswith("Qm") or event_data.ipfs_cid.startswith("bafy")):
        raise HTTPException(status_code=400, detail="Invalid IPFS CID format. Must start with 'Qm' or 'bafy'")
    
    # Get enterprise and product IDs from the batch
    enterprise_id = batch.get("enterprise_id")
    product_id = batch.get("product_id")
    batch_number = batch.get("batch_number")
    
    # Generate event ID
    event_id = f"trace_{uuid.uuid4().hex[:8]}"
    
    # Current timestamp
    creation_date = datetime.now()
    
    # Set timestamp to now if not provided
    timestamp = event_data.timestamp or creation_date
    
    # Prepare event document
    event = TraceEvent(
        id=event_id,
        batch_id=event_data.batch_id,
        batch_number=batch_number,
        product_id=product_id,
        enterprise_id=enterprise_id,
        event_type=event_data.event_type,
        timestamp=timestamp,
        location=event_data.location,
        operator=event_data.operator,
        temperature=event_data.temperature,
        humidity=event_data.humidity,
        notes=event_data.notes,
        ipfs_cid=event_data.ipfs_cid,
        creation_date=creation_date
    )
    
    # Process blockchain transaction for the traceability event - this is now mandatory
    try:
        # Import here to avoid circular imports
        from services.blockchain import BlockchainService
        blockchain_service = BlockchainService()
        
        # Record trace event in blockchain
        tx_hash = await blockchain_service.record_trace_event(
            event_id=event_id,
            batch_id=event_data.batch_id,
            event_type=event_data.event_type,
            ipfs_cid=event_data.ipfs_cid
        )
        
        if not tx_hash:
            raise HTTPException(status_code=500, detail="Failed to get blockchain transaction hash")
        
        # Update event with blockchain tx hash
        event.blockchain_tx_hash = tx_hash
    except Exception as e:
        # Since blockchain integration is mandatory, fail the request if blockchain registration fails
        raise HTTPException(
            status_code=500, 
            detail=f"Blockchain registration is required but failed: {str(e)}"
        )
    
    # Insert event into database
    db.trace_events.insert_one(event.dict())
    
    # Update batch status based on event type
    if event_data.event_type == "shipping":
        db.batches.update_one(
            {"id": event_data.batch_id},
            {"$set": {"status": "shipped"}}
        )
    elif event_data.event_type == "receiving":
        db.batches.update_one(
            {"id": event_data.batch_id},
            {"$set": {"status": "received"}}
        )
    elif event_data.event_type == "storage":
        db.batches.update_one(
            {"id": event_data.batch_id},
            {"$set": {"status": "in_storage"}}
        )
    elif event_data.event_type == "sold":
        db.batches.update_one(
            {"id": event_data.batch_id},
            {"$set": {"status": "sold"}}
        )
    
    return {
        "event_id": event_id,
        "message": "Traceability event added successfully"
    }

@router.get("/list/{batch_id}", response_model=List[TraceEvent])
async def list_trace_events(
    batch_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    List all traceability events for a batch, with optional filters.
    """
    # Build query
    query = {"batch_id": batch_id}
    if start_date and end_date:
        query["timestamp"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        query["timestamp"] = {"$gte": start_date}
    elif end_date:
        query["timestamp"] = {"$lte": end_date}
    
    if event_type:
        query["event_type"] = event_type
    
    # Get events
    events = list(db.trace_events.find(query).sort("timestamp", 1).skip(offset).limit(limit))
    
    return [TraceEvent(**event) for event in events]

@router.get("/{event_id}", response_model=TraceEvent)
async def get_trace_event(
    event_id: str,
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Get traceability event details by ID.
    """
    event = db.trace_events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Traceability event not found")
    
    return TraceEvent(**event)

@router.post("/upload", response_model=Dict[str, str])
async def upload_trace_document(
    batch_id: str,
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Upload a document for a traceability event and store it on IPFS.
    Returns the IPFS CID that can be used when creating a trace event.
    """
    # Verify batch exists
    batch = db.batches.find_one({"id": batch_id})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # TODO: Upload to IPFS and get CID
        # This would typically use an IPFS client
        # For now, we'll mock the CID
        import hashlib
        mock_ipfs_cid = "Qm" + hashlib.sha256(file_content).hexdigest()[:44]
        
        return {
            "ipfs_cid": mock_ipfs_cid,
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.get("/history/{enterprise_id}", response_model=List[TraceEvent])
async def get_trace_history(
    enterprise_id: str,
    product_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_active_user)
):
    """
    Get traceability history for an enterprise, with optional filters.
    """
    # Build query
    query = {"enterprise_id": enterprise_id}
    if product_id:
        query["product_id"] = product_id
    
    if start_date and end_date:
        query["timestamp"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        query["timestamp"] = {"$gte": start_date}
    elif end_date:
        query["timestamp"] = {"$lte": end_date}
    
    # Get events
    events = list(db.trace_events.find(query).sort("timestamp", -1).skip(offset).limit(limit))
    
    return [TraceEvent(**event) for event in events]
