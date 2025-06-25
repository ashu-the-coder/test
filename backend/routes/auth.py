from fastapi import APIRouter, HTTPException, Depends, Form, Header, Request, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
import os
import logging
from datetime import datetime, timedelta
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import User, FileMetadata, Enterprise
from services.metadata import MetadataService
from pymongo import MongoClient
from utils.mongodb import get_mongo_connection, get_users_collection

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()
metadata_service = MetadataService()

# Get MongoDB connection and collections
try:
    from utils.mongodb import get_mongo_connection, get_users_collection
    mongo_client, db = get_mongo_connection()
    users_collection = get_users_collection()
    print("Auth route connected to MongoDB successfully")
except Exception as e:
    print(f"Auth route failed to connect to MongoDB: {str(e)}")
    # Let FastAPI handle the exception but we'll still attempt to initialize
    # Get MongoDB connection directly for authentication routes
    try:
        mongo_client = MongoClient(
            host=f'mongodb://100.123.165.22:27017/',
            username="admin",
            password="@dminXinetee@123",
            authSource='admin',
            connectTimeoutMS=5000
        )
        db = mongo_client["xinetee"]
        users_collection = db["users"]
        print("Auth route connected to MongoDB with fallback method")
    except Exception as fallback_err:
        print(f"All MongoDB connection attempts failed: {str(fallback_err)}")

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
async def login(
    request: Request,
    user: Optional[UserLogin] = None, 
    username: Optional[str] = Form(default=None), 
    password: Optional[str] = Form(default=None),
    user_agent: Optional[str] = Header(default=None)
):
    try:
        # Get client IP address for logging
        client_ip = request.client.host if request else "unknown"
        client_agent = user_agent or "unknown"
        
        # Log request details
        logger.info(f"Login request from IP: {client_ip}, User-Agent: {client_agent}")
        
        # Handle both JSON body and form data
        login_username = None
        login_password = None
        
        # Check for form data first
        if username is not None and password is not None:
            login_username = username
            login_password = password
            logger.info(f"Login attempt using form data for username: {login_username}")
        # Then check for JSON data
        elif user is not None:
            login_username = user.username
            login_password = user.password
            logger.info(f"Login attempt using JSON for username: {login_username}")
        # Finally try to get data from request body
        else:
            try:
                body = await request.json()
                login_username = body.get("username")
                login_password = body.get("password")
                logger.info(f"Login attempt using raw JSON body for username: {login_username}")
            except Exception as e:
                logger.error(f"Error parsing request body: {str(e)}")
                
        # Check if we have credentials
        if not login_username or not login_password:
            logger.warning("Login attempt with missing credentials")
            raise HTTPException(status_code=400, detail="Missing credentials")
            
        normalized_username = login_username.lower()
        logger.info(f"Normalized username for login: {normalized_username}")
        
        # Ensure we have a valid MongoDB connection and users collection
        from utils.mongodb import get_users_collection
        try:
            users_collection = get_users_collection()
            logger.debug("Connected to users collection for login attempt")
        except Exception as e:
            logger.error(f"MongoDB connection error during login: {str(e)}")
            raise HTTPException(status_code=500, detail="Database connection error")
            
        # Attempt to find the user
        try:
            db_user = users_collection.find_one({"username": normalized_username})
            if db_user:
                logger.info(f"User found in database: {normalized_username}")
            else:
                logger.warning(f"User not found in database: {normalized_username}")
        except Exception as e:
            logger.error(f"Error finding user in database: {str(e)}")
            raise HTTPException(status_code=500, detail="Database query error")
            
        if not db_user:
            logger.warning(f"Login failed - user not registered: {login_username}")
            raise HTTPException(status_code=401, detail=f"Username '{login_username}' is not registered")
            
        if db_user['password'] != login_password:
            logger.warning(f"Login failed - incorrect password for user: {normalized_username}")
            raise HTTPException(status_code=401, detail="Invalid password")
            
        # Get user role and enterprise ID if available
        user_role = db_user.get("role", db_user.get("user_type", "individual"))
        enterprise_id = None
        
        # Handle different types of enterprise IDs
        if user_role == "enterprise" or "enterprise_id" in db_user:
            if "enterprise_id" in db_user:
                enterprise_id = str(db_user["enterprise_id"])
            else:
                enterprise_id = str(db_user.get("_id"))
                
        logger.info(f"User {normalized_username} logged in with role: {user_role}, enterprise_id: {enterprise_id}")
        
        # Create token with role information
        access_token = create_access_token(
            data={"sub": normalized_username}, 
            user_role=user_role, 
            enterprise_id=enterprise_id
        )
        logger.info(f"Generated access token for user: {normalized_username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.options("/login")
async def login_options():
    """
    Handle OPTIONS requests for the login endpoint explicitly.
    This helps resolve CORS preflight issues.
    """
    return JSONResponse(
        content={"message": "OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin",
        },
    )

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