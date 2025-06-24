"""
Initialize MongoDB with sample data for the Xinete Enterprise System.

This script creates sample data for all collections to help with testing
and development of the Xinete Enterprise System.
"""

from db_schema import db, setup_database
from datetime import datetime, timedelta
import uuid
import random

def create_sample_data():
    """Create sample data for all collections"""
    # Clear existing data (optional)
    # Uncomment these lines if you want to clear existing data
    # db.enterprises.delete_many({})
    # db.accounts.delete_many({})
    # db.products.delete_many({})
    # db.batches.delete_many({})
    # db.traceability.delete_many({})
    # db.inventory.delete_many({})
    # db.audit_logs.delete_many({})
    
    # Create enterprises
    enterprises = [
        {
            "enterprise_id": "amol_milk_dairy",
            "name": "Amol Milk Dairy",
            "industry": "Dairy",
            "contact": {
                "email": "info@amoldairy.com",
                "phone": "1234567890"
            },
            "created_at": datetime.now()
        },
        {
            "enterprise_id": "greenleaf_farms",
            "name": "Green Leaf Organic Farms",
            "industry": "Agriculture",
            "contact": {
                "email": "contact@greenleaf.com",
                "phone": "9876543210"
            },
            "created_at": datetime.now()
        }
    ]
    
    for enterprise in enterprises:
        db.enterprises.update_one(
            {"enterprise_id": enterprise["enterprise_id"]},
            {"$set": enterprise},
            upsert=True
        )
    
    # Create accounts
    accounts = [
        {
            "user_id": "emp_amol_001",
            "enterprise_id": "amol_milk_dairy",
            "name": "Ravi Deshmukh",
            "email": "ravi@amoldairy.com",
            "role": "admin",
            "permissions": ["create_batch", "update_inventory", "manage_users"],
            "created_at": datetime.now() - timedelta(days=30)
        },
        {
            "user_id": "emp_amol_002",
            "enterprise_id": "amol_milk_dairy",
            "name": "Priya Sharma",
            "email": "priya@amoldairy.com",
            "role": "inventory_manager",
            "permissions": ["update_inventory"],
            "created_at": datetime.now() - timedelta(days=15)
        },
        {
            "user_id": "emp_amol_003",
            "enterprise_id": "amol_milk_dairy",
            "name": "Sunil Patil",
            "email": "sunil@amoldairy.com",
            "role": "supply_chain_head",
            "permissions": ["create_batch", "update_inventory", "create_trace_event"],
            "created_at": datetime.now() - timedelta(days=20)
        },
        {
            "user_id": "emp_green_001",
            "enterprise_id": "greenleaf_farms",
            "name": "Anjali Mehta",
            "email": "anjali@greenleaf.com",
            "role": "admin",
            "permissions": ["create_batch", "update_inventory", "manage_users"],
            "created_at": datetime.now() - timedelta(days=25)
        }
    ]
    
    for account in accounts:
        db.accounts.update_one(
            {"user_id": account["user_id"]},
            {"$set": account},
            upsert=True
        )
    
    # Create products
    products = [
        {
            "product_id": "milk_1l",
            "enterprise_id": "amol_milk_dairy",
            "product_name": "1L Milk Packet",
            "product_type": "liquid",
            "unit": "liter",
            "custom_data": {
                "fat_percentage": 3.5,
                "is_organic": True
            },
            "created_at": datetime.now() - timedelta(days=60)
        },
        {
            "product_id": "curd_500g",
            "enterprise_id": "amol_milk_dairy",
            "product_name": "500g Curd Cup",
            "product_type": "dairy",
            "unit": "gram",
            "custom_data": {
                "fat_percentage": 4.0,
                "is_organic": True,
                "culture_type": "probiotic"
            },
            "created_at": datetime.now() - timedelta(days=45)
        },
        {
            "product_id": "spinach_bunch",
            "enterprise_id": "greenleaf_farms",
            "product_name": "Organic Spinach Bunch",
            "product_type": "vegetable",
            "unit": "bunch",
            "custom_data": {
                "is_organic": True,
                "cultivation_method": "hydroponic"
            },
            "created_at": datetime.now() - timedelta(days=30)
        }
    ]
    
    for product in products:
        db.products.update_one(
            {"product_id": product["product_id"], "enterprise_id": product["enterprise_id"]},
            {"$set": product},
            upsert=True
        )
    
    # Create batches with IPFS and blockchain data
    batches = [
        {
            "batch_id": "BATCH20250625_001",
            "product_id": "milk_1l",
            "enterprise_id": "amol_milk_dairy",
            "production_date": datetime.now() - timedelta(days=2),
            "expiry_date": datetime.now() + timedelta(days=5),
            "initial_quantity": 1000,
            "current_quantity": 950,
            "ipfs_cid": "QmXYZ123abcdefghijklmnopqrstuvwxyz123456789ABCDEFGH",
            "blockchain_tx_hash": "0xabc123def456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "qr_code_url": "https://ipfs.io/ipfs/QmXYZ123abcdefghijklmnopqrstuvwxyz123456789ABCDEFGH",
            "status": "in_storage",
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "batch_id": "BATCH20250624_002",
            "product_id": "curd_500g",
            "enterprise_id": "amol_milk_dairy",
            "production_date": datetime.now() - timedelta(days=3),
            "expiry_date": datetime.now() + timedelta(days=10),
            "initial_quantity": 500,
            "current_quantity": 500,
            "ipfs_cid": "QmABC456defghijklmnopqrstuvwxyz123456789ABCDEFGHJKL",
            "blockchain_tx_hash": "0xdef456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "qr_code_url": "https://ipfs.io/ipfs/QmABC456defghijklmnopqrstuvwxyz123456789ABCDEFGHJKL",
            "status": "produced",
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "batch_id": "BATCH20250623_001",
            "product_id": "spinach_bunch",
            "enterprise_id": "greenleaf_farms",
            "production_date": datetime.now() - timedelta(days=4),
            "expiry_date": datetime.now() + timedelta(days=3),
            "initial_quantity": 200,
            "current_quantity": 150,
            "ipfs_cid": "QmDEF789abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHI",
            "blockchain_tx_hash": "0x789abcdef0123456789abcdef0123456789abcdef0123456789abcdefabcdef",
            "qr_code_url": "https://ipfs.io/ipfs/QmDEF789abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHI",
            "status": "shipped",
            "created_at": datetime.now() - timedelta(days=4)
        }
    ]
    
    for batch in batches:
        db.batches.update_one(
            {"batch_id": batch["batch_id"]},
            {"$set": batch},
            upsert=True
        )
    
    # Create traceability events
    traceability_events = [
        {
            "batch_id": "BATCH20250625_001",
            "enterprise_id": "amol_milk_dairy",
            "event_type": "produced",
            "timestamp": datetime.now() - timedelta(days=2, hours=2),
            "location": {
                "name": "Amol Dairy Factory",
                "lat": 18.52,
                "lng": 73.85
            },
            "ipfs_cid": "QmTraceDoc123abcdefghijklmnopqrstuvwxyz123456789ABC",
            "blockchain_tx_hash": "0x123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "remarks": "Production completed and quality checks passed",
            "created_by": "emp_amol_001"
        },
        {
            "batch_id": "BATCH20250625_001",
            "enterprise_id": "amol_milk_dairy",
            "event_type": "stored",
            "timestamp": datetime.now() - timedelta(days=2, hours=1),
            "location": {
                "name": "Warehouse WH001",
                "lat": 18.50,
                "lng": 73.80
            },
            "ipfs_cid": "QmTraceDoc456defghijklmnopqrstuvwxyz123456789ABCDEF",
            "blockchain_tx_hash": "0x234567890abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "remarks": "Transferred to cold storage facility",
            "created_by": "emp_amol_002"
        },
        {
            "batch_id": "BATCH20250623_001",
            "enterprise_id": "greenleaf_farms",
            "event_type": "produced",
            "timestamp": datetime.now() - timedelta(days=4, hours=3),
            "location": {
                "name": "Green Leaf Farm Field A",
                "lat": 18.60,
                "lng": 73.90
            },
            "ipfs_cid": "QmTraceDoc789ghijklmnopqrstuvwxyz123456789ABCDEFGHI",
            "blockchain_tx_hash": "0x345678901abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "remarks": "Harvested and packaged",
            "created_by": "emp_green_001"
        },
        {
            "batch_id": "BATCH20250623_001",
            "enterprise_id": "greenleaf_farms",
            "event_type": "shipped",
            "timestamp": datetime.now() - timedelta(days=3, hours=2),
            "location": {
                "name": "Green Leaf Distribution Center",
                "lat": 18.58,
                "lng": 73.88
            },
            "ipfs_cid": "QmTraceDocABCijklmnopqrstuvwxyz123456789ABCDEFGHIJK",
            "blockchain_tx_hash": "0x456789012abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "remarks": "Shipped to retail distributor",
            "created_by": "emp_green_001"
        }
    ]
    
    for event in traceability_events:
        # Generate a unique ID for each traceability event
        event_id = f"trace_{uuid.uuid4().hex[:8]}"
        db.traceability.insert_one({**event, "id": event_id})
    
    # Create inventory records
    inventory_records = [
        {
            "enterprise_id": "amol_milk_dairy",
            "product_id": "milk_1l",
            "location": {
                "name": "Warehouse WH001",
                "lat": 18.50,
                "lng": 73.80
            },
            "quantity": 950,
            "last_updated": datetime.now() - timedelta(hours=12)
        },
        {
            "enterprise_id": "amol_milk_dairy",
            "product_id": "curd_500g",
            "location": {
                "name": "Warehouse WH001",
                "lat": 18.50,
                "lng": 73.80
            },
            "quantity": 500,
            "last_updated": datetime.now() - timedelta(hours=24)
        },
        {
            "enterprise_id": "greenleaf_farms",
            "product_id": "spinach_bunch",
            "location": {
                "name": "Distribution Center DC001",
                "lat": 18.58,
                "lng": 73.88
            },
            "quantity": 150,
            "last_updated": datetime.now() - timedelta(hours=36)
        }
    ]
    
    for inventory in inventory_records:
        # Create a compound key for inventory
        inventory_id = f"{inventory['product_id']}@{inventory['location']['name']}"
        db.inventory.update_one(
            {"product_id": inventory["product_id"], "location.name": inventory["location"]["name"]},
            {"$set": {**inventory, "id": inventory_id}},
            upsert=True
        )
    
    # Create audit logs
    audit_logs = [
        {
            "entity_type": "inventory",
            "entity_id": "milk_1l@Warehouse WH001",
            "field_changed": "quantity",
            "old_value": 1000,
            "new_value": 950,
            "changed_by": "emp_amol_002",
            "timestamp": datetime.now() - timedelta(hours=12)
        },
        {
            "entity_type": "batch",
            "entity_id": "BATCH20250625_001",
            "field_changed": "status",
            "old_value": "produced",
            "new_value": "in_storage",
            "changed_by": "emp_amol_001",
            "timestamp": datetime.now() - timedelta(days=2, hours=1)
        },
        {
            "entity_type": "batch",
            "entity_id": "BATCH20250623_001",
            "field_changed": "status",
            "old_value": "produced",
            "new_value": "shipped",
            "changed_by": "emp_green_001",
            "timestamp": datetime.now() - timedelta(days=3, hours=2)
        },
        {
            "entity_type": "inventory",
            "entity_id": "spinach_bunch@Distribution Center DC001",
            "field_changed": "quantity",
            "old_value": 200,
            "new_value": 150,
            "changed_by": "emp_green_001",
            "timestamp": datetime.now() - timedelta(hours=36)
        }
    ]
    
    for log in audit_logs:
        db.audit_logs.insert_one(log)
    
    print("Sample data created successfully!")

if __name__ == "__main__":
    # Set up database schema and indexes first
    setup_database()
    
    # Create sample data
    create_sample_data()
    
    print("Database initialization complete with sample data.")
