from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Header
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional, List, Dict, Any
import os
import hashlib
import json
import logging
from datetime import datetime
from pymongo import MongoClient

from services.ipfs import IPFSService
from services.blockchain import BlockchainService
from services.metadata import MetadataService
from models.user import User
from .auth import get_current_user
from models.user import FileMetadata

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
ipfs_service = IPFSService()
blockchain_service = BlockchainService()
metadata_service = MetadataService()

# Get MongoDB connection and collections
try:
    from utils.mongodb import get_mongo_connection, get_users_collection
    mongo_client, db = get_mongo_connection()
    users_collection = get_users_collection()
    logger.info("Storage route connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Storage route failed to connect to MongoDB: {str(e)}")
    # Let FastAPI handle the exception

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Processing file upload: {file.filename} for user: {current_user.get('username', 'unknown')}")
        
        # Upload file to IPFS
        cid = await ipfs_service.upload_file(file)
        file_hash = hashlib.sha256(cid.encode()).hexdigest()
        
        # Store in blockchain
        try:
            tx_hash = await blockchain_service.store_cid(current_user, cid, file_hash)
            logger.info(f"File stored in blockchain with tx_hash: {tx_hash}")
        except Exception as e:
            logger.error(f"Error storing in blockchain: {str(e)}")
            tx_hash = "error-" + hashlib.md5(str(datetime.now()).encode()).hexdigest()
            
        # Get file size
        await file.seek(0)
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)
        
        # Create metadata object
        metadata = FileMetadata(
            filename=file.filename,
            user=current_user,  # Pass the entire user object
            size=file_size,
            upload_date=datetime.now(),
            content_type=file.content_type,
            file_hash=file_hash,
            transaction_hash=tx_hash
        )
        
        # Store metadata using our service - will handle different user types
        success = await metadata_service.store_metadata(metadata)
        if not success:
            logger.warning(f"Failed to store metadata for file {file_hash}")
            
        # Also update the user's files list for backward compatibility
        try:
            normalized_username = current_user.get("username", "").lower()
            if normalized_username:
                users_collection.update_one(
                    {"username": normalized_username},
                    {"$push": {"files": metadata.dict()}},
                    upsert=True
                )
        except Exception as e:
            logger.error(f"Error updating user's files list: {str(e)}")
            
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
    try:
        logger.info(f"Getting files for user: {current_user.get('username', 'unknown')}")
        
        # Get files using metadata service - handles both B2C and enterprise users
        files = await metadata_service.get_user_files(current_user)
        
        # If no files found in metadata service, try legacy approach from users collection
        if not files:
            logger.info("No files found in metadata service, trying legacy approach")
            normalized_username = current_user.get("username", "").lower()
            if normalized_username:
                db_user = users_collection.find_one({"username": normalized_username})
                files = db_user.get("files", []) if db_user else []
                
        # Always return as { files: [...] } for frontend compatibility
        return {"files": [f for f in files]}
    except Exception as e:
        logger.error(f"Error getting user files: {str(e)}")
        return {"files": []}

@router.get("/user", response_model=User)
async def get_user(current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Getting user profile for: {current_user.get('username', 'unknown')}")
        normalized_username = current_user.get("username", "").lower()
        
        # Get user data from database
        db_user = users_collection.find_one({"username": normalized_username}) if normalized_username else None
        wallet_address = db_user.get("wallet_address", None) if db_user else None
        
        # Get files from metadata service
        files = await metadata_service.get_user_files(current_user)
        
        # If no files found in metadata service, try legacy approach
        if not files and db_user:
            logger.info("No files found in metadata service, using files from user document")
            files = db_user.get("files", [])
            
        # Convert all files to FileMetadata objects
        file_objs = []
        for f in files:
            if isinstance(f, dict):
                try:
                    file_objs.append(FileMetadata(**f))
                except Exception as e:
                    logger.warning(f"Error converting file metadata: {str(e)}")
            else:
                file_objs.append(f)
                
        return User(
            username=current_user.get("username", "unknown"),
            wallet_address=wallet_address,
            files=file_objs
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return User(
            username=current_user.get("username", "unknown"),
            wallet_address=None,
            files=[]
        )

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
        # Use self-hosted IPFS gateway for download (ensure correct URL)
        ipfs_gateway = os.getenv("IPFS_GATEWAY", "http://100.123.165.22:8080/ipfs")
        ipfs_url = f"{ipfs_gateway.rstrip('/')}/{cid}"
        return {"ipfs_url": ipfs_url, "cid": cid}
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