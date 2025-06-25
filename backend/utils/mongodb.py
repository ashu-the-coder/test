"""
MongoDB connection utility for the Xinete platform.
This module provides a consistent way to connect to MongoDB across all routes.
"""

import os
from pymongo import MongoClient
from urllib.parse import urlparse

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
        print(f"Error parsing MongoDB URI: {e}")
        return default_db

def get_mongo_connection():
    """
    Get a MongoDB connection with proper authentication.
    Returns a tuple of (client, db)
    """
    # Get MongoDB connection string from environment
    MONGODB_URL = os.getenv("MONGODB_URL", os.getenv("MONGO_URI", "mongodb://localhost:27017/xinete_storage"))
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "admin")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "@dminXinetee@123")
    MONGODB_DB = os.getenv("MONGODB_DB", os.getenv("MONGO_DB", "xinetee"))

    # Connect to MongoDB with authentication
    try:
        # Use the combined approach to ensure authentication works
        print(f"Connecting to MongoDB with authentication")
        
        # Direct connection with embedded auth is most reliable
        try:
            # First try using the connection string directly
            client = MongoClient(MONGODB_URL, connectTimeoutMS=5000, serverSelectionTimeoutMS=5000)
            # Quick test
            client.admin.command('ping')
            print("Connected to MongoDB using connection string")
        except Exception as e:
            print(f"Connection with string failed: {str(e)}, trying with explicit auth")
            
            try:
                # Try using explicit auth with MongoClient
                client = MongoClient(
                    host=f'mongodb://100.123.165.22:27017/',
                    username=MONGODB_USERNAME,
                    password=MONGODB_PASSWORD,
                    authSource='admin',  # Specify the authentication database
                    connectTimeoutMS=5000,
                    serverSelectionTimeoutMS=5000
                )
                # Quick test
                client.admin.command('ping')
                print("Connected to MongoDB using explicit auth")
            except Exception as auth_err:
                print(f"Explicit auth failed: {str(auth_err)}, falling back to basic connection")
                # Last resort - basic connection
                client = MongoClient("mongodb://100.123.165.22:27017/")

        # Get database reference - we now know it's "xinetee" explicitly
        db_name = "xinetee"  # Hard-coded based on your environment variables
        print(f"Using database: {db_name}")
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB")
        return client, db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise

def get_users_collection():
    """
    Get the users collection with the proper connection.
    """
    client, db = get_mongo_connection()
    users_collection_name = os.getenv("MONGO_USERS_COLLECTION", "users")
    return db[users_collection_name]
