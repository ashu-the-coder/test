"""
Create test users in MongoDB for both B2C individual users and enterprise users.
This script helps set up the initial test data for the application.
"""

import os
from datetime import datetime
import uuid
from pymongo import MongoClient
from utils.mongodb import get_mongo_connection

def create_test_users():
    print("Creating test users in MongoDB...")
    
    try:
        # Get MongoDB connection
        client, db = get_mongo_connection()
        
        # Create B2C individual users
        users_collection = db['users']
        
        # Test user 1: ashutosh
        if not users_collection.find_one({"username": "ashutosh"}):
            users_collection.insert_one({
                "username": "ashutosh",
                "password": "Anand@123",
                "wallet_address": None,
                "files": [],
                "user_type": "individual",
                "created_at": datetime.now()
            })
            print("Created B2C test user: ashutosh")
            
        # Test user 2: tanmay
        if not users_collection.find_one({"username": "tanmay"}):
            users_collection.insert_one({
                "username": "tanmay",
                "password": "Tanmay@123",
                "wallet_address": "0xb17E8DCeA7B18B0bbA91Cd33540B38Aff8217dd7",
                "files": [],
                "user_type": "individual",
                "created_at": datetime.now()
            })
            print("Created B2C test user: tanmay")
            
        # Create enterprise test data
        enterprises_collection = db['enterprises']
        accounts_collection = db['accounts']
        
        # Enterprise 1: Acme Corp
        enterprise_id = "acme_corp"
        if not enterprises_collection.find_one({"enterprise_id": enterprise_id}):
            enterprises_collection.insert_one({
                "enterprise_id": enterprise_id,
                "name": "Acme Corporation",
                "industry": "Manufacturing",
                "contact": {
                    "email": "contact@acmecorp.com",
                    "phone": "123-456-7890"
                },
                "created_at": datetime.now()
            })
            print(f"Created test enterprise: {enterprise_id}")
            
            # Create enterprise admin account
            if not accounts_collection.find_one({"user_id": f"{enterprise_id}_admin"}):
                accounts_collection.insert_one({
                    "user_id": f"{enterprise_id}_admin",
                    "enterprise_id": enterprise_id,
                    "name": "John Doe",
                    "email": "admin@acmecorp.com",
                    "password": "Admin123",  # Store password here for enterprise accounts
                    "role": "admin",
                    "permissions": ["create_batch", "update_inventory", "manage_users", "create_trace_event", "delete_batch", "create_product"],
                    "created_at": datetime.now()
                })
                print(f"Created admin account for enterprise: {enterprise_id}")
            
            # Create enterprise user with username/password for testing the login
            if not accounts_collection.find_one({"username": "acmeuser"}):
                accounts_collection.insert_one({
                    "username": "acmeuser",
                    "password": "Acme@123",
                    "user_id": str(uuid.uuid4()),
                    "enterprise_id": enterprise_id,
                    "name": "Acme Test User",
                    "email": "test@acmecorp.com",
                    "role": "user",
                    "permissions": ["view_inventory", "view_batch", "view_trace"],
                    "created_at": datetime.now()
                })
                print(f"Created test user account for enterprise: {enterprise_id}")
            
        # Enterprise 2: XYZ Ltd
        enterprise_id = "xyz_ltd"
        if not enterprises_collection.find_one({"enterprise_id": enterprise_id}):
            enterprises_collection.insert_one({
                "enterprise_id": enterprise_id,
                "name": "XYZ Limited",
                "industry": "Technology",
                "contact": {
                    "email": "info@xyzltd.com",
                    "phone": "987-654-3210"
                },
                "created_at": datetime.now()
            })
            print(f"Created test enterprise: {enterprise_id}")
            
            # Create enterprise admin account
            if not accounts_collection.find_one({"user_id": f"{enterprise_id}_admin"}):
                accounts_collection.insert_one({
                    "user_id": f"{enterprise_id}_admin", 
                    "enterprise_id": enterprise_id,
                    "name": "Jane Smith",
                    "email": "admin@xyzltd.com",
                    "password": "Admin456",  # Store password here for enterprise accounts
                    "role": "admin",
                    "permissions": ["create_batch", "update_inventory", "manage_users", "create_trace_event", "delete_batch", "create_product"],
                    "created_at": datetime.now()
                })
                print(f"Created admin account for enterprise: {enterprise_id}")
        
        print("Test users and enterprises created successfully!")
        
    except Exception as e:
        print(f"Error creating test users: {str(e)}")

if __name__ == "__main__":
    create_test_users()
