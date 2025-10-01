# Hybrid Insurance DApp - Requirements & Dependencies

This document outlines all the requirements and dependencies needed to run the Hybrid Insurance DApp project.

## System Requirements

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.9 or higher
- **PostgreSQL**: v13 or higher (for production) or SQLite (for development)
- **Git**: Latest version

### Operating System Support
- Windows 10/11
- macOS 10.15+
- Ubuntu 20.04+

## Project Structure Dependencies

### 1. Backend (Django) Dependencies

#### Core Requirements
```txt
# Core Django Framework
Django>=4.2.0,<5.0.0
djangorestframework>=3.14.0

# Database
psycopg2-binary>=2.9.0

# Web3 Integration
web3>=6.0.0

# Environment Variables
python-decouple>=3.8
python-dotenv>=1.0.0

# HTTP Requests (for external API calls)
requests>=2.31.0

# JSON Handling (for performance)
ujson>=5.8.0

# CORS Headers (for frontend-backend communication)
django-cors-headers>=4.3.0

# Security & Authentication
djangorestframework-simplejwt>=5.3.0

# Development & Debugging (optional but recommended)
django-debug-toolbar>=4.2.0

# Production WSGI Server
gunicorn>=21.2.0

# Static Files Handling
whitenoise>=6.5.0

# Cryptography (for encryption features)
cryptography>=41.0.0

# Date/Time Utilities
python-dateutil>=2.8.0

# Validation
validators>=0.22.0

# Logging
structlog>=23.1.0

# Testing (optional)
pytest>=7.4.0
pytest-django>=4.5.0
factory-boy>=3.3.0

# Code Quality (optional)
flake8>=6.0.0
black>=23.7.0
isort>=5.12.0
```

#### Installation Command
```bash
cd backend
pip install -r requirements.txt
```

### 2. Frontend (React + Vite) Dependencies

#### Package.json Dependencies
```json
{
  "name": "health-insurance-dapp-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "@storacha/client": "^1.7.10",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "web3": "^4.0.3"
  },
  "devDependencies": {
    "@types/node": "^20.11.30",
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "@typescript-eslint/eslint-plugin": "^7.15.0",
    "@typescript-eslint/parser": "^7.15.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.19",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.6",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.2.2",
    "vite": "^5.2.0"
  }
}
```

#### Installation Commands
```bash
cd frontend
npm install
# or
yarn install
```

### 3. Blockchain Development Dependencies

#### Global Dependencies
```bash
# Install Hardhat globally (optional)
npm install -g hardhat

# Install Hardhat locally (recommended)
npm install --save-dev hardhat

# Essential Hardhat plugins
npm install --save-dev @nomicfoundation/hardhat-toolbox
npm install --save-dev @nomicfoundation/hardhat-network-helpers
npm install --save-dev @nomicfoundation/hardhat-chai-matchers
npm install --save-dev @nomicfoundation/hardhat-ethers
npm install --save-dev @typechain/hardhat
npm install --save-dev chai
npm install --save-dev ethers
npm install --save-dev hardhat-gas-reporter
npm install --save-dev solidity-coverage
npm install --save-dev @typechain/ethers-v6
npm install --save-dev @typechain/chai
```

#### Root Package.json (Create if not exists)
```json
{
  "name": "hybrid-insurance-dapp",
  "version": "1.0.0",
  "description": "Hybrid Insurance DApp with Django backend and React frontend",
  "scripts": {
    "compile": "hardhat compile",
    "test": "hardhat test",
    "deploy": "hardhat run scripts/deploy.js",
    "node": "hardhat node",
    "frontend": "cd frontend && npm run dev",
    "backend": "cd backend && python manage.py runserver",
    "install-all": "npm install && cd frontend && npm install && cd ../backend && pip install -r requirements.txt"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^4.0.0",
    "hardhat": "^2.19.0"
  },
  "dependencies": {
    "dotenv": "^16.3.1"
  }
}
```

