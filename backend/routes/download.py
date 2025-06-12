from fastapi import APIRouter, HTTPException, Depends
from services.blockchain import BlockchainService
from services.ipfs import IPFSService
from routes.auth import get_current_user
from fastapi.responses import StreamingResponse
import io
from models.user import User, FileMetadata

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
    from routes.auth import load_users
    users = load_users()
    normalized_username = username.lower()
    user_data = users.get(normalized_username, {})
    wallet_address = user_data.get("wallet_address", None)
    from services.metadata import MetadataService
    metadata_service = MetadataService()
    files = await metadata_service.get_user_files(username)
    file_objs = [FileMetadata(**f) for f in files]
    return User(username=username, wallet_address=wallet_address, files=file_objs)