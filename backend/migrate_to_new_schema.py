"""
Data Migration Script for MongoDB Schema Update

This script migrates data from the old schema to the new enterprise schema.
Run this script if you have existing data that needs to be converted to the new format.
"""

from datetime import datetime
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import uuid
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

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
        print(f"Error parsing MongoDB URI: {e}")
        return default_db

# MongoDB connection with authentication support
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/xinete_storage")
MONGODB_URL = os.getenv("MONGODB_URL", MONGO_URI)  # Fallback to MONGO_URI if MONGODB_URL not set
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_DB = os.getenv("MONGODB_DB", "")  # Allow explicit database name override

# Connect to MongoDB
try:
    # If the connection string already includes auth, use it directly
    if "@" in MONGODB_URL:
        print(f"Using MongoDB connection string with embedded authentication")
        client = MongoClient(MONGODB_URL)
    # If separate username and password provided, use them
    elif MONGODB_USERNAME and MONGODB_PASSWORD:
        # Parse the connection string to add auth credentials
        if "://" in MONGODB_URL:
            protocol, rest = MONGODB_URL.split("://", 1)
            auth_url = f"{protocol}://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{rest}"
            print(f"Connecting to MongoDB with authentication")
            client = MongoClient(auth_url)
        else:
            client = MongoClient(MONGODB_URL)
            # Get database name properly
            db_name = extract_db_name_from_uri(MONGODB_URL)
            print(f"Using direct authentication with MongoDB")
            client[db_name].authenticate(MONGODB_USERNAME, MONGODB_PASSWORD)
    else:
        print(f"Connecting to MongoDB without authentication")
        client = MongoClient(MONGODB_URL)
        
    # Test connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Get database reference - prioritize explicit DB name if provided
db_name = MONGODB_DB if MONGODB_DB else extract_db_name_from_uri(MONGODB_URL)
print(f"Using database: {db_name}")
db = client[db_name]

def migrate_users_to_accounts():
    """
    Migrate users to the new accounts collection, preserving enterprises.
    """
    print("Migrating users to accounts...")
    
    # Get all users
    users = list(db.users.find({}))
    
    for user in users:
        # Check if the user is associated with an enterprise
        enterprise_id = user.get("enterprise_id")
        
        if enterprise_id:
            # Create account record
            account = {
                "user_id": user.get("user_id", f"user_{uuid.uuid4().hex[:8]}"),
                "enterprise_id": enterprise_id,
                "name": user.get("name", user.get("username", "")),
                "email": user.get("email", ""),
                "role": user.get("role", "individual"),
                "permissions": get_permissions_for_role(user.get("role", "individual")),
                "created_at": user.get("created_at", datetime.now())
            }
            
            # Insert or update account
            db.accounts.update_one(
                {"user_id": account["user_id"]},
                {"$set": account},
                upsert=True
            )
            
            print(f"Migrated user {account['name']} to account with role {account['role']}")

def migrate_enterprises():
    """
    Ensure all enterprises have the required fields in the new schema.
    """
    print("Migrating enterprises...")
    
    # Get all enterprises
    enterprises = list(db.enterprises.find({}))
    
    for enterprise in enterprises:
        # Update enterprise with new schema
        updated_enterprise = {
            "enterprise_id": enterprise.get("enterprise_id", enterprise.get("id", f"enterprise_{uuid.uuid4().hex[:8]}")),
            "name": enterprise.get("name", ""),
            "industry": enterprise.get("industry", "Other"),
            "contact": {
                "email": enterprise.get("email", ""),
                "phone": enterprise.get("phone", "")
            },
            "created_at": enterprise.get("created_at", datetime.now())
        }
        
        # Insert or update enterprise
        db.enterprises.update_one(
            {"enterprise_id": updated_enterprise["enterprise_id"]},
            {"$set": updated_enterprise},
            upsert=True
        )
        
        print(f"Migrated enterprise {updated_enterprise['name']}")

def migrate_products():
    """
    Migrate products to the new schema.
    """
    print("Migrating products...")
    
    # Get all products
    products = list(db.products.find({}))
    
    for product in products:
        # Update product with new schema
        updated_product = {
            "product_id": product.get("product_id", product.get("id", f"product_{uuid.uuid4().hex[:8]}")),
            "enterprise_id": product.get("enterprise_id", ""),
            "product_name": product.get("product_name", product.get("name", "")),
            "product_type": product.get("product_type", product.get("type", "other")),
            "unit": product.get("unit", "piece"),
            "custom_data": product.get("custom_data", {}),
            "created_at": product.get("created_at", datetime.now())
        }
        
        # Insert or update product
        db.products.update_one(
            {"product_id": updated_product["product_id"], "enterprise_id": updated_product["enterprise_id"]},
            {"$set": updated_product},
            upsert=True
        )
        
        print(f"Migrated product {updated_product['product_name']}")

