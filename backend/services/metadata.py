import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from models.file_metadata import FileMetadata

class MetadataService:
    def __init__(self):
        # Use relative paths from the project root
        self.user_data_dir = 'user_data'
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.metadata_file = os.path.join(self.user_data_dir, 'file_metadata.json')
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w') as f:
                json.dump({}, f)
    
    def _read_metadata(self) -> Dict:
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def _write_metadata(self, data: Dict):
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, default=str)
    
    async def store_metadata(self, metadata: FileMetadata):
        data = self._read_metadata()
        if metadata.user not in data:
            data[metadata.user] = {}
        data[metadata.user][metadata.file_hash] = metadata.dict()
        self._write_metadata(data)
    
    async def get_user_files(self, user: str) -> List[Dict]:
        data = self._read_metadata()
        user_files = data.get(user, {})
        files = list(user_files.values())
        # Convert stored datetime strings back to datetime objects
        for file in files:
            if 'upload_date' in file and isinstance(file['upload_date'], str):
                file['upload_date'] = datetime.strptime(file['upload_date'], '%Y-%m-%d %H:%M:%S.%f')
        return files
    
    async def get_file_metadata(self, user: str, file_hash: str) -> Optional[Dict]:
        data = self._read_metadata()
        user_files = data.get(user, {})
        return user_files.get(file_hash)
    
    async def remove_metadata(self, user: str, file_hash: str):
        data = self._read_metadata()
        if user in data and file_hash in data[user]:
            del data[user][file_hash]
            self._write_metadata(data)