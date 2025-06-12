from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import os
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User, FileMetadata
from services.metadata import MetadataService
from pymongo import MongoClient

router = APIRouter()
security = HTTPBearer()
metadata_service = MetadataService()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:%40dminXinetee%40123@100.123.165.22:27017")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[os.getenv("MONGO_DB", "xinetee")]
users_collection = db[os.getenv("MONGO_USERS_COLLECTION", "users")]

class UserCreate(BaseModel):
    username: str
    password: str
    wallet_address: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return {"username": username}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    normalized_username = user.username.lower()
    if users_collection.find_one({"username": normalized_username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    users_collection.insert_one({
        "username": normalized_username,
        "password": user.password,
        "wallet_address": user.wallet_address,
        "files": []
    })
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    normalized_username = user.username.lower()
    db_user = users_collection.find_one({"username": normalized_username})
    if not db_user:
        raise HTTPException(status_code=401, detail=f"Username '{user.username}' is not registered")
    if db_user['password'] != user.password:
        raise HTTPException(status_code=401, detail="Invalid password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    normalized_username = current_user["username"].lower()
    db_user = users_collection.find_one({"username": normalized_username})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    wallet_address = db_user.get("wallet_address", None)
    files = db_user.get("files", [])
    file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
    return User(username=current_user["username"], wallet_address=wallet_address, files=file_objs)

@router.get("/profile", response_model=User)
async def get_profile(current_user: dict = Depends(get_current_user)):
    normalized_username = current_user["username"].lower()
    db_user = users_collection.find_one({"username": normalized_username})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    wallet_address = db_user.get("wallet_address", None)
    files = db_user.get("files", [])
    file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
    return User(username=current_user["username"], wallet_address=wallet_address, files=file_objs)

@router.get("/all-users", response_model=list[User])
async def get_all_users():
    users = []
    for db_user in users_collection.find():
        files = db_user.get("files", [])
        file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
        users.append(User(username=db_user["username"], wallet_address=db_user.get("wallet_address"), files=file_objs))
    return users