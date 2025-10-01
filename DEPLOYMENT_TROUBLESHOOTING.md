# Deployment Script Fix - Troubleshooting Guide

## ❌ Original Error

```
TypeError: deployer.getBalance is not a function
    at main (F:\web3\hybrid_Insurance _reviced\scripts\deploy.js:7:51)
```

## 🔍 Root Cause Analysis

The error occurred because:

1. **Ethers.js Version Compatibility**: The original script used `deployer.getBalance()` which is not available on the signer object in newer versions of Ethers.js
2. **Incorrect Method Call**: The balance should be fetched using `provider.getBalance(address)` instead of `signer.getBalance()`
3. **Missing Error Handling**: No fallback for when balance fetching fails

## ✅ Fixed Deployment Script

### Key Changes Made:

1. **Fixed Balance Fetching**:
   ```javascript
   // ❌ Old (broken)
   console.log("Account balance:", (await deployer.getBalance()).toString());
   
   // ✅ New (working)
   const balance = await deployer.provider.getBalance(deployer.address);
   console.log("Account balance:", ethers.formatEther(balance), "ETH");
   ```

2. **Added Error Handling**:
   ```javascript
   try {
     const balance = await deployer.provider.getBalance(deployer.address);
     console.log("Account balance:", ethers.formatEther(balance), "ETH");
   } catch (error) {
     console.log("Could not fetch balance:", error.message);
   }
   ```

3. **Enhanced Deployment Info**:
   ```javascript
   // Save deployment details to file
   const deploymentInfo = {
     contractAddress: contractAddress,
     deployerAddress: deployer.address,
     network: hre.network.name,
     timestamp: new Date().toISOString(),
     transactionHash: healthInsurance.deploymentTransaction().hash
   };
   
   fs.writeFileSync('deployment-info.json', JSON.stringify(deploymentInfo, null, 2));
   ```

4. **Better Console Output**:
   ```javascript
   console.log(`🎉 Deployment successful!`);
   console.log(`📋 Contract Address: ${contractAddress}`);
   console.log(`📝 Update your .env file with:`);
   console.log(`   CONTRACT_ADDRESS=${contractAddress}`);
   ```

## 🚀 How to Use the Fixed Script

### Step 1: Compile Contracts
```bash
npx hardhat compile
```

### Step 2: Start Local Network (Optional)
```bash
# Terminal 1: Start Hardhat node
npx hardhat node
```

### Step 3: Deploy Contract
```bash
# Option A: Deploy to built-in Hardhat network
npx hardhat run scripts/deploy.js

# Option B: Deploy to localhost network (if hardhat node is running)
npx hardhat run scripts/deploy.js --network localhost
```

### Expected Output:
```
Deploying contracts with the account: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Account balance: 10000.0 ETH
Deploying HealthInsurance contract...
HealthInsurance deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
Transaction hash: 0x...
Deployment completed successfully!
Deployment info saved to deployment-info.json

🎉 Deployment successful!
📋 Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
📝 Update your .env file with:
   CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

## 📁 Generated Files

After successful deployment, you'll get:

### 1. `deployment-info.json`
```json
{
  "contractAddress": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
  "deployerAddress": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
  "network": "localhost",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "transactionHash": "0x..."
}
```

### 2. `artifacts/` Directory
```
artifacts/
├── contracts/
│   └── HealthInsurance.sol/
│       ├── HealthInsurance.json  # Contains ABI and bytecode
│       └── HealthInsurance.dbg.json
└── ...
```

## 🔧 Next Steps After Deployment

### 1. Update Environment Variables
```bash
# Copy the contract address from deployment output
# Update .env file:
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### 2. Extract Full ABI for Django
```bash
# View the ABI
cat artifacts/contracts/HealthInsurance.sol/HealthInsurance.json | jq '.abi'

# Or use Node.js to extract it
node -e "
const artifact = require('./artifacts/contracts/HealthInsurance.sol/HealthInsurance.json');
console.log(JSON.stringify(artifact.abi, null, 2));
"
```

### 3. Update Django Views with Full ABI
Replace the temporary minimal ABI in [`backend/insurance/views.py`](backend/insurance/views.py) with the full ABI from the artifacts.

### 4. Test Contract Integration
```bash
# Restart Django server to pick up new contract address
cd backend
python manage.py runserver
```

## 🐛 Common Issues & Solutions

### Issue: "Cannot find module 'hardhat'"
**Solution:**
```bash
npm install
```

### Issue: "Error HH8: There's one or more errors in your config file"
**Solution:** Check `hardhat.config.js` syntax and ensure all required plugins are installed.

### Issue: "Network localhost not found"
**Solution:** Make sure `npx hardhat node` is running in another terminal.

### Issue: "Insufficient funds for intrinsic transaction cost"
**Solution:** 
- Use the built-in Hardhat network: `npx hardhat run scripts/deploy.js`
- Or ensure your local node has funded accounts

### Issue: "Contract creation code storage out of gas"
**Solution:** The contract is too large. This shouldn't happen with the HealthInsurance contract, but if it does, optimize the contract code.

## 🔄 Alternative Deployment Methods

### Method 1: Using Hardhat Console
```bash
npx hardhat console --network localhost

# In console:
const HealthInsurance = await ethers.getContractFactory("HealthInsurance");
const healthInsurance = await HealthInsurance.deploy();
await healthInsurance.waitForDeployment();
console.log("Deployed to:", await healthInsurance.getAddress());
```

### Method 2: Using Hardhat Ignition (Advanced)
```bash
# Install Hardhat Ignition
npm install --save-dev @nomicfoundation/hardhat-ignition-ethers

# Create ignition module and deploy
npx hardhat ignition deploy ignition/modules/HealthInsurance.js
```

## 📊 Deployment Verification

### Verify Contract on Blockchain
```bash
# Check if contract exists
npx hardhat console --network localhost

# In console:
const code = await ethers.provider.getCode("0x5FbDB2315678afecb367f032d93F642f64180aa3");
console.log("Contract code length:", code.length);
// Should be > 2 (more than just "0x")
```

### Test Contract Functions
```bash
# In Hardhat console:
const HealthInsurance = await ethers.getContractFactory("HealthInsurance");
const contract = HealthInsurance.attach("0x5FbDB2315678afecb367f032d93F642f64180aa3");
const admin = await contract.admin();
console.log("Contract admin:", admin);
```

## 🎯 Integration with Django

Once deployed successfully:

1. **Update .env**: Add the contract address
2. **Update views.py**: Replace temporary ABI with full ABI
3. **Restart Django**: `python manage.py runserver`
4. **Test API endpoints**: Verify contract integration works

The deployment script is now robust and should handle various edge cases gracefully while providing clear feedback about the deployment process.