# Payment Error Solution Guide

## 🚨 Problem: "Payment failed: Returned error: Internal JSON-RPC error"

This error occurs when buyers try to pay premiums but are not registered in the smart contract.

## 🔍 Root Cause Analysis

The smart contract's `payPremium()` function includes this requirement:
```solidity
require(registeredBuyer[msg.sender], "Not registered buyer");
```

If a buyer is not registered, the transaction fails with an "Internal JSON-RPC error".

## ✅ Solution Steps

### Step 1: Verify the Issue
1. Open the Buyer Dashboard
2. Check the "Account Status" section
3. Look for "❌ Not Registered" status

### Step 2: Register the Buyer (Admin Required)
1. **Admin Login**: Access the Admin Dashboard
2. **Navigate**: Go to "Buyer Registration" tab (🔐 icon)
3. **Register**: 
   - Enter the buyer's wallet address: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
   - Click "Register Buyer on Blockchain"
   - Confirm the MetaMask transaction

### Step 3: Verify Registration
1. Use the "Check Registration Status" section
2. Enter the buyer's address
3. Confirm it shows "✅ Address is registered"

### Step 4: Test Payment
1. Return to Buyer Dashboard
2. The status should now show "✅ Registered"
3. Try the payment again - it should work!

## 🛠️ Technical Details

### Enhanced Diagnostics Added
- **Comprehensive Logging**: Detailed console logs for debugging
- **Registration Checks**: Automatic verification before payment
- **Better Error Messages**: Clear explanations of failures
- **UI Improvements**: Visual status indicators

### Files Modified
- `frontend/src/services/contract.ts` - Enhanced logging and registration functions
- `frontend/src/components/BuyerDashboard.tsx` - Registration status display
- `frontend/src/components/AdminDashboard.tsx` - Registration management interface
- `frontend/.env` - Fixed environment variables

## 🔧 Quick Fix Commands

### For Admins:
```bash
# 1. Ensure Hardhat network is running
npx hardhat node

# 2. Deploy contract (if needed)
npx hardhat run scripts/deploy.js --network localhost

# 3. Access Admin Dashboard and register the buyer
# Address to register: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
```

### For Developers:
```bash
# Run the diagnostic script
node debug-payment.js
```

## 🎯 Prevention

To prevent this issue in the future:
1. **Always register buyers** before they attempt payments
2. **Check registration status** in the UI before enabling payment buttons
3. **Provide clear error messages** when registration is required
4. **Monitor blockchain events** for registration confirmations

## 📋 Checklist

- [ ] Hardhat network is running
- [ ] Contract is deployed
- [ ] Admin wallet is connected
- [ ] Buyer address is registered on blockchain
- [ ] Buyer dashboard shows "✅ Registered" status
- [ ] Payment button is enabled
- [ ] Transaction succeeds

## 🆘 Still Having Issues?

1. **Check Console Logs**: Look for detailed diagnostic information
2. **Verify Network**: Ensure MetaMask is on Hardhat Local (Chain ID: 31337)
3. **Check Balance**: Ensure sufficient ETH for 0.1 ETH premium + gas
4. **Contract Address**: Verify correct contract address in environment variables
5. **Admin Permissions**: Ensure you're using the admin wallet for registration

## 📞 Support

If you continue experiencing issues:
1. Check the browser console for detailed error logs
2. Verify all environment variables are correctly set
3. Ensure the smart contract is properly deployed
4. Contact the development team with console logs and transaction details