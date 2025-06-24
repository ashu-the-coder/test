from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import pymongo
from pymongo import MongoClient

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

# Setup MongoDB connection with authentication support
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/xinete_storage")
MONGODB_URL = os.getenv("MONGODB_URL", MONGO_URI)  # Fallback to MONGO_URI if MONGODB_URL not set
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")

# Connect to MongoDB
try:
    # If the connection string already includes auth, use it directly
    if "@" in MONGODB_URL:
        logger.info(f"Using MongoDB connection string with embedded authentication")
        client = MongoClient(MONGODB_URL)
    # If separate username and password provided, use them
    elif MONGODB_USERNAME and MONGODB_PASSWORD:
        # Parse the connection string to add auth credentials
        if "://" in MONGODB_URL:
            protocol, rest = MONGODB_URL.split("://", 1)
            auth_url = f"{protocol}://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{rest}"
            logger.info(f"Connecting to MongoDB with authentication")
            client = MongoClient(auth_url)
        else:
            client = MongoClient(MONGODB_URL)
            # Set authentication directly if needed
            db_name = MONGODB_URL.split("/")[-1] if "/" in MONGODB_URL else "xinete_storage"
            logger.info(f"Using direct authentication with MongoDB")
            client[db_name].authenticate(MONGODB_USERNAME, MONGODB_PASSWORD)
    else:
        logger.info(f"Connecting to MongoDB without authentication")
        client = MongoClient(MONGODB_URL)
        
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Get database reference
db_name = MONGODB_URL.split("/")[-1] if "/" in MONGODB_URL else "xinete_storage"
db = client[db_name]

# Configure CORS
default_origins = ["http://164.52.203.17:5173", "http://localhost:5173"]
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
allowed_origins.extend(default_origins)
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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