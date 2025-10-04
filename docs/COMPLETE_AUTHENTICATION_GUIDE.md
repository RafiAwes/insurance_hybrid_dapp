# Complete Authentication System - Buyer & Admin Guide

## 🎯 Overview

I have successfully implemented a complete dual authentication system for your Health Insurance DApp where both buyers and admins use email/password + MetaMask wallet verification. When one type of user logs in, the other option is hidden from the interface.

## 🏗️ System Architecture

### Dual Authentication Flow
1. **Admin Login**: Email/Password → Designated Admin Wallet Verification
2. **Buyer Login**: Email/Password → Individual Buyer Wallet Verification
3. **Mutual Exclusion**: Only one user type can be logged in at a time

### Backend Implementation
- **Admin Model**: Custom admin users with shared wallet address
- **Enhanced Buyer Model**: Email/password authentication + individual wallet addresses
- **Secure Authentication**: Password hashing and wallet verification
- **API Endpoints**: Separate endpoints for admin and buyer authentication

### Frontend Implementation
- **Dynamic UI**: Admin/Buyer toggle hidden when logged in
- **Dual Login Systems**: Separate login components for each user type
- **Session Management**: Proper logout and state management

## 🔐 Authentication Credentials

### Admin Access
**Login Credentials:**
- **Email**: `admin@healthinsurance.com`
- **Password**: `admin123`
- **Required Wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (Hardhat Account #0)
- **Admin ID**: `51dcd84f-a0be-45b5-9daa-dcfbcd5b60a6`

### Buyer Access
**Login Credentials:**
- **Email**: `buyer@healthinsurance.com`
- **Password**: `buyer123`
- **Required Wallet**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` (Hardhat Account #1)
- **Buyer ID**: `55f5cf0d-2696-4ae4-89ca-7562c14ca01d`

## 🚀 How to Access Each System

### Method 1: Admin Access

1. **Open Frontend**: `http://localhost:5173`
2. **Click "🛡️ Admin"** in header toggle
3. **Enter Admin Credentials**:
   - Email: `admin@healthinsurance.com`
   - Password: `admin123`
4. **Connect MetaMask** with admin wallet: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
5. **Verify Wallet** → Access admin dashboard

### Method 2: Buyer Access

1. **Open Frontend**: `http://localhost:5173`
2. **Click "👤 Buyer"** in header toggle (default view)
3. **Enter Buyer Credentials**:
   - Email: `buyer@healthinsurance.com`
   - Password: `buyer123`
4. **Connect MetaMask** with buyer wallet: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
5. **Verify Wallet** → Access buyer dashboard

## 🔄 User Interface Behavior

### When No One is Logged In
```
Header: 🏥 Health Insurance DApp    [👤 Buyer] [🛡️ Admin]    [Logout]
                                    ↑ Both options visible
```

### When Admin is Logged In
```
Header: 🏥 Health Insurance DApp    [🛡️ Admin Portal]    Welcome, System Administrator    [Logout]
                                    ↑ Only admin portal shown, buyer option hidden
```

### When Buyer is Logged In
```
Header: 🏥 Health Insurance DApp    [👤 Buyer Portal]    Welcome, John Doe    [Logout]
                                    ↑ Only buyer portal shown, admin option hidden
```

## 🛠️ Backend API Endpoints

### Admin Endpoints
```http
POST /api/admin/login/              # Admin email/password login
POST /api/admin/verify-wallet/      # Admin wallet verification
GET  /api/admin/claims/             # Get all claims for admin
GET  /api/admin/buyers/             # Get all buyers for admin
POST /api/admin/update-claim-status/ # Approve/reject claims
```

### Buyer Endpoints
```http
POST /api/buyer/login/              # Buyer email/password login
POST /api/buyer/verify-wallet/      # Buyer wallet verification
POST /api/buyer/register/           # Register new buyer
```

### Existing Buyer Operations
```http
POST /api/submit-claim/             # Submit insurance claim
GET  /api/claim-history/            # Get buyer's claim history
POST /api/upload-claim-doc/         # Upload claim documents
```

## 🔒 Security Features

### 1. **Dual Authentication**
- **Email/Password**: Traditional secure authentication
- **MetaMask Wallet**: Blockchain-based verification
- **Both Required**: Neither alone provides access

### 2. **Wallet Address Validation**
- **Admin**: Must use designated admin wallet (`0xf39F...2266`)
- **Buyer**: Must use their registered individual wallet
- **Format Validation**: Proper Ethereum address format checking

### 3. **Session Management**
- **Mutual Exclusion**: Admin login clears buyer session and vice versa
- **Secure Logout**: Clears all authentication data
- **Login Tracking**: Timestamps and activity monitoring

### 4. **Password Security**
- **Django Hashing**: Secure password storage
- **No Plain Text**: Passwords never stored in readable format
- **Validation**: Strong password requirements

## 📱 Frontend Components

### 1. **AdminLogin Component** ([`frontend/src/components/AdminLogin.tsx`](frontend/src/components/AdminLogin.tsx))
- **Two-step authentication** for admin users
- **Admin wallet verification** with designated address
- **Professional blue-themed UI**

### 2. **BuyerLogin Component** ([`frontend/src/components/BuyerLogin.tsx`](frontend/src/components/BuyerLogin.tsx))
- **Two-step authentication** for buyer users
- **Individual wallet verification** with registered address
- **Professional green-themed UI**

### 3. **Enhanced App Component** ([`frontend/src/App.tsx`](frontend/src/App.tsx))
- **Dynamic toggle visibility**: Hides options when logged in
- **User type indication**: Shows current portal type
- **Proper state management**: Handles admin/buyer sessions

## 🔧 Management Commands

### Create Admin User
```bash
cd backend
python manage.py create_admin --email admin@example.com --password securepass --name "Admin Name"
```

### Create Buyer User
```bash
cd backend
python manage.py create_buyer --email buyer@example.com --password securepass --name "Buyer Name" --wallet 0x1234... --national-id "ID123" --phone "+1234567890"
```

### List Users
```bash
cd backend
python manage.py shell
>>> from insurance.models import Admin, Buyer
>>> Admin.objects.all()
>>> Buyer.objects.all()
```

## 🎮 Testing the System

### Test Admin Login
1. **Open frontend** → Click "🛡️ Admin"
2. **Login**: `admin@healthinsurance.com` / `admin123`
3. **MetaMask**: Connect with `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
4. **Result**: Admin dashboard + buyer option disappears

### Test Buyer Login
1. **Logout** from admin (if logged in)
2. **Click "👤 Buyer"** (should reappear after logout)
3. **Login**: `buyer@healthinsurance.com` / `buyer123`
4. **MetaMask**: Connect with `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
5. **Result**: Buyer dashboard + admin option disappears

### Test Mutual Exclusion
1. **Login as admin** → Buyer option hidden
2. **Logout** → Both options reappear
3. **Login as buyer** → Admin option hidden
4. **Logout** → Both options reappear

## 🔍 Wallet Address Management

### Admin Wallet (Shared)
- **Address**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- **Source**: Hardhat Account #0
- **Usage**: All admins use this same wallet
- **Configuration**: Stored in `.env` as `ADMIN_WALLET_ADDRESS`

### Buyer Wallets (Individual)
- **Address**: Unique for each buyer (registered during account creation)
- **Example**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` (Hardhat Account #1)
- **Usage**: Each buyer has their own wallet address
- **Verification**: Must match registered wallet during login

## 🚨 Troubleshooting

### Issue: "Wallet address does not match"
**For Admin**: Use `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
**For Buyer**: Use the wallet address registered for that buyer account

### Issue: "Invalid email or password"
**Admin**: `admin@healthinsurance.com` / `admin123`
**Buyer**: `buyer@healthinsurance.com` / `buyer123`

### Issue: Toggle buttons not hiding
**Solution**: Make sure both users are properly logged out and App.tsx is updated

### Issue: Network errors
**Solution**: Ensure Django server is running and CORS is configured

## 📊 System Benefits

### 1. **Enhanced Security**
- **Two-factor authentication** for both user types
- **Individual wallet verification** for buyers
- **Shared admin wallet** for administrative control

### 2. **User Experience**
- **Clear separation** between admin and buyer interfaces
- **Intuitive navigation** with dynamic UI elements
- **Professional design** with distinct themes

### 3. **Scalability**
- **Multiple admins** can use the same wallet
- **Unlimited buyers** with individual wallets
- **Easy user management** with Django commands

### 4. **Blockchain Integration**
- **MetaMask verification** ensures wallet ownership
- **Smart contract compatibility** with user roles
- **Secure transaction signing** with verified wallets

## 🎉 Ready-to-Use Accounts

### **Admin Account** ✅
- **Email**: `admin@healthinsurance.com`
- **Password**: `admin123`
- **Wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

### **Buyer Account** ✅
- **Email**: `buyer@healthinsurance.com`
- **Password**: `buyer123`
- **Wallet**: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`

## 🔄 Complete Workflow

### Admin Workflow
1. **Access**: Click "🛡️ Admin" → Login → Verify wallet
2. **Features**: Manage all claims, view all buyers, system analytics
3. **Logout**: Admin option reappears for buyers

### Buyer Workflow
1. **Access**: Click "👤 Buyer" → Login → Verify wallet
2. **Features**: Submit claims, view history, manage profile
3. **Logout**: Buyer option reappears for admins

Your complete authentication system is now operational with mutual exclusion between admin and buyer access! 🎉

## 📋 Quick Access Summary

**Frontend URL**: `http://localhost:5173`

**Admin Access**: Header → "🛡️ Admin" → `admin@healthinsurance.com` / `admin123` → MetaMask `0xf39F...2266`

**Buyer Access**: Header → "👤 Buyer" → `buyer@healthinsurance.com` / `buyer123` → MetaMask `0x7099...79C8`

The system now works exactly as you requested - buyers login the same way as admins, each with their own wallet addresses, and the interface dynamically hides the other option when one user type is logged in.