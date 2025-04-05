from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import os
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

import json
import os.path

# File-based user storage
USER_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.json')

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
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
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    users = load_users()
    normalized_username = user.username.lower()
    if normalized_username in users:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # In production, hash the password before storing
    users[normalized_username] = {
        "password": user.password
    }
    save_users(users)
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    users = load_users()
    print(f"Attempting login for user: {user.username}")
    print(f"Available users: {list(users.keys())}")
    
    if not users:
        print("No users found in database")
        raise HTTPException(status_code=401, detail="No users registered in the system")
    
    normalized_username = user.username.lower()
    if normalized_username not in users:
        print(f"User {user.username} not found in database")
        raise HTTPException(status_code=401, detail=f"Username '{user.username}' is not registered")
    
    stored_password = users[normalized_username]
    if stored_password != user.password:
        print(f"Invalid password attempt for user: {user.username}")
        raise HTTPException(status_code=401, detail="Invalid password")
    
    print(f"Successful login for user: {user.username}")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}