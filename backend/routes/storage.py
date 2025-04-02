from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
import os
from services.ipfs import IPFSService
from services.blockchain import BlockchainService
from .auth import get_current_user

router = APIRouter()

# Initialize services
ipfs_service = IPFSService()
blockchain_service = BlockchainService()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    try:
        # Upload file to IPFS through Pinata
        cid = await ipfs_service.upload_file(file)
        
        # Store CID in blockchain
        tx_hash = await blockchain_service.store_cid(current_user, cid)
        
        return {
            "status": "success",
            "cid": cid,
            "tx_hash": tx_hash,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def get_user_files(current_user: str = Depends(get_current_user)):
    try:
        # Get all CIDs for the user from blockchain
        cids = await blockchain_service.get_user_cids(current_user)
        
        # Get file metadata from Pinata for each CID
        files = []
        for cid in cids:
            metadata = await ipfs_service.get_file_metadata(cid)
            files.append({
                "cid": cid,
                "metadata": metadata
            })
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{cid}")
async def get_file(
    cid: str,
    current_user: str = Depends(get_current_user)
):
    try:
        # Verify ownership
        is_owner = await blockchain_service.verify_ownership(current_user, cid)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Not authorized to access this file")
        
        # Get file from IPFS
        file_data = await ipfs_service.get_file(cid)
        return JSONResponse(content=file_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{cid}")
async def delete_file(
    cid: str,
    current_user: str = Depends(get_current_user)
):
    try:
        # Verify ownership
        is_owner = await blockchain_service.verify_ownership(current_user, cid)
        if not is_owner:
            raise HTTPException(status_code=403, detail="Not authorized to delete this file")
        
        # Remove from Pinata
        await ipfs_service.unpin_file(cid)
        
        # Remove from blockchain
        tx_hash = await blockchain_service.remove_cid(current_user, cid)
        
        return {"status": "success", "tx_hash": tx_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))