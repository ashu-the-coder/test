from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path
import os
import pymongo
from pymongo import MongoClient
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
import os
import pymongo
from pymongo import MongoClient
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

app = FastAPI(title="Xinete Storage Platform")

# Configure logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Function to extract database name from MongoDB URI
def extract_db_name_from_uri(uri):
    """
    Parse MongoDB URI to extract database name, handling cases with
    authentication credentials and query parameters properly.
    
    Returns the database name or a default value if not found
    """
    default_db = "xinete_storage"
    
    if not uri:
        return default_db
        
    try:
        # Parse the URI
        parsed = urlparse(uri)
        
        # Extract path and remove leading slash
        path = parsed.path
        if path.startswith('/'):
            path = path[1:]
            
        # If path has query parameters, extract just the DB name
        if '?' in path:
            path = path.split('?')[0]
            
        # Return the extracted database name or default
        return path if path else default_db
    except Exception as e:
        logger.error(f"Error parsing MongoDB URI: {e}")
        return default_db

# Connect to MongoDB using our utility module
from utils.mongodb import get_mongo_connection

# Connect to MongoDB
try:
    client, db = get_mongo_connection()
    
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
    
    # Log the database being used
    logger.info(f"Using database: {db.name}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Configure CORS
# When allow_credentials=True, cannot use wildcard "*" for origins
default_origins = [
    "http://164.52.203.17:5173",
    "http://164.52.203.17:8000",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://100.123.165.22:5173",  # Add your specific IP
    "http://100.123.165.22:8000",
]

# Add any additional origins from environment
env_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
additional_origins = [origin.strip() for origin in env_origins if origin.strip()]
allowed_origins = default_origins + additional_origins

# If in development mode, make sure we're being permissive
if os.getenv("ENVIRONMENT", "").lower() != "production":
    # Add common development origins
    dev_origins = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:4000",
        "http://127.0.0.1:4000",
        # Include HTTPS variants as well
        "https://localhost:5173",
        "https://127.0.0.1:5173",
        "https://localhost:3000",
        "https://127.0.0.1:3000",
        "https://localhost:8080",
        "https://127.0.0.1:8080"
    ]
    allowed_origins.extend(dev_origins)
    
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

# Comprehensive list of headers that might be used by clients
all_allowed_headers = [
    "Content-Type", 
    "Authorization", 
    "X-Requested-With", 
    "Accept", 
    "Origin", 
    "Content-Language", 
    "Accept-Language",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
    "Access-Control-Allow-Origin",
    "Access-Control-Allow-Credentials",
    "X-CSRF-Token",
    "X-Wallet-Address",  # Add wallet address header
    "X-API-Key"  # Common for API authentication
]

# In development environments, we might need to be more permissive
# CORS configuration - use a more permissive setup in all environments to debug issues
logger.info("Configuring CORS to handle preflight requests properly")

# Always allow all origins temporarily to debug CORS issues
# This is a permissive configuration that should work in all cases
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins 
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # Allow all headers
    expose_headers=["Content-Length", "Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.debug(f"Request headers: {request.headers}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Middleware to debug CORS issues and add headers when needed
@app.middleware("http")
async def cors_debug_middleware(request, call_next):
    """
    Middleware to debug CORS issues and add headers when needed.
    """
    # For OPTIONS requests, log details
    if request.method == "OPTIONS":
        origin = request.headers.get("origin", "unknown")
        req_method = request.headers.get("access-control-request-method", "unknown")
        req_headers = request.headers.get("access-control-request-headers", "unknown")
        logger.info(f"OPTIONS request from {origin}, method: {req_method}, headers: {req_headers}")
        
        # If it's a preflight request, respond immediately with appropriate headers
        if req_method and req_headers:
            # This is a CORS preflight request - respond directly
            # Make sure to include X-Wallet-Address in allowed headers if needed
            allowed_headers = req_headers
            if "x-wallet-address" not in req_headers.lower():
                allowed_headers = f"{req_headers}, X-Wallet-Address"
            
            headers = {
                "Access-Control-Allow-Origin": origin if origin != "unknown" else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": allowed_headers,
                "Access-Control-Allow-Credentials": "true" if origin != "unknown" and origin != "*" else "false",
                "Access-Control-Max-Age": "600",
            }
            return JSONResponse(content={"message": "OK"}, status_code=200, headers=headers)
    
    # Continue with the request
    response = await call_next(request)
    
    # Log CORS-related responses
    if response.status_code == 400 and request.method == "OPTIONS":
        logger.warning("OPTIONS request returned 400 Bad Request. CORS issue likely.")
        
    return response

# Health check endpoint
@app.get("/")
async def read_root():
    return {"status": "healthy", "service": "Xinete Storage Platform"}

# Ensure MongoDB collections exist
try:
    # Create MongoDB collections if they don't exist
    collections_to_check = ["users", "enterprises", "products", "batches", "trace_events", "inventory", "audit_logs", "file_metadata"]
    
    for collection_name in collections_to_check:
        if collection_name not in db.list_collection_names():
            logger.info(f"Creating MongoDB collection: {collection_name}")
            db.create_collection(collection_name)
    
    logger.info("MongoDB collections initialized")
except Exception as e:
    logger.error(f"Error initializing MongoDB collections: {str(e)}")

# Import routes after app initialization to avoid circular imports
from routes import auth, storage, download, verification, enterprise, product, batch, traceability, inventory, audit

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(storage.router, prefix="/storage", tags=["storage"])
app.include_router(download.router, prefix="/api", tags=["download"])
app.include_router(verification.router, prefix="/api/verification", tags=["verification"])
app.include_router(enterprise.router, prefix="/enterprise", tags=["enterprise"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(batch.router, prefix="/batch", tags=["batch"])
app.include_router(traceability.router, prefix="/trace", tags=["traceability"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])

# Register global OPTIONS handler at the highest level
@app.options("/{full_path:path}")
async def global_options_catch_all(request: Request, full_path: str):
    """
    Global catch-all handler for OPTIONS preflight requests.
    This will take precedence over the route-specific handlers.
    """
    origin = request.headers.get("origin", "*")
    requested_method = request.headers.get("access-control-request-method", "")
    requested_headers = request.headers.get("access-control-request-headers", "")
    
    logger.info(f"Master OPTIONS handler called for path: /{full_path}")
    logger.info(f"Origin: {origin}, Method: {requested_method}, Headers: {requested_headers}")
    
    # Be extremely permissive with OPTIONS requests
    # Make sure to include X-Wallet-Address in allowed headers if not already in requested_headers
    allowed_headers = requested_headers
    if requested_headers and "x-wallet-address" not in requested_headers.lower():
        allowed_headers = f"{requested_headers}, x-wallet-address"
    
    return JSONResponse(
        content={"message": "OK"},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": origin if origin != "*" else "*",
            "Access-Control-Allow-Credentials": "true" if origin != "*" else "false",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": allowed_headers or "*",
            "Access-Control-Max-Age": "600",
            "Content-Type": "application/json",
            "Content-Length": "2"
        },
    )

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    # Configure host for VM deployment
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)