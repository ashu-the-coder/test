# Xinetee Decentralized Storage Platform

A decentralized storage platform built on SKALE Network that allows users to store and manage files using IPFS and blockchain technology, featuring secure hash-based file retrieval and enhanced smart contract functionality.

## Project Overview

Xinetee is a decentralized storage solution that combines:
- IPFS (InterPlanetary File System) for distributed file storage
- SKALE Network for blockchain operations
- Smart contracts for managing file ownership, access, and metadata
- FastAPI backend with JWT authentication for secure API services
- Hash-based file retrieval system for enhanced security
- React frontend for intuitive user interface

## Technical Stack

### Backend
- FastAPI (Python web framework)
- Web3.py for blockchain interactions
- Pinata SDK for IPFS integration
- Python-dotenv for environment management
- JWT-based authentication system
- Python-multipart for file handling
- Pydantic for data validation
- Cryptography for secure operations
- Beacon-chain for blockchain synchronization
- Aiohttp for async HTTP requests

### Frontend
- React.js
- Web3.js for blockchain interactions
- Modern UI components

### Blockchain
- SKALE Network (Testnet)
- Solidity smart contracts
- Hardhat development environment

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/              # API route handlers
│   ├── services/            # Business logic services
│   └── .env                 # Environment configuration
├── contracts/
│   └── XineteStorage.sol    # Smart contract
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/      # React components
│   └── package.json
├── scripts/
│   └── deploy.js            # Contract deployment script
└── hardhat.config.js        # Hardhat configuration
```

## Setup Instructions

### Prerequisites

1. Node.js (v14 or higher)
2. Python (v3.8 or higher)
3. Git

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd xinete-storage
```

2. Backend Setup:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cd backend
cp .env.example .env
# Edit .env with your credentials:
# - PINATA_API_KEY
# - PINATA_API_SECRET
# - PRIVATE_KEY
# - CONTRACT_ADDRESS
```

3. Smart Contract Deployment:
```bash
# Install dependencies
npm install

# Deploy to SKALE testnet
# The smart contract will be deployed to SKALE testnet network
# After deployment, the contract address will be displayed in the console
# Make sure to save the contract address for frontend and backend configuration
npx hardhat run scripts/deploy.js --network skale

# Note: The smart contract is deployed on SKALE testnet for testing and development purposes
# You can verify the contract on SKALE testnet explorer after deployment
```

4. Frontend Setup:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the Backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the Frontend:
```bash
cd frontend
npm run dev
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Security Considerations

1. Never commit your `.env` file containing sensitive credentials
2. Keep your private keys secure and never share them
3. Use environment variables for all sensitive configuration
4. Implement proper access controls in your smart contracts

## Features

### Hash-Based File Retrieval
- Secure file identification using cryptographic hashes
- Metadata storage on blockchain for enhanced traceability
- Efficient file deduplication system

### Authentication System
- JWT-based secure authentication
- User registration and login functionality
- Protected API endpoints

### Smart Contract Enhancements
- File ownership management
- Access control mechanisms
- Metadata storage and retrieval
- Event tracking for file operations

## API Documentation

The API documentation is available at `/docs` when running the backend server. It provides detailed information about available endpoints and their usage.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.