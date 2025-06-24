# Xinete Enterprise Supply Chain Platform

A comprehensive enterprise supply chain management platform that leverages blockchain and IPFS technologies to provide traceability, inventory management, batch tracking, and auditing capabilities for businesses.

## Project Overview

Xinete Enterprise is an advanced supply chain solution that combines:
- Blockchain technology for immutable data records and verification
- IPFS (InterPlanetary File System) for decentralized document storage
- MongoDB for efficient enterprise data management
- Role-based access control (RBAC) for security
- QR code generation for product verification
- Comprehensive audit trails for all operations
- Real-time inventory management and tracking
- React frontend for a modern, responsive user interface

## Technical Stack

### Backend
- FastAPI (Python web framework)
- MongoDB for enterprise data storage
- Web3.py for blockchain interactions
- IPFS integration for document storage
- Python-dotenv for environment management
- JWT-based authentication with RBAC
- Python-multipart for file handling
- Pydantic for data validation and schema enforcement
- Cryptography for secure operations
- QR code generation for batch verification

### Frontend
- React.js with hooks and context API
- TailwindCSS for responsive design
- Web3.js for blockchain interactions
- Dark/light theme support
- Role-based UI rendering
- Interactive data visualization

### Blockchain & Storage
- Ethereum compatibility (or SKALE Network)
- Smart contracts for data verification
- IPFS for decentralized document storage
- QR code generation linked to IPFS and blockchain

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── db_schema.py         # MongoDB schema definitions and indexing
│   ├── init_db.py           # Sample data initialization script
│   ├── migrate_to_new_schema.py # Database migration script
│   ├── MONGODB_SCHEMA.md    # Database schema documentation
│   ├── middleware/          # RBAC and authentication middleware
│   ├── models/              # Data models for enterprise features
│   │   ├── audit.py         # Audit log models
│   │   ├── batch.py         # Batch management models
│   │   ├── enterprise.py    # Enterprise and user models
│   │   ├── inventory.py     # Inventory management models
│   │   ├── product.py       # Product catalog models
│   │   └── traceability.py  # Supply chain event models
│   ├── routes/              # API route handlers
│   │   ├── audit.py         # Audit trail endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── batch.py         # Batch management endpoints
│   │   ├── enterprise.py    # Enterprise management endpoints
│   │   ├── inventory.py     # Inventory management endpoints
│   │   ├── product.py       # Product management endpoints
│   │   └── traceability.py  # Supply chain event endpoints
│   └── services/            # Business logic services
│       ├── audit.py         # Audit logging service
│       ├── blockchain.py    # Blockchain integration service
│       └── ipfs.py          # IPFS storage service
├── contracts/
│   └── XineteStorage.sol    # Smart contract for blockchain integration
├── frontend/
│   ├── src/                 # Source code directory
│   │   ├── components/      # React components
│   │   │   ├── BatchManagement.jsx     # Batch management UI
│   │   │   ├── EnterpriseModules.jsx   # Enterprise module navigation
│   │   │   ├── InventoryManagement.jsx # Inventory management UI
│   │   │   └── Traceability.jsx        # Traceability event tracking
│   │   ├── contexts/        # React context providers
│   │   │   └── ThemeContext.jsx        # Dark/light theme support
│   │   └── App.jsx          # Main application with auth context
│   ├── index.html           # HTML entry point
│   ├── package.json         # Frontend dependencies
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.js       # Vite bundler configuration
├── scripts/
│   └── deploy.js            # Smart contract deployment script
├── artifacts/               # Compiled contract artifacts
├── DEPLOYMENT.md            # Detailed deployment instructions
├── hardhat.config.js        # Hardhat blockchain configuration
├── package.json             # Project dependencies
└── requirements.txt         # Python dependencies
```

## MongoDB Schema

The application uses MongoDB with the following collection structure:

1. **enterprises** - Company information
2. **accounts** - Enterprise user accounts with role-based permissions
3. **products** - Product catalog for enterprises
4. **batches** - Production batches with IPFS and blockchain integration
5. **traceability** - Supply chain events with IPFS and blockchain integration
6. **inventory** - Current stock levels across different locations
7. **audit_logs** - Comprehensive system activity logs

For detailed schema information, refer to `backend/MONGODB_SCHEMA.md`.

## MongoDB Connection

The application is configured to automatically connect to MongoDB using the connection string and authentication credentials specified in the `.env` file:

```
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/xinete_storage
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
```

### Connection Options:

#### 1. Without Authentication (Development)
```
MONGODB_URL=mongodb://localhost:27017/xinete_storage
```

#### 2. With Authentication (Production)
```
MONGODB_URL=mongodb://localhost:27017/xinete_storage
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
```

#### 3. Connection String with Authentication (Alternative)
```
MONGODB_URL=mongodb://your_username:your_password@localhost:27017/xinete_storage
```

When deploying on a VM:
1. Ensure MongoDB is installed and running on the VM or accessible from the VM
2. Update the `.env` file with the correct MongoDB connection details
3. If MongoDB requires authentication, provide the username and password
4. The application will automatically connect to MongoDB when started

The enhanced connection logic in `main.py` handles authentication automatically:

```python
# Setup MongoDB connection with authentication
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/xinete_storage")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")

