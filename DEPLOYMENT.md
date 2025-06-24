# Deployment Guide for Xinete Storage Platform

## Prerequisites

1. Python 3.8+ installed
2. Node.js 14+ and npm installed
3. IPFS Pinata account with API keys
4. SKALE Network account and credentials
5. MongoDB 4.4+ installed and running

## Backend Deployment

### 1. Environment Setup

Create a `.env` file in the backend directory with the following variables:

```env
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
PINATA_API_KEY=c9b9b1234ca03df077ef
PINATA_SECRET_KEY=5039f58273154b1adfef004e07ae535c8987d5c5c1c1b44ca3b75714085cb0e5
SKALE_ENDPOINT=https://testnet.skalenodes.com/v1/lanky-ill-funny-testnet
SKALE_PRIVATE_KEY=d6795c913606efc3b717b90514cbf40b666537585c6d30b019de3fcc4f17d5f6
JWT_SECRET=c8d1a95d37cb4e06b3e3fa1f89a37d2c9b8f276e3a094c51b5f1d98e2f7d4a6b
MONGODB_URL=mongodb://localhost:27017/xinete_storage
```

### 2. Initialize Database Schema

```bash
cd backend
python db_schema.py
```

This will create all required collections with schema validation and proper indexing.

### 3. (Optional) Load Sample Data

```bash
python init_db.py
```

This will populate the database with sample enterprises, users, products, batches, and traceability data for testing purposes.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Database Setup

Ensure the following files exist and have write permissions:
- `backend/users.json`
- `backend/file_metadata.json`

### 6. Start the Backend Server

Development:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Frontend Deployment

### 1. Environment Setup

Create a `.env` file in the frontend directory:

```env
VITE_BACKEND_URL=http://your-backend-url:8000
VITE_SKALE_ENDPOINT=your_skale_endpoint
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Build for Production

```bash
npm run build
```

### 4. Serve Production Build

```bash
npm run preview
```

## Cloud Deployment Steps

### Backend (Using Cloud Platform)

1. Choose a cloud provider (e.g., AWS, GCP, Azure)
2. Set up a virtual machine or container service
3. Install Python and dependencies
4. Set up environment variables
5. Use a process manager (e.g., PM2, Supervisor) to run the uvicorn server
6. Configure nginx as a reverse proxy

### Frontend (Static Hosting)

1. Build the frontend application
2. Upload the `dist` directory to a static hosting service
3. Configure the domain and SSL certificate

## Security Considerations

1. Use HTTPS for all communications
2. Implement rate limiting
3. Set up proper CORS configuration
4. Secure all API keys and sensitive data
5. Regular security audits and updates

## Monitoring and Maintenance

1. Set up logging and monitoring
2. Configure automated backups
3. Implement health checks
4. Set up alerts for system issues

## Troubleshooting

1. Check logs for errors
2. Verify environment variables
3. Confirm network connectivity
4. Validate IPFS and blockchain connections

For additional support, refer to the project documentation or contact the development team.