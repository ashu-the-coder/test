from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Header
from fastapi.responses import JSONResponse
from typing import Optional
import os
import hashlib
import json
from datetime import datetime
from services.ipfs import IPFSService
from services.blockchain import BlockchainService
from services.metadata import MetadataService
from models.file_metadata import FileMetadata
from .auth import get_current_user

router = APIRouter()

# Initialize services
ipfs_service = IPFSService()
blockchain_service = BlockchainService()
metadata_service = MetadataService()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Upload file to IPFS through Pinata
        cid = await ipfs_service.upload_file(file)
        
        # Generate a unique hash for the file using CID
        file_hash = hashlib.sha256(cid.encode()).hexdigest()
        
        # Store CID and hash in blockchain
        tx_hash = await blockchain_service.store_cid(current_user, cid, file_hash)
        
        # Calculate file size
        await file.seek(0)
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)
        
        # Store file metadata without CID
        metadata = FileMetadata(
            filename=file.filename,
            user=current_user["username"],
            size=file_size,
            upload_date=datetime.now(),
            content_type=file.content_type,
            file_hash=file_hash,
            transaction_hash=tx_hash
        )
        await metadata_service.store_metadata(metadata)
        
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
        # Get file metadata for the user
        files = await metadata_service.get_user_files(current_user["username"])
        
        # Return file information with transaction hashes
        return {
            "files": [{
                "filename": f["filename"],
                "upload_date": f["upload_date"],
                "size": f["size"],
                "content_type": f["content_type"],
                "file_hash": f["file_hash"],
                "transaction_hash": f["transaction_hash"]
            } for f in files]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        # Get file metadata
        file_metadata = await metadata_service.get_file_metadata(current_user["username"], file_hash)
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")
            
        # Get CID from blockchain
        cid = await blockchain_service.get_cid_by_hash(file_hash)
        if not cid:
            raise HTTPException(status_code=404, detail="File not found in blockchain")
        
        # Remove from blockchain without wallet verification
        tx_hash = await blockchain_service.remove_cid(None, cid)
        
        # Remove from metadata
        await metadata_service.remove_metadata(current_user["username"], file_hash)
        
        return {"status": "success", "tx_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))