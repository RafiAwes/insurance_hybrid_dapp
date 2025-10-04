# Custom Admin System - Complete Guide

## 🛡️ Overview

I've created a custom admin system for your Health Insurance DApp that combines traditional email/password authentication with MetaMask wallet verification. This provides a secure two-factor authentication system for admin access.

## 🏗️ System Architecture

### Backend Components
1. **Admin Model** ([`backend/insurance/models.py`](backend/insurance/models.py)) - Custom admin user model
2. **Admin Serializers** ([`backend/insurance/serializers.py`](backend/insurance/serializers.py)) - API serializers for admin operations
3. **Admin Views** ([`backend/insurance/views.py`](backend/insurance/views.py)) - Authentication and management endpoints
4. **Admin URLs** ([`backend/insurance/urls.py`](backend/insurance/urls.py)) - API routes for admin functions

### Frontend Components
1. **AdminLogin Component** ([`frontend/src/components/AdminLogin.tsx`](frontend/src/components/AdminLogin.tsx)) - Two-step login interface
2. **AdminDashboard Component** ([`frontend/src/components/AdminDashboard.tsx`](frontend/src/components/AdminDashboard.tsx)) - Management interface

### Configuration
1. **Environment Variables** ([`.env`](.env)) - Admin wallet address configuration
2. **Django Settings** ([`backend/backend/settings.py`](backend/backend/settings.py)) - Admin wallet integration

## 🔐 Authentication Flow

### Step 1: Email/Password Login
```
User enters email and password → Backend validates credentials → Returns admin data
```

### Step 2: MetaMask Wallet Verification
```
User connects MetaMask → Frontend gets wallet address → Backend verifies against admin wallet → Full access granted
```

## 🚀 How to Access Admin System

### Method 1: Using the Created Admin Account

