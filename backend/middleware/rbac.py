from fastapi import HTTPException, Depends, Request
from functools import wraps
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from pymongo import MongoClient

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET"))
ALGORITHM = "HS256"

# Setup MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xinete_storage")
client = MongoClient(MONGODB_URL)
db = client.xinete_storage

def verify_user_role(required_roles):
    """
    Middleware to verify if the user has the required role(s)
    required_roles can be a string or a list of roles (any one role is sufficient)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security), *args, **kwargs):
            try:
                token = credentials.credentials
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                
                # Extract user ID and role from token
                user_id = payload.get("sub")
                user_role = payload.get("role", "individual")
                enterprise_id = payload.get("enterprise_id")
                
                # Convert required_roles to list if it's a string
                roles_list = [required_roles] if isinstance(required_roles, str) else required_roles
                
                # For enterprise-specific endpoints, verify user belongs to the enterprise
                path_params = request.path_params
                if "enterprise_id" in path_params and enterprise_id != path_params["enterprise_id"]:
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied: You don't belong to this enterprise"
                    )
                
                # Check if the user has any of the required roles
                if "admin" == user_role or user_role in roles_list:
                    # Admin has access to everything
                    # Or user has one of the required roles
                    # Add user info to request state for use in endpoint handlers
                    request.state.user = {
                        "user_id": user_id,
                        "role": user_role,
                        "enterprise_id": enterprise_id
                    }
                    
                    # For specific permissions, check the database
                    if any(perm.startswith("permission:") for perm in roles_list):
                        required_permission = next(perm.replace("permission:", "") for perm in roles_list if perm.startswith("permission:"))
                        user = db.accounts.find_one({"user_id": user_id})
                        
                        if not user or required_permission not in user.get("permissions", []):
                            raise HTTPException(
                                status_code=403,
                                detail=f"Access denied: Required permission '{required_permission}' not found"
                            )
                    
                    return await func(*args, request=request, **kwargs)
                else:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Access denied: Requires one of these roles: {roles_list}"
                    )
            except jwt.PyJWTError as e:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid authentication token: {str(e)}"
                )
        return wrapper
    return decorator
    
def verify_permission(required_permission):
    """
    Middleware to verify if the user has the required permission
    """
    return verify_user_role(f"permission:{required_permission}")
