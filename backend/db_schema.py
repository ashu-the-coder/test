"""
MongoDB Schema and Indexing Configuration for Xinete Enterprise

This file defines the schema structure and creates necessary indexes for the MongoDB collections
used in the Xinete Enterprise system. It includes:

1. Enterprises - Company information
2. Accounts - Enterprise user accounts
3. Products - Product catalog
4. Batches - Production batch information
5. Traceability - Supply chain events
6. Inventory - Current stock levels
7. Audit Logs - System activity logs

Each collection has its schema defined as a Python dictionary that can be used for validation.
"""

import pymongo
from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB connection with authentication support
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xinete_storage")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")

# If username and password are provided, use them in the connection
if MONGODB_USERNAME and MONGODB_PASSWORD:
    # Parse the connection string to add auth credentials
    if "://" in MONGODB_URL:
        protocol, rest = MONGODB_URL.split("://", 1)
        auth_url = f"{protocol}://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{rest}"
        client = MongoClient(auth_url)
        print(f"Connecting to MongoDB with authentication")
    else:
        client = MongoClient(MONGODB_URL)
        # Set authentication directly if needed
        db_name = MONGODB_URL.split("/")[-1] if "/" in MONGODB_URL else "xinete_storage"
        client[db_name].authenticate(MONGODB_USERNAME, MONGODB_PASSWORD)
        print(f"Using direct authentication with MongoDB")
else:
    client = MongoClient(MONGODB_URL)
    print(f"Connecting to MongoDB without authentication")
db = client.xinete_storage

# Schema Definitions
# These schemas follow MongoDB's schema validation format

# 1. Enterprises Collection
enterprises_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["enterprise_id", "name", "industry", "created_at"],
            "properties": {
                "enterprise_id": {
                    "bsonType": "string",
                    "description": "Unique identifier for the enterprise"
                },
                "name": {
                    "bsonType": "string",
                    "description": "Name of the enterprise"
                },
                "industry": {
                    "bsonType": "string",
                    "description": "Industry sector of the enterprise"
                },
                "contact": {
                    "bsonType": "object",
                    "properties": {
                        "email": {
                            "bsonType": "string",
                            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                        },
                        "phone": {
                            "bsonType": "string"
                        }
                    }
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "Date and time when the enterprise was created"
                }
            }
        }
    }
}

# 2. Accounts Collection (Enterprise Users)
accounts_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "enterprise_id", "name", "email", "role", "created_at"],
            "properties": {
                "user_id": {
                    "bsonType": "string",
                    "description": "Unique identifier for the user"
                },
                "enterprise_id": {
                    "bsonType": "string",
                    "description": "Enterprise ID the user belongs to"
                },
                "name": {
                    "bsonType": "string",
                    "description": "Full name of the user"
                },
                "email": {
                    "bsonType": "string",
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "description": "Email address of the user"
                },
                "role": {
                    "enum": ["admin", "supply_chain_head", "inventory_manager", "quality_control", "logistics"],
                    "description": "Role of the user within the enterprise"
                },
                "permissions": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "string"
                    },
                    "description": "List of permissions for the user"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "Date and time when the account was created"
                }
            }
        }
    }
}

# 3. Products Collection
products_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["product_id", "enterprise_id", "product_name", "product_type", "unit", "created_at"],
            "properties": {
                "product_id": {
                    "bsonType": "string",
                    "description": "Unique identifier for the product"
                },
                "enterprise_id": {
                    "bsonType": "string",
                    "description": "Enterprise ID the product belongs to"
                },
                "product_name": {
                    "bsonType": "string",
                    "description": "Name of the product"
                },
                "product_type": {
                    "bsonType": "string",
                    "description": "Type or category of the product"
                },
                "unit": {
                    "bsonType": "string",
                    "description": "Unit of measurement (e.g., liter, kg, piece)"
                },
                "custom_data": {
                    "bsonType": "object",
                    "description": "Additional custom product data"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "Date and time when the product was created"
                }
            }
        }
    }
}

