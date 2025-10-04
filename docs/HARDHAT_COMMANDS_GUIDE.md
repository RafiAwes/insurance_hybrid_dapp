# Hardhat Commands Guide for Hybrid Insurance DApp

## ❌ Common Mistake
**DON'T RUN**: `npx hardhat init` 
- Your project already has Hardhat configured
- This command is only for creating new Hardhat projects
- Running it in an existing project will show error HH23

## ✅ Correct Commands to Use

### 1. Install Dependencies First
```bash
# Install root project dependencies (includes Hardhat)
npm install

# This will install all the dependencies from package.json including:
# - hardhat
# - @nomicfoundation/hardhat-toolbox
# - ethers
# - chai, etc.
```

### 2. Compile Smart Contracts
```bash
# Compile all contracts in the contracts/ directory
npx hardhat compile

# This will:
# - Compile HealthInsurance.sol
# - Generate ABI and bytecode
# - Create artifacts/ directory
# - Output: artifacts/contracts/HealthInsurance.sol/HealthInsurance.json
```

### 3. Start Local Blockchain (Optional)
```bash
# Start Hardhat's local blockchain network
npx hardhat node

# This will:
# - Start a local Ethereum network on http://127.0.0.1:8545
# - Create 20 test accounts with 10,000 ETH each
# - Show account addresses and private keys
# - Keep running until you stop it (Ctrl+C)
```

### 4. Deploy Smart Contract
```bash
# Deploy to local network (make sure hardhat node is running)
npx hardhat run scripts/deploy.js --network localhost

# Or deploy to Hardhat's built-in network (no need to run hardhat node)
npx hardhat run scripts/deploy.js

# This will:
# - Deploy HealthInsurance contract
# - Show the deployed contract address
# - You'll need this address for your .env file
```

### 5. Run Tests
```bash
# Run all tests in test/ directory
npx hardhat test

# Run specific test file
npx hardhat test test/HealthInsurance.test.js
```

### 6. Other Useful Commands
```bash
# Clean compiled artifacts
npx hardhat clean

# Show available tasks
npx hardhat help

# Check Hardhat version
npx hardhat --version

# Verify contract (for testnets/mainnet)
npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS
```

## Step-by-Step Workflow

### Step 1: Install Dependencies
```bash
npm install
```

### Step 2: Compile Contracts
```bash
npx hardhat compile
```
**Expected Output:**
```
Compiling 1 file with 0.8.20
Compilation finished successfully
```

### Step 3: Deploy Contract
```bash
# Option A: Deploy to built-in Hardhat network
npx hardhat run scripts/deploy.js

# Option B: Deploy to local node (run 'npx hardhat node' first)
npx hardhat run scripts/deploy.js --network localhost
```

**Expected Output:**
```
HealthInsurance deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### Step 4: Update Environment Variables
```bash
# Copy the deployed contract address and update .env
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### Step 5: Extract ABI for Django
```bash
# View the generated ABI
cat artifacts/contracts/HealthInsurance.sol/HealthInsurance.json | grep -A 1000 '"abi":'
```

## Troubleshooting

### Error: "Cannot find module '@nomicfoundation/hardhat-toolbox'"
**Solution:**
```bash
npm install @nomicfoundation/hardhat-toolbox --save-dev
```

### Error: "HH23: You are trying to initialize a project inside an existing Hardhat project"
**Solution:** Don't run `npx hardhat init`. Your project is already initialized.

### Error: "Cannot find module 'hardhat'"
**Solution:**
```bash
npm install hardhat --save-dev
```

### Error: "No contracts to compile"
**Solution:** Make sure you have contracts in the `contracts/` directory.

### Error: "Cannot connect to network"
**Solution:** 
- For localhost network: Make sure `npx hardhat node` is running
- For built-in network: Use `npx hardhat run scripts/deploy.js` without `--network`

## Current Project Status

✅ **Hardhat Config**: Already configured in `hardhat.config.js`  
✅ **Smart Contract**: `contracts/HealthInsurance.sol` exists  
✅ **Deploy Script**: `scripts/deploy.js` exists  
✅ **Test File**: `test/HealthInsurance.test.js` exists  
⚠️ **Dependencies**: Need to run `npm install`  
⚠️ **Compilation**: Need to run `npx hardhat compile`  
⚠️ **Deployment**: Need to deploy and get contract address  

## Next Steps

1. **Install dependencies**: `npm install`
2. **Compile contracts**: `npx hardhat compile`
3. **Deploy contract**: `npx hardhat run scripts/deploy.js`
4. **Update .env**: Add the deployed contract address
5. **Update Django views**: Replace temporary ABI with full ABI from artifacts

Your Django server is already working! These steps will complete the blockchain integration.