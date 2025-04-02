import os
import requests
from fastapi import UploadFile
from dotenv import load_dotenv
from typing import Dict, Any

class IPFSService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("PINATA_API_KEY")
        self.api_secret = os.getenv("PINATA_API_SECRET")
        self.base_url = "https://api.pinata.cloud"
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.api_secret
        }
    
    async def upload_file(self, file: UploadFile) -> str:
        """Upload a file to Pinata IPFS and return the CID"""
        try:
            url = f"{self.base_url}/pinning/pinFileToIPFS"
            
            # Read file content
            file_content = await file.read()
            
            # Prepare the files for upload
            files = {
                'file': (file.filename, file_content)
            }
            
            # Upload to Pinata
            response = requests.post(
                url,
                files=files,
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to upload to Pinata: {response.text}")
            
            return response.json()["IpfsHash"]
        
        except Exception as e:
            raise Exception(f"Error uploading file to IPFS: {str(e)}")
        
        finally:
            await file.seek(0)  # Reset file pointer
    
    async def get_file_metadata(self, cid: str) -> Dict[str, Any]:
        """Get metadata for a file from Pinata"""
        try:
            url = f"{self.base_url}/pinning/pinList?hashContains={cid}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get metadata from Pinata: {response.text}")
            
            pins = response.json()["rows"]
            return pins[0] if pins else {}
        
        except Exception as e:
            raise Exception(f"Error getting file metadata: {str(e)}")
    
    async def get_file(self, cid: str) -> bytes:
        """Get file content from IPFS"""
        try:
            url = f"https://gateway.pinata.cloud/ipfs/{cid}"
            response = requests.get(url)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get file from IPFS: {response.text}")
            
            return response.content
        
        except Exception as e:
            raise Exception(f"Error getting file from IPFS: {str(e)}")
    
    async def unpin_file(self, cid: str) -> bool:
        """Remove a file from Pinata"""
        try:
            url = f"{self.base_url}/pinning/unpin/{cid}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to unpin file from Pinata: {response.text}")
            
            return True
        
        except Exception as e:
            raise Exception(f"Error unpinning file: {str(e)}")