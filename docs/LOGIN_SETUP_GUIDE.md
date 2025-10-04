# Login Setup Guide

## 🚨 Login Issue Fixed

The login functions have been implemented. You need to create admin and buyer accounts first.

## 🛠️ Setup Steps

### 1. **Easy Setup (Recommended)**

Run the Python script from the project root:

```bash
python create_test_accounts.py
```

This will create both admin and buyer accounts automatically.

### 2. **Manual Setup (Alternative)**

**Create Admin Account**:
```bash
cd backend
python manage.py create_admin --email admin@example.com --password admin123 --name "System Admin"
```

**Create Buyer Account** (note the hyphen in `--national-id`):
```bash
cd backend
python manage.py create_buyer --email buyer@example.com --password buyer123 --name "Test Buyer" --wallet 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 --national-id "123456789"
```

### 3. **Login Credentials**

**Admin Login**:
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Required Wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (Hardhat Account #0)

**Buyer Login**:
- **Email**: `buyer@example.com`
- **Password**: `buyer123`
- **Required Wallet**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` (Hardhat Account #1)

### 4. **Database Migration**

Make sure to run migrations for the new fields:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 5. **MetaMask Setup**

**For Admin**:
- Import Hardhat Account #0: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
- Address should be: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

**For Buyer**:
- Import Hardhat Account #1: `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d`
- Address should be: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`

### 6. **Network Configuration**

Make sure MetaMask is connected to:
- **Network**: Hardhat Local
- **RPC URL**: `http://127.0.0.1:8545`
- **Chain ID**: `31337`

## 🔐 Login Flow

### **Admin Login**:
1. Go to Admin Login page
2. Enter email: `admin@example.com`
3. Enter password: `admin123`
4. Click "Login"
5. Connect MetaMask with admin wallet (`0xf39F...2266`)
6. Click "Verify MetaMask Wallet"

### **Buyer Login**:
1. Go to Buyer Login page
2. Enter email: `buyer@example.com`
3. Enter password: `buyer123`
4. Click "Login"
5. Connect MetaMask with buyer wallet (`0x7099...79C8`)
6. Click "Verify MetaMask Wallet"

## 🐛 Troubleshooting

### **"Invalid email or password"**:
- Make sure you created the accounts using the commands above
- Check that the database is running and migrations are applied

### **"Wallet verification failed"**:
- Ensure you're using the correct MetaMask account
- Check that MetaMask is connected to Hardhat Local network
- Verify the wallet addresses match exactly

### **"Network error"**:
- Make sure Django backend is running: `python manage.py runserver`
- Check that the backend URL is correct in frontend `.env`
- Verify CORS settings allow frontend requests

### **Database errors**:
- Run migrations: `python manage.py migrate`
- Check database connection in Django settings

## 📋 Quick Test Commands

**Option 1 - Using Python Script (Recommended)**:
```bash
# Setup accounts
python create_test_accounts.py

# Run migrations and start server
cd backend
python manage.py migrate
python manage.py runserver

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

**Option 2 - Manual Commands**:
```bash
# Backend setup
cd backend
python manage.py migrate
python manage.py create_admin --email admin@example.com --password admin123 --name "System Admin"
python manage.py create_buyer --email buyer@example.com --password buyer123 --name "Test Buyer" --wallet 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 --national-id "123456789"
python manage.py runserver

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

## 🎯 Next Steps After Login

1. **Admin**: Register the buyer address `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` for blockchain payments
2. **Buyer**: Try paying premium (should work after registration)
3. **Test**: Submit claims with documents (will use centralized Storacha account)

The login system now works with proper authentication and wallet verification!