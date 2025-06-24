from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import os
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User, FileMetadata, Enterprise
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

class EnterpriseCreate(BaseModel):
    company_name: str
    business_email: str
    password: str
    industry: str
    employee_count: int
    contact_person: str
    contact_phone: Optional[str] = None
    user_type: str = "enterprise"
    wallet_address: Optional[str] = None

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

def create_access_token(data: dict, user_role: str = "individual", enterprise_id: str = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "role": user_role,  # Add user role to token
        "enterprise_id": enterprise_id  # Add enterprise ID if present
    })
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
        
def get_current_active_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    normalized_username = current_user["username"].lower()
    db_user = users_collection.find_one({"username": normalized_username})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build user data dictionary with more information
    user_data = {
        "username": current_user["username"],
        "user_id": str(db_user.get("_id")),
        "wallet_address": db_user.get("wallet_address"),
        "role": db_user.get("user_type", "individual")
    }
    
    # Add enterprise-specific fields if applicable
    if db_user.get("user_type") == "enterprise":
        enterprise_fields = [
            "company_name", "business_email", "industry", 
            "employee_count", "contact_person", "contact_phone"
        ]
        for field in enterprise_fields:
            if field in db_user:
                user_data[field] = db_user[field]
    
    return user_data

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

@router.post("/enterprise/register", response_model=Token)
async def register_enterprise(enterprise: EnterpriseCreate):
    # Generate a username from the business email or company name (sanitized)
    normalized_username = enterprise.business_email.lower().split('@')[0]
    
    # Check if username already exists
    if users_collection.find_one({"username": normalized_username}):
        # Try with company name if email username is taken
        normalized_username = enterprise.company_name.lower().replace(' ', '_')
        
        # Check again with this new username
        if users_collection.find_one({"username": normalized_username}):
            # Add random numbers if both are taken
            import random
            normalized_username += f"_{random.randint(1000, 9999)}"
    
    # Create enterprise user in database
    users_collection.insert_one({
        "username": normalized_username,
        "password": enterprise.password,
        "wallet_address": enterprise.wallet_address or "",  # Optional for enterprise users initially
        "files": [],
        "user_type": "enterprise",
        "company_name": enterprise.company_name,
        "business_email": enterprise.business_email,
        "industry": enterprise.industry,
        "employee_count": enterprise.employee_count,
        "contact_person": enterprise.contact_person,
        "contact_phone": enterprise.contact_phone or ""
    })
    
    # Create access token
    access_token = create_access_token(data={"sub": normalized_username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    normalized_username = user.username.lower()
    db_user = users_collection.find_one({"username": normalized_username})
    if not db_user:
        raise HTTPException(status_code=401, detail=f"Username '{user.username}' is not registered")
    if db_user['password'] != user.password:
        raise HTTPException(status_code=401, detail="Invalid password")
        
    # Get user role and enterprise ID if available
    user_role = db_user.get("role", db_user.get("user_type", "individual"))
    enterprise_id = str(db_user.get("_id")) if user_role == "enterprise" else None
    
    # Create token with role information
    access_token = create_access_token(
        data={"sub": user.username}, 
        user_role=user_role, 
        enterprise_id=enterprise_id
    )
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

class EnterpriseUpdate(BaseModel):
    company_name: str
    business_email: str
    industry: str
    employee_count: int
    contact_person: str
    contact_phone: Optional[str] = None

@router.put("/enterprise/update", response_model=User)
async def update_enterprise_profile(enterprise: EnterpriseUpdate, current_user: dict = Depends(get_current_user)):
    normalized_username = current_user["username"].lower()
    db_user = users_collection.find_one({"username": normalized_username})
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update enterprise fields
    users_collection.update_one(
        {"username": normalized_username},
        {"$set": {
            "company_name": enterprise.company_name,
            "business_email": enterprise.business_email,
            "industry": enterprise.industry,
            "employee_count": enterprise.employee_count,
            "contact_person": enterprise.contact_person,
            "contact_phone": enterprise.contact_phone or "",
            "user_type": "enterprise"  # Ensure user_type is set to enterprise
        }}
    )
    
    # Get updated user
    updated_user = users_collection.find_one({"username": normalized_username})
    if not updated_user:
        raise HTTPException(status_code=404, detail="Failed to retrieve updated profile")
    
    wallet_address = updated_user.get("wallet_address", None)
    files = updated_user.get("files", [])
    file_objs = [FileMetadata(**f) if not isinstance(f, FileMetadata) else f for f in files]
    
    # Convert MongoDB document to Pydantic model
    return User(
        username=updated_user["username"],
        wallet_address=wallet_address,
        files=file_objs,
        user_type=updated_user.get("user_type", "individual"),
        **{k: updated_user.get(k) for k in ["company_name", "business_email", "industry", "employee_count", "contact_person", "contact_phone"] if k in updated_user}
    )