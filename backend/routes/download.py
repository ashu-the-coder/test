from fastapi import APIRouter, HTTPException, Depends
from services.blockchain import BlockchainService
from services.ipfs import IPFSService
from routes.auth import get_current_user
from fastapi.responses import StreamingResponse
import io

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