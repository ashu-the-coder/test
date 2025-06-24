import os
import requests
from fastapi import UploadFile
from dotenv import load_dotenv
from typing import Dict, Any

class IPFSService:
    def __init__(self):
        load_dotenv()
        self.api_host = os.getenv("IPFS_API_HOST", "127.0.0.1")
        self.api_port = os.getenv("IPFS_API_PORT", "5001")
        self.gateway_port = os.getenv("IPFS_GATEWAY_PORT", "8080")
        self.spawn_port = os.getenv("IPFS_SPAWN_PORT", "4001")
        self.api_url = f"http://{self.api_host}:{self.api_port}/api/v0"
        self.gateway_url = f"http://{self.api_host}:{self.gateway_port}/ipfs"

    async def upload_file(self, file: UploadFile) -> str:
        """Upload a file to self-hosted IPFS and return the CID"""
        try:
            files = {'file': (file.filename, await file.read())}
            response = requests.post(f"{self.api_url}/add", files=files)
            if response.status_code != 200:
                raise Exception(f"Failed to upload to IPFS: {response.text}")
            cid = response.json()["Hash"] if response.headers.get('Content-Type', '').startswith('application/json') else response.text.split(',')[1].split(':')[1].replace('"', '').strip()
            return cid
        except Exception as e:
            raise Exception(f"Error uploading file to IPFS: {str(e)}")
        finally:
            await file.seek(0)

    async def get_file_metadata(self, cid: str) -> Dict[str, Any]:
        """Get metadata for a file from self-hosted IPFS (not supported natively)"""
        return {"cid": cid}

    async def get_file(self, cid: str) -> bytes:
        """Get file content from self-hosted IPFS"""
        try:
            url = f"{self.gateway_url}/{cid}"
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to get file from IPFS: {response.text}")
            return response.content
        except Exception as e:
            raise Exception(f"Error getting file from IPFS: {str(e)}")

    async def unpin_file(self, cid: str) -> bool:
        """Remove a file from self-hosted IPFS"""
        try:
            params = {"arg": cid}
            response = requests.post(f"{self.api_url}/pin/rm", params=params)
            if response.status_code != 200:
                raise Exception(f"Failed to unpin file from IPFS: {response.text}")
            return True
        except Exception as e:
            raise Exception(f"Error unpinning file: {str(e)}")

    async def get_ipfs_view_link(self, cid: str) -> str:
        """
        Get a public IPFS view link for a CID.
        
        This uses the public IPFS gateway at ipfs.io instead of a local gateway,
        which makes it accessible to anyone on the internet.
        
        Args:
            cid: The IPFS CID
            
        Returns:
            str: The public gateway URL
        """
        return f"https://ipfs.io/ipfs/{cid}"