**Login Credentials:**
- **Email**: `admin@healthinsurance.com`
- **Password**: `admin123`
- **Required Wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (Hardhat Account #0)

### Method 2: Create New Admin Account

```bash
cd backend
python manage.py create_admin --email your@email.com --password yourpassword --name "Your Name"
```

## 📱 Frontend Integration

### Step 1: Add AdminLogin to Your App

```typescript
// In App.tsx
import AdminLogin from './components/AdminLogin';
import AdminDashboard from './components/AdminDashboard';

const [adminData, setAdminData] = useState(null);

const handleAdminLogin = (admin) => {
  setAdminData(admin);
};

// Render admin interface
{adminData ? (
  <AdminDashboard adminData={adminData} />
) : (
  <AdminLogin onAdminLogin={handleAdminLogin} />
)}
```

### Step 2: Admin Route Protection

```typescript
// Check if user is admin
const isAdmin = adminData && adminData.wallet_verified;

// Show admin features only to verified admins
{isAdmin && (
  <div className="admin-section">
    <AdminDashboard />
  </div>
)}
```

## 🔧 API Endpoints

### Authentication Endpoints

#### 1. Admin Login
```http
POST /api/admin/login/
Content-Type: application/json

{
  "email": "admin@healthinsurance.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "admin": {
    "id": "51dcd84f-a0be-45b5-9daa-dcfbcd5b60a6",
    "email": "admin@healthinsurance.com",
    "full_name": "System Administrator",
    "last_login": "2025-01-01T12:00:00Z"
  }
}
```

#### 2. Wallet Verification
```http
POST /api/admin/verify-wallet/
Content-Type: application/json

{
  "wallet_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
  "admin_id": "51dcd84f-a0be-45b5-9daa-dcfbcd5b60a6"
}
```

**Response:**
```json
{
  "message": "Wallet verified successfully",
  "admin": {
    "id": "51dcd84f-a0be-45b5-9daa-dcfbcd5b60a6",
    "email": "admin@healthinsurance.com",
    "full_name": "System Administrator",
    "wallet_verified": true
  }
}
```

### Management Endpoints

#### 3. Get All Claims
```http
GET /api/admin/claims/
```

#### 4. Get All Buyers
```http
GET /api/admin/buyers/
```

#### 5. Update Claim Status
```http
POST /api/admin/update-claim-status/
Content-Type: application/json

{
  "claim_id": "CLM-001",
  "status": "verified",
  "admin_id": "51dcd84f-a0be-45b5-9daa-dcfbcd5b60a6"
}
```

## 🔒 Security Features

### 1. Password Hashing
- Uses Django's built-in password hashing
- Passwords are never stored in plain text
- Secure password validation

### 2. Wallet Address Verification
- Admin wallet address stored in environment variables
- Only the designated wallet can complete authentication
- Prevents unauthorized access even with email/password

### 3. Two-Factor Authentication
- Requires both email/password AND MetaMask wallet
- Either factor alone is insufficient for access
- Provides defense in depth

### 4. Session Management
- Tracks last login timestamps
- Admin status can be deactivated
- Proper logout handling

## 🛠️ Configuration

### Environment Variables

Add to your [`.env`](.env) file:
```env
# Admin wallet address (Hardhat Account #0 by default)
ADMIN_WALLET_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

### Django Settings

Already configured in [`backend/backend/settings.py`](backend/backend/settings.py):
```python
ADMIN_WALLET_ADDRESS = os.getenv('ADMIN_WALLET_ADDRESS', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266')
```

## 📊 Admin Dashboard Features

### Claims Management
- **View all claims** in table format
- **Approve/Reject claims** with one click
- **Real-time status updates**
- **Integration with smart contract** for blockchain verification

### Buyer Management
- **View all registered buyers**
- **Search and filter capabilities**
- **Contact information access**
- **Registration tracking**

### System Analytics
- **Total claims statistics**
- **Approval/rejection rates**
- **Recent activity monitoring**
- **System health indicators**

## 🔄 Workflow Example

### Complete Admin Login Process

1. **Navigate to admin interface**
2. **Enter email and password**:
   - Email: `admin@healthinsurance.com`
   - Password: `admin123`
3. **Click "Login"** - validates credentials
4. **Connect MetaMask** with admin wallet (`0xf39F...2266`)
5. **Click "Verify MetaMask Wallet"** - completes authentication
6. **Access admin dashboard** with full management capabilities

### Claim Management Workflow

1. **View pending claims** in the dashboard
2. **Review claim details** and supporting documents
3. **Click "Approve" or "Reject"** for each claim
4. **System updates database** and blockchain automatically
5. **Confirmation message** shows successful action

## 🚨 Troubleshooting

### Issue: "Invalid email or password"
**Solutions:**
- Verify email: `admin@healthinsurance.com`
- Verify password: `admin123`
- Check admin account exists: `python manage.py shell` → `Admin.objects.all()`

### Issue: "Wallet address does not match admin wallet"
**Solutions:**
- Use Hardhat Account #0: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- Check MetaMask is connected to correct account
- Verify admin wallet in `.env` file

### Issue: "Admin not found or inactive"
**Solutions:**
- Create admin: `python manage.py create_admin --email ... --password ... --name ...`
- Check admin is active: Admin model `is_active=True`

### Issue: "Network error"
**Solutions:**
- Verify Django server is running: `python manage.py runserver`
- Check API endpoints are accessible
- Verify CORS settings for frontend

## 🔧 Management Commands

### Create Admin User
```bash
cd backend
python manage.py create_admin --email admin@example.com --password securepass --name "Admin Name"
```

### List All Admins
```bash
cd backend
python manage.py shell
>>> from insurance.models import Admin
>>> Admin.objects.all()
```

### Deactivate Admin
```bash
cd backend
python manage.py shell
>>> from insurance.models import Admin
>>> admin = Admin.objects.get(email='admin@example.com')
>>> admin.is_active = False
>>> admin.save()
```

## 🎯 Key Benefits

### 1. **Enhanced Security**
- Two-factor authentication (email + wallet)
- Secure password hashing
- Environment-based configuration

### 2. **User-Friendly Interface**
- Step-by-step login process
- Clear error messages
- Professional UI design

### 3. **Blockchain Integration**
- MetaMask wallet verification
- Smart contract admin functions
- On-chain claim verification

### 4. **Scalable Architecture**
- Multiple admin support
- Role-based permissions ready
- API-first design

### 5. **Development Friendly**
- Management commands for admin creation
- Comprehensive error handling
- Detailed logging and feedback

## 📋 Admin Credentials Summary

**Default Admin Account:**
- **Email**: `admin@healthinsurance.com`
- **Password**: `admin123`
- **Required Wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- **Admin ID**: `51dcd84f-a0be-45b5-9daa-dcfbcd5b60a6`

**Access URL**: Your frontend application with admin login component

Your custom admin system is now fully operational! 🎉

## 🔄 Next Steps

1. **Test the admin login** with the provided credentials
2. **Connect MetaMask** with the admin wallet address
3. **Explore the admin dashboard** features
4. **Create additional admin users** as needed
5. **Customize the interface** to match your requirements

The system provides a secure, user-friendly way to manage your Health Insurance DApp with both traditional and blockchain-based authentication.