def migrate_batches():
    """
    Migrate batches to the new schema with IPFS and blockchain fields.
    """
    print("Migrating batches...")
    
    # Get all batches
    batches = list(db.batches.find({}))
    
    for batch in batches:
        # Generate new QR code URL with IPFS if not using one already
        qr_code_url = batch.get("qr_code_url", "")
        ipfs_cid = batch.get("ipfs_cid", f"QmPlaceholder{uuid.uuid4().hex[:36]}")
        
        if qr_code_url and not qr_code_url.startswith("https://ipfs.io/ipfs/"):
            qr_code_url = f"https://ipfs.io/ipfs/{ipfs_cid}"
        
        # Update batch with new schema
        updated_batch = {
            "batch_id": batch.get("batch_id", batch.get("id", f"BATCH{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:4]}")),
            "product_id": batch.get("product_id", ""),
            "enterprise_id": batch.get("enterprise_id", ""),
            "production_date": batch.get("production_date", datetime.now()),
            "expiry_date": batch.get("expiry_date"),
            "initial_quantity": batch.get("initial_quantity", 0),
            "current_quantity": batch.get("current_quantity", batch.get("initial_quantity", 0)),
            "ipfs_cid": ipfs_cid,
            "blockchain_tx_hash": batch.get("blockchain_tx_hash", f"0x{uuid.uuid4().hex}"),
            "qr_code_url": qr_code_url,
            "status": batch.get("status", "produced"),
            "created_at": batch.get("created_at", batch.get("creation_date", datetime.now()))
        }
        
        # Insert or update batch
        db.batches.update_one(
            {"batch_id": updated_batch["batch_id"]},
            {"$set": updated_batch},
            upsert=True
        )
        
        print(f"Migrated batch {updated_batch['batch_id']}")

def migrate_traceability():
    """
    Migrate traceability events to the new schema.
    """
    print("Migrating traceability events...")
    
    # Get all traceability events
    events = list(db.traceability.find({}))
    
    for event in events:
        # Update event with new schema
        updated_event = {
            "id": event.get("id", f"trace_{uuid.uuid4().hex[:8]}"),
            "batch_id": event.get("batch_id", ""),
            "enterprise_id": event.get("enterprise_id", ""),
            "event_type": event.get("event_type", ""),
            "timestamp": event.get("timestamp", datetime.now()),
            "location": {
                "name": event.get("location_name", ""),
                "lat": event.get("lat", 0),
                "lng": event.get("lng", 0)
            } if event.get("location_name") else event.get("location", {"name": "Unknown", "lat": 0, "lng": 0}),
            "ipfs_cid": event.get("ipfs_cid", f"QmTrace{uuid.uuid4().hex[:36]}"),
            "blockchain_tx_hash": event.get("blockchain_tx_hash", f"0x{uuid.uuid4().hex}"),
            "remarks": event.get("remarks", ""),
            "created_by": event.get("created_by", "")
        }
        
        # Insert or update event
        db.traceability.update_one(
            {"id": updated_event["id"]},
            {"$set": updated_event},
            upsert=True
        )
        
        print(f"Migrated traceability event for batch {updated_event['batch_id']}")

def get_permissions_for_role(role):
    """
    Get default permissions for a given role.
    """
    permissions = []
    
    if role == "admin":
        permissions = ["create_batch", "update_inventory", "manage_users", "create_trace_event", "delete_batch", "create_product"]
    elif role == "supply_chain_head":
        permissions = ["create_batch", "update_inventory", "create_trace_event", "create_product"]
    elif role == "inventory_manager":
        permissions = ["update_inventory"]
    elif role == "quality_control":
        permissions = ["create_trace_event"]
    
    return permissions

def run_migration():
    """
    Run the complete migration process.
    """
    try:
        print("Starting migration process...")
        
        # Migrate enterprises first
        migrate_enterprises()
        
        # Migrate users to accounts
        migrate_users_to_accounts()
        
        # Migrate products
        migrate_products()
        
        # Migrate batches
        migrate_batches()
        
        # Migrate traceability events
        migrate_traceability()
        
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {str(e)}")

if __name__ == "__main__":
    # Run migration
    run_migration()
