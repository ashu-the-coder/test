from fastapi import APIRouter, HTTPException
from services.blockchain import BlockchainService
import logging
from routes.auth import user_store
from models.user import User, FileMetadata

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

@router.get("/verify-user/{username}", response_model=User)
async def verify_user_and_files(username: str):
    normalized_username = username.lower()
    user_data = user_store.get(normalized_username, {})
    wallet_address = user_data.get("wallet_address", None)
    files = user_data.get("files", [])
    file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
    return User(username=username, wallet_address=wallet_address, files=file_objs)