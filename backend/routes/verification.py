from fastapi import APIRouter, HTTPException
from services.blockchain import BlockchainService
import logging

router = APIRouter()
blockchain_service = BlockchainService()

@router.post("/verify-cid")
async def verify_cid_from_blockchain(file_hash: str):
    try:
        logging.info(f"Attempting to retrieve CID for hash: {file_hash}")
        cid = await blockchain_service.get_cid_by_hash(file_hash)
        logging.info(f"Successfully verified CID {cid} for hash {file_hash}")
        return {"cid": cid, "status": "verified"}
    except Exception as e:
        logging.error(f"CID verification failed for hash {file_hash}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))