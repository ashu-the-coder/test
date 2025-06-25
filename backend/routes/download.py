from fastapi import APIRouter, HTTPException, Depends, Request
from services.blockchain import BlockchainService
from services.ipfs import IPFSService
from services.metadata import MetadataService
from routes.auth import get_current_user
from fastapi.responses import StreamingResponse, JSONResponse, JSONResponse
import io
import logging
from models.user import User, FileMetadata

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
blockchain_service = BlockchainService()
ipfs_service = IPFSService()

@router.get("/storage/download/{file_hash}")
async def download_file(file_hash: str, current_user: dict = Depends(get_current_user)):
    try:
        try:
            # Get CID from blockchain using file hash
            cid = await blockchain_service.get_cid_by_hash(file_hash)
        except Exception as e:
            if "File not found" in str(e):
                raise HTTPException(status_code=404, detail="File not found in blockchain. The file may have been deleted.")
            raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
            
        # Verify ownership
        try:
            is_owner = await blockchain_service.verify_ownership(current_user["address"], cid)
            if not is_owner:
                raise HTTPException(status_code=403, detail="Not authorized to download this file")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error verifying file ownership: {str(e)}")
        
        try:
            # Get filename from blockchain
            filename = await blockchain_service.get_filename_by_hash(file_hash)
            if not filename:
                filename = file_hash

            # Get file from IPFS
            file_content = await ipfs_service.get_file(cid)
            
            # Create a stream from the file content
            stream = io.BytesIO(file_content)
            
            # Return the file as a streaming response with filename in headers
            headers = {
                "Content-Disposition": f"attachment; filename={filename}"
            }
            return StreamingResponse(
                stream,
                media_type="application/octet-stream",
                headers=headers
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading file content: {str(e)}")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{username}", response_model=User)
async def get_user_by_username(username: str):
    try:
        from utils.mongodb import get_users_collection
        users_collection = get_users_collection()
        
        # Normalize username
        normalized_username = username.lower()
        
        # Get user from MongoDB
        db_user = users_collection.find_one({"username": normalized_username})
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get wallet address
        wallet_address = db_user.get("wallet_address", None)
        
        # Get user files using metadata service
        from services.metadata import MetadataService
        metadata_service = MetadataService()
        
        # Get files - first try with username string for B2C users
        files = await metadata_service.get_user_files(normalized_username)
        
        # If no files found and it might be an enterprise user, try with user dict
        if not files and "enterprise_id" in db_user:
            user_dict = {"username": normalized_username, "enterprise_id": db_user["enterprise_id"]}
            files = await metadata_service.get_user_files(user_dict)
        
        # If still no files, check the legacy storage in user document
        if not files:
            files = db_user.get("files", [])
        
        # Convert all files to proper FileMetadata objects
        file_objs = []
        for f in files:
            try:
                if isinstance(f, dict):
                    file_objs.append(FileMetadata(**f))
                else:
                    file_objs.append(f)
            except Exception as e:
                pass  # Skip invalid files
                
        return User(username=username, wallet_address=wallet_address, files=file_objs)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user data: {str(e)}")

@router.options("/{path:path}")
async def download_options_handler(path: str):
    """
    Catch-all OPTIONS handler for download routes.
    """
    logger.info(f"Handling OPTIONS request for download path: /{path}")
    return JSONResponse(
        content={"message": "OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin, Content-Language, Accept-Language",
        },
    )