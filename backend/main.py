from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
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
# Allow all origins in development, restrict in production
if os.getenv("ENVIRONMENT", "").lower() == "production":
    default_origins = ["http://164.52.203.17:5173", "http://localhost:5173"]
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    allowed_origins.extend(default_origins)
else:
    # In development, allow all origins
    allowed_origins = ["*"]
    
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
    expose_headers=["Content-Length"],
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

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    # Configure host for VM deployment
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)