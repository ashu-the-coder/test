from fastapi import APIRouter, HTTPException, Request
from services.blockchain import BlockchainService
import logging
from pymongo import MongoClient
import os
from models.user import User, FileMetadata
from fastapi.responses import JSONResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
blockchain_service = BlockchainService()

# Get MongoDB connection and collections
try:
    from utils.mongodb import get_mongo_connection, get_users_collection
    mongo_client, db = get_mongo_connection()
    users_collection = get_users_collection()
    print("Verification route connected to MongoDB successfully")
except Exception as e:
    print(f"Verification route failed to connect to MongoDB: {str(e)}")
    # Let FastAPI handle the exception

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
    db_user = users_collection.find_one({"username": normalized_username})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    wallet_address = db_user.get("wallet_address", None)
    files = db_user.get("files", [])
    file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
    return User(username=username, wallet_address=wallet_address, files=file_objs)

@router.options("/verify-cid")
async def options_verify_cid(request: Request):
    return JSONResponse(status_code=200, content={"message": "CORS preflight response"})

@router.options("/{path:path}")
async def verification_options_handler(path: str):
    """
    Catch-all OPTIONS handler for verification routes.
    """
    logger.info(f"Handling OPTIONS request for verification path: /{path}")
    return JSONResponse(
        content={"message": "OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin, Content-Language, Accept-Language",
        },
    )