# Authentication is used if credentials are provided
if MONGODB_USERNAME and MONGODB_PASSWORD:
    # Connection logic with authentication
    ...
else:
    # Connection logic without authentication
    ...
```

### Database Initialization

The application includes scripts to set up and initialize the database:

1. `db_schema.py` - Sets up collections, schema validation, and indexes
2. `init_db.py` - Populates collections with sample data for testing
3. `migrate_to_new_schema.py` - Migrates data from old schema to new schema

Run these scripts in order when setting up a new instance:

```bash
python db_schema.py
python init_db.py  # Optional, for sample data
```

## Setup Instructions

### Prerequisites

1. Node.js (v14 or higher)
2. Python (v3.8 or higher)
3. MongoDB (v4.4 or higher)
4. Git

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd xinete-enterprise
```

2. Backend Setup:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cd backend
cp .env.example .env
```

3. Edit `.env` with your credentials:
```
MONGODB_URL=mongodb://localhost:27017/xinete_storage
JWT_SECRET=your_secure_jwt_secret
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```
4. Initialize the Database:

```bash
# Set up MongoDB schema and indexes
python db_schema.py

# (Optional) Load sample data
python init_db.py
```

5. Smart Contract Deployment:
```bash
# Install dependencies
npm install

# Deploy the smart contract
npx hardhat run scripts/deploy.js --network <your-network>

# Note: Save the contract address displayed in the console
# Update the contract address in the frontend environment
```

6. Frontend Setup:
```bash
cd frontend
npm install

# Create frontend environment file
echo "VITE_API_URL=http://localhost:8000" > .env
```

## Running the Application

### Development Environment

1. Start the MongoDB server (if running locally):
```bash
# The command may vary depending on your MongoDB installation
mongod --dbpath /path/to/data/directory
```

2. Start the Backend:
```bash
cd backend
uvicorn main:app --reload
```

3. Start the Frontend:
```bash
cd frontend
npm run dev
```

4. Access the development environment:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Deployment

For detailed production deployment instructions, refer to `DEPLOYMENT.md` which includes:

- VM configuration
- Environment setup
- MongoDB configuration
- Nginx setup
- PM2 process management
- SSL configuration

## Enterprise Features

### 1. Batch Management with Blockchain Integration
- Create and track production batches with unique IDs
- Store batch documentation on IPFS with CID tracking
- Record blockchain transaction hashes for verification
- QR code generation for easy batch verification
- Support for batch lifecycle status tracking

### 2. Supply Chain Traceability
- Record events throughout the supply chain lifecycle
- Document every step from production to delivery
- IPFS storage for event documentation
- Blockchain verification for event authenticity
- Timeline visualization of batch journey

### 3. Inventory Management
- Real-time inventory tracking across locations
- Automated inventory updates from batch and traceability events
- Location-based inventory management
- Low stock alerts and notifications
- Comprehensive inventory audit trails

### 4. Role-Based Access Control (RBAC)
- Fine-grained permission management
- Role-specific UI elements and capabilities
- Secure middleware for API endpoint protection
- Role-based audit logging for accountability
- Support for various enterprise roles (admin, supply_chain_head, etc.)

### 5. Audit Logging
- Comprehensive change tracking for all entities
- User-specific action logging
- Before/after value comparison
- Timestamp and user tracking
- Filterable audit trail viewing

### 6. MongoDB Integration
- Schema validation for data integrity
- Optimized indexing for query performance
- Structured data relationships
- Flexible schema for custom enterprise fields
- Detailed documentation of database design

## Security Features

1. JWT-based authentication with role claims
2. IPFS for decentralized document storage
3. Blockchain integration for data verification
4. Comprehensive audit logging for all changes
5. Role-based access control for all endpoints
6. Protected environment variables for sensitive data

## API Documentation

The API documentation is available at `/docs` when running the backend server. It provides detailed information about:

- Authentication endpoints
- Enterprise management
- Product catalog management
- Batch creation and tracking
- Traceability event recording
- Inventory management
- Audit log retrieval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes with meaningful messages
4. Push to the branch
5. Create a Pull Request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.
