"""
IPFS utility functions for interacting with IPFS storage.
This is a minimal implementation for demonstration purposes.
In a production environment, you would use a more robust IPFS client.
"""

import os
import requests
import json
import io
import hashlib

# Get IPFS configuration from environment
IPFS_API_URL = os.getenv("IPFS_API_URL", "http://localhost:5001/api/v0")
IPFS_GATEWAY_URL = os.getenv("IPFS_GATEWAY_URL", "http://localhost:8080/ipfs")

def add_file_to_ipfs(file_bytes, filename=None):
    """
    Add a file to IPFS and return the CID.
    
    Args:
        file_bytes: The file content as bytes
        filename: Optional filename
        
    Returns:
        str: The IPFS CID
    """
    try:
        # In a production environment, you would use the IPFS HTTP API to upload the file
        # For demonstration, we'll just create a mock CID based on the file content
        mock_cid = "Qm" + hashlib.sha256(file_bytes).hexdigest()[:44]
        return mock_cid
    except Exception as e:
        print(f"Error adding file to IPFS: {str(e)}")
        raise

def add_json_to_ipfs(data):
    """
    Add JSON data to IPFS and return the CID.
    
    Args:
        data: The JSON-serializable data to add
        
    Returns:
        str: The IPFS CID
    """
    try:
        # Convert data to JSON string
        json_str = json.dumps(data)
        # Add as a file to IPFS
        return add_file_to_ipfs(json_str.encode('utf-8'))
    except Exception as e:
        print(f"Error adding JSON to IPFS: {str(e)}")
        raise

def get_from_ipfs(cid):
    """
    Get content from IPFS by CID.
    
    Args:
        cid: The IPFS CID
        
    Returns:
        bytes: The content
    """
    try:
        # In a production environment, you would use the IPFS HTTP API to get the content
        # For demonstration, we'll just return a mock content
        return f"Mock content for CID: {cid}".encode('utf-8')
    except Exception as e:
        print(f"Error getting content from IPFS: {str(e)}")
        raise

def get_ipfs_gateway_url(cid):
    """
    Get the IPFS gateway URL for a CID.
    
    Args:
        cid: The IPFS CID
        
    Returns:
        str: The gateway URL
    """
    return f"{IPFS_GATEWAY_URL}/{cid}"

def get_ipfs_view_link(cid):
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
