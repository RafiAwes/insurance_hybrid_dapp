
# Admin Access Guide - Health Insurance DApp

## 🛡️ Overview

This guide covers how to access and use the admin features of the Health Insurance DApp, including both Django admin interface and frontend admin dashboard.

## 📋 Table of Contents

1. [Django Admin Setup](#django-admin-setup)
2. [Creating Admin User](#creating-admin-user)
3. [Accessing Django Admin](#accessing-django-admin)
4. [Frontend Admin Dashboard](#frontend-admin-dashboard)
5. [Admin Features](#admin-features)
6. [Smart Contract Admin](#smart-contract-admin)
7. [Troubleshooting](#troubleshooting)

## 🔧 Django Admin Setup

### Step 1: Create Superuser Account

```bash
# Navigate to backend directory
cd backend

# Create superuser (admin account)
python manage.py createsuperuser

# You'll be prompted to enter:
# - Username: admin (or your preferred username)
# - Email: your-email@example.com
# - Password: (choose a strong password)
# - Password (again): (confirm password)
```

**Example:**
```
Username (leave blank to use 'your-computer-name'): admin
Email address: admin@healthinsurance.com
Password: ********
Password (again): ********
Superuser created successfully.
```

### Step 2: Verify Django Server is Running

```bash
# Make sure Django server is running
python manage.py runserver

# Should see:
# Starting development server at http://127.0.0.1:8000/
```

## 🌐 Accessing Django Admin

### Method 1: Direct URL Access
1. **Open your browser**
2. **Navigate to**: `http://127.0.0.1:8000/admin/`
3. **Login** with your superuser credentials

### Method 2: From Main App
1. **Go to**: `http://127.0.0.1:8000/`
2. **Add `/admin/`** to the URL
3. **Login** with your credentials

### Admin Login Screen
```
Django Administration
Username: [admin]
Password: [your-password]
[Log in]
```

## 🎛️ Django Admin Features

### Available Admin Sections

#### 1. **Buyers Management**
- **View all registered buyers**
- **Search by wallet address, name, or email**
- **Filter by registration date**
- **Edit buyer information**

**Features:**
- List view shows: Wallet Address, Name, Email, Created Date
- Search functionality
- Date filters
- Detailed edit forms

#### 2. **Claims Management**
- **View all insurance claims**
- **Approve or reject claims in bulk**
- **Search by claim ID, buyer, or hospital transaction**
- **Filter by claim status**

**Features:**
- List view shows: Claim ID, Buyer, Amount, Status, Date
- Bulk actions: "Approve selected claims", "Reject selected claims"
- Status filtering: Pending, Verified, Rejected
- Detailed claim information

#### 3. **Policies Management**
- **View all insurance policies**
- **Manage policy types and coverage**
- **Filter by active/inactive status**

#### 4. **Hospital Transaction Records**
- **View encrypted medical records**
- **Track IPFS storage (Storacha CIDs)**
- **Search by transaction ID**

#### 5. **Claim Documents**
- **View uploaded claim documents**
- **Track document storage on IPFS**
- **Link documents to specific claims**

### Admin Actions

#### Bulk Claim Management
1. **Go to Claims section**
2. **Select multiple claims** using checkboxes
3. **Choose action** from dropdown:
   - "Approve selected claims"
   - "Reject selected claims"
4. **Click "Go"** to execute

#### Individual Claim Management
1. **Click on a claim ID** to open details
2. **Change claim_status** field:
   - `pending` → `verified` (approved)
   - `pending` → `rejected` (denied)
3. **Click "Save"**

## 💻 Frontend Admin Dashboard

### Accessing Frontend Admin

The frontend admin dashboard is integrated into the main React app. Here's how to access it:

#### Method 1: Add Admin Route (Recommended)

1. **Update App.tsx** to include admin access:

```typescript
// Add this to your App.tsx
import AdminDashboard from './components/AdminDashboard'

// Add admin route logic
const isAdmin = (account: string) => {
  // Define admin wallet addresses
  const adminAddresses = [
    '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', // Hardhat account #0
    '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', // Hardhat account #1
    // Add your admin wallet addresses here
  ];
  return adminAddresses.includes(account);
};

// In your render method, add admin check
{connectedAccount && isAdmin(connectedAccount) && (
  <div className="mt-8">
    <AdminDashboard />
  </div>
)}
```

#### Method 2: Direct Component Access

1. **Import AdminDashboard** in your App.tsx
2. **Add admin wallet check**
3. **Render AdminDashboard** for admin users

### Frontend Admin Features

#### 1. **Claims Management Tab**
- **View all claims** in a table format
- **Approve/Reject claims** with one click
- **Real-time status updates**
- **Search and filter capabilities**

#### 2. **Buyers Tab**
- **View all registered buyers**
- **See wallet addresses and contact info**
- **Registration date tracking**

#### 3. **Analytics Tab**
- **System statistics**:
  - Total claims count
  - Approved claims count
  - Pending claims count
- **Recent activity feed**
- **Visual data representation**

## 🔐 Smart Contract Admin

### Contract Admin Setup

The smart contract has an admin role that's set during deployment:

```solidity
// In HealthInsurance.sol
address public admin;

constructor() {
    admin = msg.sender; // Deployer becomes admin
}

modifier onlyAdmin() {
    require(msg.sender == admin, "Only admin");
    _;
}
```

### Admin Functions in Smart Contract

#### 1. **Register Buyer**
```solidity
function registerBuyer(address buyer) external onlyAdmin
```
- Only admin can register new buyers
- Adds buyer to the approved list

#### 2. **Verify Claims**
```solidity
function verifyClaim(string calldata _claimId, bool _status) external onlyAdmin
```
- Only admin can approve/reject claims
- Updates claim verification status

### Getting Admin Wallet Address

When you deploy the contract, the deployer's address becomes the admin:

```bash
# Deploy contract
npx hardhat run scripts/deploy.js --network localhost

# Output will show:
# Deploying contracts with the account: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
# HealthInsurance deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3

# The deployer address (0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266) is the admin
```

## 🚀 Quick Start Guide

### For Django Admin Access:

1. **Create superuser**:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

2. **Access admin panel**:
   - URL: `http://127.0.0.1:8000/admin/`
   - Login with superuser credentials

3. **Manage the system**:
   - View/edit buyers, claims, policies
   - Approve/reject claims in bulk
   - Monitor system activity

### For Frontend Admin Access:

1. **Connect with admin wallet**:
   - Use MetaMask with the contract deployer address
   - Or add your wallet to admin list

2. **Access admin dashboard**:
   - Admin features appear automatically for admin wallets
   - Use the AdminDashboard component

3. **Manage claims**:
   - View all claims in table format
   - Approve/reject with one click
   - Monitor real-time updates

## 🔧 Configuration

### Adding Admin Wallets

#### Method 1: In Frontend Code
```typescript
// In App.tsx or AdminDashboard.tsx
const adminAddresses = [
  '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', // Hardhat account #0
  '0x70997970C51812dc3A010C7d01b50e0d17dc79C8', // Hardhat account #1
  '0xYourWalletAddressHere',                      // Your wallet
];
```

#### Method 2: Environment Variables
```bash
# Add to .env
ADMIN_WALLETS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266,0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

### Django Admin Customization

The admin interface is already customized with:
- **Custom site header**: "Health Insurance DApp Administration"
- **Organized sections** for each model
- **Search and filter capabilities**
- **Bulk actions** for claim management
- **Readonly fields** for timestamps and IDs

## 🐛 Troubleshooting

### Issue: Can't access Django admin
**Solutions:**
1. **Check if superuser exists**:
   ```bash
   python manage.py shell
   from django.contrib.auth.models import User
   User.objects.filter(is_superuser=True)
   ```

2. **Create new superuser**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Check server is running**:
   ```bash
   python manage.py runserver
   ```

### Issue: "Permission denied" in Django admin
**Solutions:**
1. **Login with superuser account** (not regular user)
2. **Check user permissions** in Django admin → Users section
3. **Recreate superuser** if needed

### Issue: Frontend admin not showing
**Solutions:**
1. **Check wallet address** is in admin list
2. **Verify MetaMask connection** is working
3. **Check browser console** for errors
4. **Ensure AdminDashboard component** is imported and rendered

### Issue: Claims not updating
**Solutions:**
1. **Check API endpoints** are working
2. **Verify database connection**
3. **Check Django admin** for actual data
4. **Refresh frontend** after backend changes

### Issue: Smart contract admin functions failing
**Solutions:**
1. **Use deployer wallet** for admin functions
2. **Check contract address** is correct
3. **Verify network connection** (Hardhat node running)
4. **Check gas fees** and account balance

## 📊 Admin Workflow

### Daily Admin Tasks

1. **Morning Check**:
   - Login to Django admin
   - Review new claims
   - Check system health

2. **Claim Processing**:
   - Review pending claims
   - Verify medical documents
   - Approve/reject claims
   - Update claim status

3. **User Management**:
   - Review new buyer registrations
   - Handle user support requests
   - Monitor system usage

4. **System Monitoring**:
   - Check analytics dashboard
   - Monitor blockchain transactions
   - Review error logs

### Emergency Procedures

1. **System Issues**:
   - Check Django admin for errors
   - Review server logs
   - Restart services if needed

2. **Fraudulent Claims**:
   - Reject suspicious claims
   - Flag buyer accounts
   - Document incidents

3. **Smart Contract Issues**:
   - Check contract deployment
   - Verify admin permissions
   - Contact technical support

## 🔒 Security Best Practices

### Django Admin Security
1. **Use strong passwords** for superuser accounts
2. **Enable two-factor authentication** (if available)
3. **Limit admin access** to trusted personnel
4. **Regular password updates**
5. **Monitor admin activity logs**

### Wallet Security
1. **Keep admin wallet private keys secure**
2. **Use hardware wallets** for production
3. **Regular security audits**
4. **Backup wallet recovery phrases**
5. **Monitor admin wallet transactions**

### System Security
1. **Regular database backups**
2. **Server security updates**
3. **SSL certificates** for production
4. **Access logging and monitoring**
5. **Regular security assessments**

## 📞 Support

### Getting Help
1. **Check this documentation** first
2. **Review error logs** in Django admin
3. **Check browser console** for frontend issues
4. **Contact technical support** if needed

### Useful Commands
```bash
# Django management
python manage.py shell          # Django shell
python manage.py dbshell        # Database shell
python manage.py collectstatic  # Collect static files
python manage.py migrate        # Run migrations

# Hardhat management
npx hardhat console             # Hardhat console
npx hardhat node               # Start local blockchain
npx hardhat compile            # Compile contracts
npx hardhat test               # Run tests
```

## ✅ Admin Access Checklist

### Initial Setup
- [ ] Django superuser created
- [ ] Django admin accessible at `/admin/`
- [ ] Smart contract deployed
- [ ] Admin wallet address noted
- [ ] Frontend admin component integrated

### Daily Operations
- [ ] Django admin login working
- [ ] Claims management functional
- [ ] Buyer registration working
- [ ] Analytics dashboard accessible
- [ ] Smart contract admin functions working

### Security
- [ ] Strong admin passwords set
- [ ] Admin wallet secured
- [ ] Access logs monitored
- [ ] Regular backups performed
- [ ] Security updates applied

You now have complete admin access to manage your Health Insurance DApp! 🎉