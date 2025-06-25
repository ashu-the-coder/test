import os
from datetime import datetime
from typing import List, Dict, Optional
from models.file_metadata import FileMetadata
from utils.mongodb import get_mongo_connection

class MetadataService:
    def __init__(self):
        # Get MongoDB connection
        try:
            self.client, self.db = get_mongo_connection()
            # Use a dedicated collection for file metadata
            self.metadata_collection = self.db['file_metadata']
            # Create indexes if needed
            self.metadata_collection.create_index([("user", 1), ("file_hash", 1)], unique=True)
            print("MetadataService connected to MongoDB successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB in MetadataService: {str(e)}")
            raise
    
    async def store_metadata(self, metadata: FileMetadata):
        # Convert metadata to dictionary
        metadata_dict = metadata.dict()
        
        # Use upsert to either update existing record or create new one
        try:
            result = self.metadata_collection.update_one(
                {"user": metadata.user, "file_hash": metadata.file_hash},
                {"$set": metadata_dict},
                upsert=True
            )
            print(f"Stored metadata for file {metadata.file_hash}: {'Created' if result.upserted_id else 'Updated'}")
            return True
        except Exception as e:
            print(f"Error storing metadata: {str(e)}")
            return False
    
    async def get_user_files(self, user: str) -> List[Dict]:
        try:
            # Find all files for this user
            cursor = self.metadata_collection.find({"user": user})
            # Convert cursor to list and remove MongoDB _id
            files = []
            for file in cursor:
                if '_id' in file:
                    del file['_id']
                files.append(file)
            return files
        except Exception as e:
            print(f"Error getting user files: {str(e)}")
            return []
    
    async def get_file_metadata(self, user: str, file_hash: str) -> Optional[Dict]:
        try:
            result = self.metadata_collection.find_one({"user": user, "file_hash": file_hash})
            if result and '_id' in result:
                del result['_id']  # Remove MongoDB _id
            return result
        except Exception as e:
            print(f"Error getting file metadata: {str(e)}")
            return None
    
    async def remove_metadata(self, user: str, file_hash: str):
        try:
            result = self.metadata_collection.delete_one({"user": user, "file_hash": file_hash})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error removing file metadata: {str(e)}")
            return False