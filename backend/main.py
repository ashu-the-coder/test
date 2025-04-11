from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="Xinete Storage Platform")

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
print(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def read_root():
    return {"status": "healthy", "service": "Xinete Storage Platform"}

# Import routes after app initialization to avoid circular imports
from routes import auth, storage, download, verification

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(storage.router, prefix="/storage", tags=["storage"])
app.include_router(download.router, prefix="/api", tags=["download"])
app.include_router(verification.router, prefix="/api/verification", tags=["verification"])

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    # Configure host for VM deployment
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=False)