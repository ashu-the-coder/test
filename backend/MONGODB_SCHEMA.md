# MongoDB Schema for Xinete Enterprise System

This directory contains the MongoDB schema definition for the Xinete Enterprise System, which provides data storage for supply chain traceability, batch management, and inventory tracking.

## Schema Structure

The database consists of the following collections:

1. **enterprises** - Company information
2. **accounts** - Enterprise user accounts
3. **products** - Product catalog
4. **batches** - Production batch information with IPFS/blockchain integration
5. **traceability** - Supply chain events with IPFS/blockchain integration
6. **inventory** - Current stock levels
7. **audit_logs** - System activity logs

## Database Setup

To initialize the database with the defined schema and indexes:

```bash
python db_schema.py
```

This script will:
- Create collections with schema validation
- Set up appropriate indexes for performance optimization
- Optionally insert sample data (commented out by default)

## Collection Details

### 1. Enterprises Collection

```json
{
  "_id": ObjectId("..."),
  "enterprise_id": "amol_milk_dairy",
  "name": "Amol Milk Dairy",
  "industry": "Dairy",
  "contact": {
    "email": "info@amoldairy.com",
    "phone": "1234567890"
  },
  "created_at": ISODate("2025-06-25T10:00:00Z")
}
```

### 2. Accounts Collection (Enterprise Users)

```json
{
  "_id": ObjectId("..."),
  "user_id": "emp_amol_001",
  "enterprise_id": "amol_milk_dairy",
  "name": "Ravi Deshmukh",
  "email": "ravi@amoldairy.com",
  "role": "inventory_manager", // supply_chain_head, admin, etc.
  "permissions": ["create_batch", "update_inventory"],
  "created_at": ISODate("2025-06-25T07:00:00Z")
}
```

### 3. Products Collection

```json
{
  "_id": ObjectId("..."),
  "product_id": "milk_1l",
  "enterprise_id": "amol_milk_dairy",
  "product_name": "1L Milk Packet",
  "product_type": "liquid",
  "unit": "liter",
  "custom_data": {
    "fat_percentage": 3.5,
    "is_organic": true
  },
  "created_at": ISODate("2025-06-25T10:15:00Z")
}
```

### 4. Batches Collection

```json
{
  "_id": ObjectId("..."),
  "batch_id": "BATCH20250625_001",
  "product_id": "milk_1l",
  "enterprise_id": "amol_milk_dairy",
  "production_date": ISODate("2025-06-25T08:00:00Z"),
  "expiry_date": ISODate("2025-06-30T08:00:00Z"),
  "initial_quantity": 1000,
  "current_quantity": 1000, 
  "ipfs_cid": "QmXYZ123...",
  "blockchain_tx_hash": "0xabc123...",
  "qr_code_url": "https://ipfs.io/ipfs/QmXYZ123...",
  "status": "produced",
  "created_at": ISODate("2025-06-25T08:05:00Z")
}
```

### 5. Traceability Collection

```json
{
  "_id": ObjectId("..."),
  "batch_id": "BATCH20250625_001",
  "enterprise_id": "amol_milk_dairy",
  "event_type": "shipped",
  "timestamp": ISODate("2025-06-25T09:00:00Z"),
  "location": {
    "name": "Factory A",
    "lat": 18.52,
    "lng": 73.85
  },
  "ipfs_cid": "QmTraceDoc123...",
  "blockchain_tx_hash": "0xdef456...",
  "remarks": "Loaded to transport vehicle",
  "created_by": "emp_amol_001"
}
```

### 6. Inventory Collection

```json
{
  "_id": ObjectId("..."),
  "enterprise_id": "amol_milk_dairy",
  "product_id": "milk_1l",
  "location": {
    "name": "Warehouse WH001",
    "lat": 18.50,
    "lng": 73.80
  },
  "quantity": 850,
  "last_updated": ISODate("2025-06-25T12:00:00Z")
}
```

### 7. Audit Logs Collection

```json
{
  "_id": ObjectId("..."),
  "entity_type": "inventory",
  "entity_id": "milk_1l@WH001",
  "field_changed": "quantity",
  "old_value": 900,
  "new_value": 850,
  "changed_by": "emp_amol_001",
  "timestamp": ISODate("2025-06-25T12:00:00Z")
}
```

## Indexing Strategy

The following indexes are automatically created for optimized querying:

```javascript
db.enterprises.createIndex("enterprise_id", { unique: true });

db.accounts.createIndex("email", { unique: true });
db.accounts.createIndex("user_id", { unique: true });
db.accounts.createIndex([("enterprise_id", 1), ("role", 1)]);

db.products.createIndex([("enterprise_id", 1), ("product_id", 1)], { unique: true });
db.products.createIndex("product_name");

db.batches.createIndex([("enterprise_id", 1), ("batch_id", 1)], { unique: true });
db.batches.createIndex([("product_id", 1), ("production_date", -1)]);
db.batches.createIndex("ipfs_cid");
db.batches.createIndex("blockchain_tx_hash");

db.traceability.createIndex([("batch_id", 1), ("timestamp", -1)]);
db.traceability.createIndex("enterprise_id");
db.traceability.createIndex("event_type");
db.traceability.createIndex("ipfs_cid");
db.traceability.createIndex("blockchain_tx_hash");

db.inventory.createIndex([("product_id", 1), ("location.name", 1)], { unique: true });
db.inventory.createIndex("enterprise_id");

db.audit_logs.createIndex([("entity_type", 1), ("entity_id", 1), ("timestamp", -1)]);
db.audit_logs.createIndex("changed_by");
```

## Environment Configuration

The MongoDB connection string can be configured using the `MONGODB_URL` environment variable. If not provided, the default connection string `mongodb://localhost:27017/xinete_storage` will be used.