## Environment Setup

### 1. Environment Variables

#### Root .env file
```env
# Backend environment variables
DJANGO_SECRET_KEY=django-insecure-your-secret-key-change-in-production
DEBUG=True
DB_NAME=health_insurance_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
HARDHAT_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0xYourDeployedContractAddressHere
STORACHA_API_KEY=your-storacha-api-key

# Frontend environment variables
VITE_CONTRACT_ADDRESS=0xYourDeployedContractAddressHere
VITE_BACKEND_URL=http://localhost:8000/api

# Database URL (for production)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 2. Database Setup

#### PostgreSQL (Production)
```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/

# Create database
sudo -u postgres createdb health_insurance_db
sudo -u postgres createuser --interactive
```

#### SQLite (Development)
```bash
# SQLite comes with Python, no additional installation needed
# Django will create the database file automatically
```

## Installation Guide

### Quick Start (All Dependencies)
```bash
# 1. Clone the repository
git clone <repository-url>
cd hybrid_Insurance_reviced

# 2. Install root dependencies
npm install

# 3. Install frontend dependencies
cd frontend
npm install
cd ..

# 4. Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your actual values

# 6. Run database migrations
cd backend
python manage.py migrate
cd ..

# 7. Compile smart contracts
npx hardhat compile
```

### Development Workflow

#### Start Development Servers
```bash
# Terminal 1: Start Hardhat local blockchain
npx hardhat node

# Terminal 2: Start Django backend
cd backend
python manage.py runserver

# Terminal 3: Start React frontend
cd frontend
npm run dev
```

#### Deploy Smart Contract
```bash
# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost

# Deploy to testnet (configure network in hardhat.config.js)
npx hardhat run scripts/deploy.js --network sepolia
```

## Common Issues & Solutions

### 1. JSON Parsing Error in Django
**Error**: `JSONDecodeError: Expecting value: line 1 column 2 (char 1)`

**Solution**: 
- Ensure smart contract ABI is properly generated and loaded
- Check that `CONTRACT_ADDRESS` in .env is a valid Ethereum address
- Compile smart contracts first: `npx hardhat compile`

### 2. Web3 Connection Issues
**Error**: `AttributeError: 'Empty' object has no attribute 'address'`

**Solution**:
- Verify `HARDHAT_RPC_URL` is correct in .env
- Ensure Hardhat node is running: `npx hardhat node`
- Check contract address format (must be 42 characters starting with 0x)

### 3. Database Connection Issues
**Error**: Database connection errors

**Solution**:
- Verify PostgreSQL is running
- Check database credentials in .env
- Run migrations: `python manage.py migrate`

### 4. Frontend Build Issues
**Error**: Module not found errors

**Solution**:
- Clear node_modules: `rm -rf node_modules package-lock.json`
- Reinstall: `npm install`
- Check Node.js version compatibility

## Production Deployment

### Backend (Django)
```bash
# Install production dependencies
pip install gunicorn whitenoise

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn backend.wsgi:application
```

### Frontend (React)
```bash
# Build for production
npm run build

# Serve with a static server
npm install -g serve
serve -s dist
```

### Smart Contracts
```bash
# Deploy to mainnet (configure network first)
npx hardhat run scripts/deploy.js --network mainnet
```

## Additional Tools (Optional)

### Development Tools
- **Metamask**: Browser wallet for testing
- **Ganache**: Alternative to Hardhat for local blockchain
- **Remix IDE**: Online Solidity IDE
- **Postman**: API testing
- **pgAdmin**: PostgreSQL administration

### Code Quality Tools
```bash
# Python
pip install black flake8 isort

# JavaScript/TypeScript
npm install -g prettier eslint
```

## Support

For issues and questions:
1. Check this requirements document
2. Review error logs carefully
3. Ensure all dependencies are installed correctly
4. Verify environment variables are set properly
5. Check that all services (database, blockchain node) are running