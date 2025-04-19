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
│   ├── models/              # Data models and schemas
│   ├── routes/              # API route handlers
│   ├── services/            # Business logic services
│   ├── file_metadata.json   # File metadata storage
│   ├── users.json           # User data storage
│   └── user_data/           # User-specific data directory
├── contracts/
│   └── XineteStorage.sol    # Smart contract for storage management
├── frontend/
│   ├── src/                 # Source code directory
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API and blockchain services
│   │   ├── styles/          # CSS and styling files
│   │   ├── utils/           # Utility functions
│   │   └── App.jsx          # Main application component
│   ├── index.html           # HTML entry point
│   ├── package.json         # Frontend dependencies
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── postcss.config.js    # PostCSS configuration
│   └── vite.config.js       # Vite bundler configuration
├── scripts/
│   └── deploy.js            # Contract deployment script
├── artifacts/               # Compiled contract artifacts
├── cache/                   # Hardhat cache directory
├── hardhat.config.js        # Hardhat configuration
├── package.json             # Project dependencies
└── requirements.txt         # Python dependencies
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

### Development Environment

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

3. Access the development environment:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Environment

The application is deployed and accessible at:
- Frontend: http://164.52.203.17:5173
- Backend API: http://164.52.203.17:8000
- API Documentation: http://164.52.203.17:8000/docs

## Security Considerations

1. Never commit your `.env` file containing sensitive credentials
2. Keep your private keys secure and never share them
3. Use environment variables for all sensitive configuration
4. Implement proper access controls in your smart contracts

## Features

### User Authentication and Profile Management
- JWT-based secure authentication system
- User registration and login functionality
- MetaMask wallet integration for blockchain interactions
- User profile management with wallet address linking
- Protected API endpoints with role-based access control

### File Management System
- Secure file upload and download through IPFS
- Pinata service integration for reliable IPFS pinning
- File metadata storage on blockchain
- Efficient file deduplication system
- Hash-based file identification and retrieval
- File sharing capabilities between users

### Smart Contract Features
- File ownership management and tracking
- Access control mechanisms for shared files
- Metadata storage and retrieval
- Event tracking for all file operations
- Integration with SKALE Network for scalability

### User Interface
- Modern and responsive React-based interface
- Dark/Light theme support for better user experience
- Real-time file upload progress tracking
- Intuitive file management dashboard
- Seamless MetaMask integration for transactions

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
