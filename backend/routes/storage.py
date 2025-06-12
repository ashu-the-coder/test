from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Header
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import hashlib
import json
from datetime import datetime
from pymongo import MongoClient

from services.ipfs import IPFSService
from services.blockchain import BlockchainService
from models.user import User
from .auth import get_current_user
from models.user import FileMetadata

router = APIRouter()

# Initialize services
ipfs_service = IPFSService()
blockchain_service = BlockchainService()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://100.123.165.22:27017")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[os.getenv("MONGO_DB", "xinetee")]
users_collection = db[os.getenv("MONGO_USERS_COLLECTION", "users")]

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Upload file to IPFS
        cid = await ipfs_service.upload_file(file)
        file_hash = hashlib.sha256(cid.encode()).hexdigest()
        tx_hash = await blockchain_service.store_cid(current_user, cid, file_hash)
        await file.seek(0)
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)
        metadata = FileMetadata(
            filename=file.filename,
            size=file_size,
            upload_date=datetime.now(),
            content_type=file.content_type,
            file_hash=file_hash,
            transaction_hash=tx_hash
        )
        normalized_username = current_user["username"].lower()
        users_collection.update_one(
            {"username": normalized_username},
            {"$push": {"files": metadata.dict()}},
            upsert=True
        )
        return {
            "status": "success",
            "filename": file.filename,
            "upload_date": metadata.upload_date,
            "size": metadata.size,
            "file_hash": file_hash,
            "transaction_hash": tx_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def get_user_files(current_user: dict = Depends(get_current_user)):
    normalized_username = current_user["username"].lower()
    db_user = users_collection.find_one({"username": normalized_username})
    files = db_user.get("files", []) if db_user else []
    # Always return as { files: [...] } for frontend compatibility
    return {"files": [FileMetadata(**f).dict() if not isinstance(f, FileMetadata) else f.dict() for f in files]}

@router.get("/user", response_model=User)
async def get_user(current_user: dict = Depends(get_current_user)):
    normalized_username = current_user["username"].lower()
    db_user = users_collection.find_one({"username": normalized_username})
    wallet_address = db_user.get("wallet_address", None) if db_user else None
    files = db_user.get("files", []) if db_user else []
    file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
    return User(username=current_user["username"], wallet_address=wallet_address, files=file_objs)

@router.get("/download/{file_hash}")
async def download_file(
    file_hash: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get CID from blockchain using file hash
        cid = await blockchain_service.get_cid_by_hash(file_hash)
        if not cid:
            raise HTTPException(status_code=404, detail="File not found in blockchain")
            
        # Temporarily removed ownership verification
        # TODO: Re-implement ownership verification after download functionality is working
        
        return {"cid": cid}
    except Exception as e:
        if "File exists in metadata but not found in blockchain" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{file_hash}")
async def delete_file(
    file_hash: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        normalized_username = current_user["username"].lower()
        db_user = users_collection.find_one({"username": normalized_username})
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        files = db_user.get("files", [])
        new_files = [f for f in files if (f["file_hash"] if isinstance(f, dict) else f.file_hash) != file_hash]
        users_collection.update_one(
            {"username": normalized_username},
            {"$set": {"files": new_files}}
        )
        cid = await blockchain_service.get_cid_by_hash(file_hash)
        tx_hash = await blockchain_service.remove_cid(None, cid) if cid else None
        return {"status": "success", "tx_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))