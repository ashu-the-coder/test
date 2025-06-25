import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from models.file_metadata import FileMetadata
from utils.mongodb import get_mongo_connection

# Configure logging
logger = logging.getLogger(__name__)

class MetadataService:
    def __init__(self):
        # Get MongoDB connection
        try:
            self.client, self.db = get_mongo_connection()
            # Use a dedicated collection for file metadata
            self.metadata_collection = self.db['file_metadata']
            # Create indexes if needed
            self.metadata_collection.create_index([("user_id", 1), ("file_hash", 1)], unique=True)
            self.metadata_collection.create_index([("enterprise_id", 1)])
            logger.info("MetadataService connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB in MetadataService: {str(e)}")
            raise
    
    async def store_metadata(self, metadata: FileMetadata):
        """
        Store file metadata for either individual (B2C) or enterprise users
        
        Args:
            metadata: The file metadata to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert metadata to dictionary
        metadata_dict = metadata.dict()
        
        # Extract user information and handle both B2C and enterprise users
        user_id = self._extract_user_id(metadata.user)
        
        # Create query document based on user type
        query = {"file_hash": metadata.file_hash}
        if isinstance(metadata.user, dict) and "enterprise_id" in metadata.user:
            # Enterprise user
            query["enterprise_id"] = metadata.user["enterprise_id"]
            metadata_dict["user_type"] = "enterprise"
            metadata_dict["enterprise_id"] = metadata.user["enterprise_id"]
            metadata_dict["user_id"] = user_id
        else:
            # B2C/Individual user
            query["user_id"] = user_id
            metadata_dict["user_type"] = "individual"
            metadata_dict["user_id"] = user_id
        
        # Use upsert to either update existing record or create new one
        try:
            result = self.metadata_collection.update_one(
                query,
                {"$set": metadata_dict},
                upsert=True
            )
            logger.info(f"Stored metadata for file {metadata.file_hash}: {'Created' if result.upserted_id else 'Updated'}")
            return True
        except Exception as e:
            logger.error(f"Error storing metadata: {str(e)}")
            return False
    
    async def get_user_files(self, user: Union[str, Dict[str, Any]]) -> List[Dict]:
        """
        Get all files for a user (both B2C and enterprise users)
        
        Args:
            user: Either a username string (B2C) or user dict with enterprise info
            
        Returns:
            List[Dict]: List of file metadata
        """
        try:
            # Create query based on user type
            query = {}
            if isinstance(user, dict):
                # Enterprise user
                if "enterprise_id" in user:
                    query["enterprise_id"] = user["enterprise_id"]
                if "username" in user:
                    query["user_id"] = user["username"].lower()
            else:
                # B2C/Individual user
                query["user_id"] = user.lower()
                query["user_type"] = "individual"
                
            logger.debug(f"Querying files with filter: {query}")
            
            # Find all files for this user
            cursor = self.metadata_collection.find(query)
            
            # Convert cursor to list and remove MongoDB _id
            files = []
            for file in cursor:
                if '_id' in file:
                    del file['_id']
                files.append(file)
                
            logger.info(f"Found {len(files)} files for user {user}")
            return files
        except Exception as e:
            logger.error(f"Error getting user files: {str(e)}")
            return []
    
    async def get_file_metadata(self, user: Union[str, Dict[str, Any]], file_hash: str) -> Optional[Dict]:
        """
        Get file metadata for a specific file
        
        Args:
            user: Either a username string (B2C) or user dict with enterprise info
            file_hash: The hash of the file to get metadata for
            
        Returns:
            Optional[Dict]: The file metadata or None if not found
        """
        try:
            # Create query based on user type and file hash
            query = {"file_hash": file_hash}
            
            if isinstance(user, dict):
                # Enterprise user
                if "enterprise_id" in user:
                    query["enterprise_id"] = user["enterprise_id"]
                if "username" in user:
                    query["user_id"] = user["username"].lower()
            else:
                # B2C/Individual user
                query["user_id"] = user.lower()
            
            logger.debug(f"Querying file metadata with filter: {query}")
            
            # Find the file metadata
            result = self.metadata_collection.find_one(query)
            
            if result and '_id' in result:
                del result['_id']  # Remove MongoDB _id
                
            return result
        except Exception as e:
            logger.error(f"Error getting file metadata: {str(e)}")
            return None
    
    async def remove_metadata(self, user: Union[str, Dict[str, Any]], file_hash: str):
        """
        Remove file metadata for a specific file
        
        Args:
            user: Either a username string (B2C) or user dict with enterprise info
            file_hash: The hash of the file to remove metadata for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create query based on user type and file hash
            query = {"file_hash": file_hash}
            
            if isinstance(user, dict):
                # Enterprise user
                if "enterprise_id" in user:
                    query["enterprise_id"] = user["enterprise_id"]
                if "username" in user:
                    query["user_id"] = user["username"].lower()
            else:
                # B2C/Individual user
                query["user_id"] = user.lower()
            
            logger.debug(f"Removing file metadata with filter: {query}")
            
            # Delete the file metadata
            result = self.metadata_collection.delete_one(query)
            success = result.deleted_count > 0
            
            if success:
                logger.info(f"Successfully removed metadata for file hash {file_hash}")
            else:
                logger.warning(f"No metadata found to remove for file hash {file_hash}")
                
            return success
        except Exception as e:
            logger.error(f"Error removing file metadata: {str(e)}")
            return False
        
    def _extract_user_id(self, user: Union[str, Dict[str, Any]]) -> str:
        """
        Extract a user ID from either a string username or a user dictionary
        
        Args:
            user: Either a username string or user dict
            
        Returns:
            str: The extracted user ID
        """
        if isinstance(user, dict):
            # For enterprise users, prefer username as user_id
            if "username" in user:
                return user["username"].lower()
            # Fall back to user_id if present
            elif "user_id" in user:
                return user["user_id"].lower()
            # Fall back to id if present
            elif "id" in user:
                return str(user["id"]).lower()
            # If all else fails, use a hash of the object
            else:
                import hashlib
                import json
                # Create a deterministic hash of the user object
                user_str = json.dumps(user, sort_keys=True)
                return hashlib.md5(user_str.encode()).hexdigest()
        else:
            # For string usernames, just return lowercase
            return str(user).lower()
            
    async def get_enterprise_files(self, enterprise_id: str) -> List[Dict]:
        """
        Get all files for an enterprise
        
        Args:
            enterprise_id: The enterprise ID
            
        Returns:
            List[Dict]: List of file metadata
        """
        try:
            # Find all files for this enterprise
            cursor = self.metadata_collection.find({"enterprise_id": enterprise_id})
            
            # Convert cursor to list and remove MongoDB _id
            files = []
            for file in cursor:
                if '_id' in file:
                    del file['_id']
                files.append(file)
                
            logger.info(f"Found {len(files)} files for enterprise {enterprise_id}")
            return files
        except Exception as e:
            logger.error(f"Error getting enterprise files: {str(e)}")
            return []
            
    async def search_metadata(self, query: Dict[str, Any]) -> List[Dict]:
        """
        Search for file metadata using a custom query
        
        Args:
            query: MongoDB query document
            
        Returns:
            List[Dict]: List of matching file metadata
        """
        try:
            # Find all files matching the query
            cursor = self.metadata_collection.find(query)
            
            # Convert cursor to list and remove MongoDB _id
            files = []
            for file in cursor:
                if '_id' in file:
                    del file['_id']
                files.append(file)
                
            logger.info(f"Found {len(files)} files matching query {query}")
            return files
        except Exception as e:
            logger.error(f"Error searching metadata: {str(e)}")
            return []