# How to Access Admin Login Page - Step by Step Guide

## 🚀 Quick Access Instructions

### Step 1: Start the Frontend Application
```bash
cd frontend
npm run dev
```

### Step 2: Open Your Browser
Navigate to the frontend URL (usually `http://localhost:5173` or `http://localhost:3000`)

### Step 3: Switch to Admin Mode
1. **Look for the toggle buttons** in the header
2. **Click "🛡️ Admin"** button (next to "👤 Buyer")
3. **Admin login page will appear**

## 🔐 Admin Login Process

### Phase 1: Email/Password Authentication

**Login Form Fields:**
- **Email**: `admin@healthinsurance.com`
- **Password**: `admin123`

**Steps:**
1. Enter the email address
2. Enter the password
3. Click "Login" button
4. System validates credentials

### Phase 2: MetaMask Wallet Verification

**Required Wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

**Steps:**
1. **Connect MetaMask** with the admin wallet address
2. **Click "🦊 Verify MetaMask Wallet"**
3. **System verifies** wallet address matches admin wallet
4. **Access granted** to admin dashboard

## 🖥️ Visual Interface Guide

### Main App Header
```
🏥 Health Insurance DApp    [👤 Buyer] [🛡️ Admin]    [Connect MetaMask] [Logout]
```

### Admin Login Page Layout
```
🛡️ Admin Login
Health Insurance DApp Administration

┌─────────────────────────────────┐
│ Email Address                   │
│ [admin@healthinsurance.com    ] │
│                                 │
│ Password                        │
│ [admin123                     ] │
│                                 │
│ [        Login        ]         │
└─────────────────────────────────┘

Admin access requires both email/password and MetaMask wallet verification
```

### After Email Login Success
```
✅ Email Verified
Welcome, System Administrator!
admin@healthinsurance.com

🦊 Wallet Verification Required
Please connect with the admin MetaMask wallet to complete authentication.
Required wallet: 0xf39F...2266 (Hardhat Account #0)

[🦊 Verify MetaMask Wallet]

← Back to Login
```

## 🔧 Setup Requirements

### 1. Backend Must Be Running
```bash
cd backend
python manage.py runserver
# Should show: Starting development server at http://127.0.0.1:8000/
```

### 2. Frontend Must Be Running
```bash
cd frontend
npm run dev
# Should show: Local: http://localhost:5173/
```

### 3. Admin Account Must Exist
```bash
cd backend
python manage.py create_admin --email admin@healthinsurance.com --password admin123 --name "System Administrator"
# Should show: Successfully created admin: admin@healthinsurance.com
```

### 4. MetaMask Setup
- **Install MetaMask** browser extension
- **Import Hardhat Account #0**:
  - Private Key: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
  - Address: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

## 🌐 Access URLs

### Direct Frontend Access
- **Main App**: `http://localhost:5173/` (or your frontend URL)
- **Click "🛡️ Admin"** in the header to switch to admin mode

### API Endpoints (for testing)
- **Admin Login**: `POST http://localhost:8000/api/admin/login/`
- **Wallet Verify**: `POST http://localhost:8000/api/admin/verify-wallet/`

## 🎯 Complete Access Flow

### 1. Open Frontend Application
```
Browser → http://localhost:5173/
```

### 2. Switch to Admin Mode
```
Click: [🛡️ Admin] button in header
```

### 3. Admin Login Form Appears
```
Email: admin@healthinsurance.com
Password: admin123
Click: [Login]
```

### 4. Wallet Verification Screen
```
Connect MetaMask with: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Click: [🦊 Verify MetaMask Wallet]
```

### 5. Admin Dashboard Access
```
✅ Full admin access granted
- Claims Management
- Buyer Management  
- System Analytics
```

## 🐛 Troubleshooting Access Issues

### Issue: Can't see Admin button
**Solution**: Make sure the App.tsx has been updated with the admin toggle

### Issue: Admin login page not loading
**Solutions**:
1. **Check frontend is running**: `npm run dev`
2. **Verify App.tsx imports**: AdminLogin component imported
3. **Check browser console** for errors

### Issue: "Invalid email or password"
**Solutions**:
1. **Use correct credentials**: `admin@healthinsurance.com` / `admin123`
2. **Check admin exists**: `python manage.py shell` → `Admin.objects.all()`
3. **Create admin if missing**: `python manage.py create_admin ...`

### Issue: "Wallet address does not match"
**Solutions**:
1. **Use correct wallet**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
2. **Check MetaMask account**: Switch to Hardhat Account #0
3. **Verify .env config**: `ADMIN_WALLET_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

### Issue: Network errors
**Solutions**:
1. **Check Django server**: `python manage.py runserver`
2. **Verify API endpoints**: Test with curl or Postman
3. **Check CORS settings**: Ensure frontend can access backend

## 📋 Quick Checklist

### Before Accessing Admin:
- [ ] Django backend running (`python manage.py runserver`)
- [ ] Frontend running (`npm run dev`)
- [ ] Admin account created (`python manage.py create_admin ...`)
- [ ] MetaMask installed and configured
- [ ] Hardhat Account #0 imported to MetaMask

### Access Steps:
- [ ] Open frontend in browser
- [ ] Click "🛡️ Admin" button in header
- [ ] Enter email: `admin@healthinsurance.com`
- [ ] Enter password: `admin123`
- [ ] Click "Login"
- [ ] Connect MetaMask with admin wallet
- [ ] Click "🦊 Verify MetaMask Wallet"
- [ ] Access admin dashboard

## 🎉 Success Indicators

### ✅ Successful Email Login
```
✅ Email Verified
Welcome, System Administrator!
admin@healthinsurance.com
```

### ✅ Successful Wallet Verification
```
Admin Dashboard appears with:
- 📋 Claims Management tab
- 👥 Buyers tab  
- 📊 Analytics tab
```

### ✅ Full Admin Access
```
Header shows: "Welcome, System Administrator"
Footer shows: "Admin: admin@healthinsurance.com | Wallet Verified: ✅"
```

## 🔄 Alternative Access Methods

### Method 1: Direct Component Testing
If you want to test the AdminLogin component directly:

```typescript
// Temporarily modify App.tsx to show AdminLogin directly
return <AdminLogin onAdminLogin={handleAdminLogin} />;
```

### Method 2: URL-Based Routing (Future Enhancement)
Consider adding React Router for URL-based admin access:

```bash
npm install react-router-dom
# Then add routes like /admin, /buyer, etc.
```

## 📞 Support

If you still can't access the admin login page:

1. **Check browser console** for JavaScript errors
2. **Verify all files** are saved and updated
3. **Restart frontend server**: `npm run dev`
4. **Check network tab** for API call failures
5. **Test backend endpoints** directly with curl

Your custom admin system is ready! Simply click the "🛡️ Admin" button in your frontend header to access the admin login page. 🎉