# 4. Batches Collection
batches_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "batch_id", "product_id", "enterprise_id", "production_date",
                "initial_quantity", "ipfs_cid", "blockchain_tx_hash", "created_at"
            ],
            "properties": {
                "batch_id": {
                    "bsonType": "string",
                    "description": "Unique identifier for the batch"
                },
                "product_id": {
                    "bsonType": "string",
                    "description": "Product ID this batch belongs to"
                },
                "enterprise_id": {
                    "bsonType": "string",
                    "description": "Enterprise ID the batch belongs to"
                },
                "production_date": {
                    "bsonType": "date",
                    "description": "Date and time when the batch was produced"
                },
                "expiry_date": {
                    "bsonType": "date",
                    "description": "Date and time when the batch expires"
                },
                "initial_quantity": {
                    "bsonType": "number",
                    "description": "Initial quantity of product in this batch"
                },
                "current_quantity": {
                    "bsonType": "number",
                    "description": "Current quantity of product in this batch"
                },
                "ipfs_cid": {
                    "bsonType": "string",
                    "description": "IPFS Content ID for batch documentation"
                },
                "blockchain_tx_hash": {
                    "bsonType": "string",
                    "description": "Blockchain transaction hash for this batch"
                },
                "qr_code_url": {
                    "bsonType": "string",
                    "description": "URL to the QR code for this batch"
                },
                "status": {
                    "enum": ["produced", "in_storage", "shipped", "received", "sold", "expired", "recalled"],
                    "description": "Current status of the batch"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "Date and time when the batch record was created"
                }
            }
        }
    }
}

# 5. Traceability Collection
traceability_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "batch_id", "enterprise_id", "event_type", "timestamp",
                "location", "ipfs_cid", "blockchain_tx_hash", "created_by"
            ],
            "properties": {
                "batch_id": {
                    "bsonType": "string",
                    "description": "Batch ID this traceability event relates to"
                },
                "enterprise_id": {
                    "bsonType": "string",
                    "description": "Enterprise ID the traceability event belongs to"
                },
                "event_type": {
                    "enum": ["produced", "stored", "shipped", "received", "sold", "recalled", "inspected"],
                    "description": "Type of traceability event"
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "Date and time when the event occurred"
                },
                "location": {
                    "bsonType": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "description": "Name of the location"
                        },
                        "lat": {
                            "bsonType": "number",
                            "description": "Latitude coordinates"
                        },
                        "lng": {
                            "bsonType": "number",
                            "description": "Longitude coordinates"
                        }
                    }
                },
                "ipfs_cid": {
                    "bsonType": "string",
                    "description": "IPFS Content ID for event documentation"
                },
                "blockchain_tx_hash": {
                    "bsonType": "string",
                    "description": "Blockchain transaction hash for this event"
                },
                "remarks": {
                    "bsonType": "string",
                    "description": "Additional remarks or details about the event"
                },
                "created_by": {
                    "bsonType": "string",
                    "description": "User ID of the user who created this event"
                }
            }
        }
    }
}

# 6. Inventory Collection
inventory_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["enterprise_id", "product_id", "location", "quantity", "last_updated"],
            "properties": {
                "enterprise_id": {
                    "bsonType": "string",
                    "description": "Enterprise ID the inventory belongs to"
                },
                "product_id": {
                    "bsonType": "string",
                    "description": "Product ID this inventory item refers to"
                },
                "location": {
                    "bsonType": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "description": "Name of the location"
                        },
                        "lat": {
                            "bsonType": "number",
                            "description": "Latitude coordinates"
                        },
                        "lng": {
                            "bsonType": "number",
                            "description": "Longitude coordinates"
                        }
                    }
                },
                "quantity": {
                    "bsonType": "number",
                    "description": "Current quantity in inventory"
                },
                "last_updated": {
                    "bsonType": "date",
                    "description": "Date and time when the inventory was last updated"
                }
            }
        }
    }
}

# 7. Audit Logs Collection
audit_logs_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["entity_type", "entity_id", "field_changed", "old_value", "new_value", "changed_by", "timestamp"],
            "properties": {
                "entity_type": {
                    "enum": ["batch", "product", "inventory", "traceability", "enterprise"],
                    "description": "Type of entity the audit log relates to"
                },
                "entity_id": {
                    "bsonType": "string",
                    "description": "Identifier for the entity"
                },
                "field_changed": {
                    "bsonType": "string",
                    "description": "Name of the field that was changed"
                },
                "old_value": {
                    "description": "Previous value before the change"
                },
                "new_value": {
                    "description": "New value after the change"
                },
                "changed_by": {
                    "bsonType": "string",
                    "description": "User ID of the user who made the change"
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "Date and time when the change was made"
                }
            }
        }
    }
}

