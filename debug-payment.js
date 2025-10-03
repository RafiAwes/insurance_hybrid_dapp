#!/usr/bin/env node

/**
 * Payment Debugging Script
 * This script helps diagnose the "Internal JSON-RPC error" payment issue
 */

const { Web3 } = require('web3');
const fs = require('fs');
const path = require('path');

// Configuration
const RPC_URL = 'http://127.0.0.1:8545';
const CONTRACT_ADDRESS = '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512';

// Contract ABI (minimal for testing)
const CONTRACT_ABI = [
  {
    "inputs": [],
    "name": "payPremium",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "registeredBuyer",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "buyer",
        "type": "address"
      }
    ],
    "name": "registerBuyer",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];

async function runDiagnostics() {
  console.log('🔍 Starting Payment Diagnostics...\n');

  try {
    // 1. Test RPC Connection
    console.log('1️⃣ Testing RPC Connection...');
    const web3 = new Web3(RPC_URL);
    
    try {
      const blockNumber = await web3.eth.getBlockNumber();
      console.log('✅ RPC Connection successful');
      console.log(`   Current block: ${blockNumber}`);
    } catch (error) {
      console.log('❌ RPC Connection failed:', error.message);
      console.log('   → Make sure Hardhat network is running: npx hardhat node');
      return;
    }

    // 2. Check Network ID
    console.log('\n2️⃣ Checking Network...');
    const chainId = await web3.eth.getChainId();
    console.log(`✅ Chain ID: ${chainId} (${chainId === 31337n ? 'Hardhat Local' : 'Unknown'})`);

    // 3. Get Accounts
    console.log('\n3️⃣ Getting Accounts...');
    const accounts = await web3.eth.getAccounts();
    if (accounts.length === 0) {
      console.log('❌ No accounts available');
      return;
    }
    console.log(`✅ Found ${accounts.length} accounts`);
    console.log(`   Primary account: ${accounts[0]}`);

    // 4. Check Account Balance
    console.log('\n4️⃣ Checking Account Balance...');
    const balance = await web3.eth.getBalance(accounts[0]);
    const balanceEth = web3.utils.fromWei(balance, 'ether');
    console.log(`✅ Balance: ${balanceEth} ETH`);
    
    if (parseFloat(balanceEth) < 0.1) {
      console.log('⚠️  Warning: Balance might be insufficient for 0.1 ETH premium + gas');
    }

    // 5. Test Contract Connection
    console.log('\n5️⃣ Testing Contract Connection...');
    const contract = new web3.eth.Contract(CONTRACT_ABI, CONTRACT_ADDRESS);
    
    try {
      // Try to call a view function
      const isRegistered = await contract.methods.registeredBuyer(accounts[0]).call();
      console.log('✅ Contract connection successful');
      console.log(`   Buyer registered: ${isRegistered}`);
      
      if (!isRegistered) {
        console.log('❌ CRITICAL: Buyer is not registered!');
        console.log('   → This is likely the cause of the payment failure');
        console.log('   → Admin needs to call registerBuyer() first');
        
        // Try to register if we're using the admin account
        console.log('\n6️⃣ Attempting to register buyer...');
        try {
          const tx = await contract.methods.registerBuyer(accounts[0]).send({
            from: accounts[0],
            gas: '100000'
          });
          console.log('✅ Buyer registered successfully!');
          console.log(`   Transaction hash: ${tx.transactionHash}`);
        } catch (regError) {
          console.log('❌ Registration failed:', regError.message);
          console.log('   → You might not be the admin, or contract is not deployed');
        }
      }
    } catch (contractError) {
      console.log('❌ Contract connection failed:', contractError.message);
      console.log('   → Contract might not be deployed at this address');
      console.log('   → Run: npx hardhat run scripts/deploy.js --network localhost');
      return;
    }

    // 6. Test Gas Estimation
    console.log('\n7️⃣ Testing Gas Estimation...');
    try {
      const gasEstimate = await contract.methods.payPremium().estimateGas({
        from: accounts[0],
        value: web3.utils.toWei('0.1', 'ether')
      });
      console.log(`✅ Gas estimation successful: ${gasEstimate}`);
    } catch (gasError) {
      console.log('❌ Gas estimation failed:', gasError.message);
      console.log('   → This indicates the transaction will fail');
    }

    // 7. Test Actual Payment (if registered)
    const finalRegistrationCheck = await contract.methods.registeredBuyer(accounts[0]).call();
    if (finalRegistrationCheck) {
      console.log('\n8️⃣ Testing Payment Transaction...');
      try {
        const tx = await contract.methods.payPremium().send({
          from: accounts[0],
          value: web3.utils.toWei('0.1', 'ether'),
          gas: '300000'
        });
        console.log('✅ Payment successful!');
        console.log(`   Transaction hash: ${tx.transactionHash}`);
      } catch (paymentError) {
        console.log('❌ Payment failed:', paymentError.message);
        console.log('   → This is the actual error causing the issue');
      }
    }

  } catch (error) {
    console.log('❌ Diagnostic failed:', error.message);
  }

  console.log('\n🏁 Diagnostics complete!');
}

// Run diagnostics
runDiagnostics().catch(console.error);