def create_or_update_collection(collection_name, schema):
    """Create a collection with schema validation or update existing collection"""
    try:
        # Check if collection exists
        if collection_name in db.list_collection_names():
            # Update validation schema for existing collection
            db.command({
                "collMod": collection_name,
                **schema
            })
            print(f"Updated validation schema for collection: {collection_name}")
        else:
            # Create new collection with validation schema
            db.create_collection(collection_name, **schema)
            print(f"Created collection with validation: {collection_name}")
    except Exception as e:
        print(f"Error handling collection {collection_name}: {str(e)}")

def create_indexes():
    """Create necessary indexes for collections"""
    try:
        # Enterprises indexes
        db.enterprises.create_index("enterprise_id", unique=True)
        
        # Accounts indexes
        db.accounts.create_index("email", unique=True)
        db.accounts.create_index("user_id", unique=True)
        db.accounts.create_index([("enterprise_id", pymongo.ASCENDING), ("role", pymongo.ASCENDING)])
        
        # Products indexes
        db.products.create_index([("enterprise_id", pymongo.ASCENDING), ("product_id", pymongo.ASCENDING)], unique=True)
        db.products.create_index("product_name")
        
        # Batches indexes
        db.batches.create_index([("enterprise_id", pymongo.ASCENDING), ("batch_id", pymongo.ASCENDING)], unique=True)
        db.batches.create_index([("product_id", pymongo.ASCENDING), ("production_date", pymongo.DESCENDING)])
        db.batches.create_index("ipfs_cid")
        db.batches.create_index("blockchain_tx_hash")
        
        # Traceability indexes
        db.traceability.create_index([("batch_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])
        db.traceability.create_index("enterprise_id")
        db.traceability.create_index("event_type")
        db.traceability.create_index("ipfs_cid")
        db.traceability.create_index("blockchain_tx_hash")
        
        # Inventory indexes
        db.inventory.create_index([("product_id", pymongo.ASCENDING), ("location.name", pymongo.ASCENDING)], unique=True)
        db.inventory.create_index("enterprise_id")
        
        # Audit logs indexes
        db.audit_logs.create_index([("entity_type", pymongo.ASCENDING), ("entity_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])
        db.audit_logs.create_index("changed_by")
        
        print("Created all required indexes")
    except Exception as e:
        print(f"Error creating indexes: {str(e)}")

def setup_database():
    """Setup the entire database schema and indexes"""
    # Create or update collections with validation
    create_or_update_collection("enterprises", enterprises_schema)
    create_or_update_collection("accounts", accounts_schema)
    create_or_update_collection("products", products_schema)
    create_or_update_collection("batches", batches_schema)
    create_or_update_collection("traceability", traceability_schema)
    create_or_update_collection("inventory", inventory_schema)
    create_or_update_collection("audit_logs", audit_logs_schema)
    
    # Create indexes
    create_indexes()
    
    print("Database setup complete")

def insert_sample_data():
    """Insert sample data for testing (optional)"""
    # Sample enterprise
    enterprise = {
        "enterprise_id": "amol_milk_dairy",
        "name": "Amol Milk Dairy",
        "industry": "Dairy",
        "contact": {
            "email": "info@amoldairy.com",
            "phone": "1234567890"
        },
        "created_at": datetime.now()
    }
    
    # Insert or update enterprise
    db.enterprises.update_one(
        {"enterprise_id": enterprise["enterprise_id"]},
        {"$set": enterprise},
        upsert=True
    )
    
    # Sample account
    account = {
        "user_id": "emp_amol_001",
        "enterprise_id": "amol_milk_dairy",
        "name": "Ravi Deshmukh",
        "email": "ravi@amoldairy.com",
        "role": "inventory_manager",
        "permissions": ["create_batch", "update_inventory"],
        "created_at": datetime.now()
    }
    
    # Insert or update account
    db.accounts.update_one(
        {"user_id": account["user_id"]},
        {"$set": account},
        upsert=True
    )
    
    # Sample product
    product = {
        "product_id": "milk_1l",
        "enterprise_id": "amol_milk_dairy",
        "product_name": "1L Milk Packet",
        "product_type": "liquid",
        "unit": "liter",
        "custom_data": {
            "fat_percentage": 3.5,
            "is_organic": True
        },
        "created_at": datetime.now()
    }
    
    # Insert or update product
    db.products.update_one(
        {"product_id": product["product_id"], "enterprise_id": product["enterprise_id"]},
        {"$set": product},
        upsert=True
    )
    
    print("Sample data inserted")

if __name__ == "__main__":
    # Set up the database
    setup_database()
    
    # Optionally insert sample data
    # Uncomment the line below to insert sample data
    # insert_sample_data()
