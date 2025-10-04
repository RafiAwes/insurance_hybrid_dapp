#!/usr/bin/env node

// Storacha client service for Node.js
// This script is called by the Python backend to interact with Storacha

const fs = require('fs');
const path = require('path');

// Check if @storacha/client is available
let storachaClient;
try {
  storachaClient = require('@storacha/client');
} catch (error) {
  console.error('⚠️  @storacha/client not found. Please install it with: npm install @storacha/client');
  process.exit(1);
}

async function loginToStoracha(email) {
  try {
    console.log(`🔐 Logging into Storacha with email: ${email}`);
    const client = await storachaClient.create();
    const account = await client.login(email);
    console.log('✅ Storacha login successful');
    return { client, account, success: true, message: 'Storacha login successful' };
  } catch (error) {
    console.error('❌ Storacha login failed:', error.message);
    return { success: false, error: error.message };
  }
}

async function getOrCreateSpace(client, account, spaceDid) {
  try {
    console.log(`📂 Getting or creating space with DID: ${spaceDid}`);
    
    // Wait for payment plan (if needed)
    await account.plan.wait({ interval: 1000, timeout: 15 * 60 * 1000 });
    
    // Try to get existing space first
    try {
      const space = await client.getSpace(spaceDid);
      console.log(`✅ Found existing space: ${spaceDid}`);
      return space;
    } catch (error) {
      // Space doesn't exist, create new one with the specific DID
      console.log(`🆕 Creating new space with DID: ${spaceDid}`);
      const space = await client.createSpace('health-insurance-space', { account, did: spaceDid });
      console.log(`✅ Space created: ${space.did()}`);
      return space;
    }
  } catch (error) {
    console.error('❌ Space creation/get failed:', error.message);
    throw error;
  }
}

async function uploadDataToStoracha(client, space, data) {
  try {
    console.log('📤 Uploading data to Storacha');
    
    // Set current space
    await client.setCurrentSpace(space.did());
    
    // Convert data to JSON string
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    
    // Upload file
    const cidObj = await client.uploadFile(blob);
    const cid = cidObj.toString();
    
    console.log(`✅ Data uploaded successfully. CID: ${cid}`);
    return cid;
  } catch (error) {
    console.error('❌ Data upload failed:', error.message);
    throw error;
  }
}

async function handleLogin(data) {
  try {
    const { email } = data;
    const result = await loginToStoracha(email);
    return result;
  } catch (error) {
    console.error('❌ Login failed:', error.message);
    return { success: false, error: error.message };
  }
}

async function uploadClaimData(data) {
  try {
    const { adminEmail, spaceDid, buyer, claim } = data;
    
    // Login to Storacha
    const loginResult = await loginToStoracha(adminEmail);
    if (!loginResult.success) {
      throw new Error(loginResult.error);
    }
    
    const { client, account } = loginResult;
    
    // Get or create space with specific DID
    const space = await getOrCreateSpace(client, account, spaceDid);
    
    // Prepare data structure
    const uploadData = {
      type: 'claim',
      buyer: {
        id: buyer.id,
        full_name: buyer.full_name,
        email: buyer.email,
        wallet_address: buyer.wallet_address,
        national_id: buyer.national_id
      },
      claim: {
        claim_id: claim.claim_id,
        amount: claim.amount,
        status: claim.status,
        description: claim.description,
        created_at: claim.created_at
      },
      uploaded_at: new Date().toISOString()
    };
    
    // Upload data
    const cid = await uploadDataToStoracha(client, space, uploadData);
    
    return { cid };
  } catch (error) {
    console.error('❌ Claim upload failed:', error.message);
    throw error;
  }
}

async function uploadPremiumData(data) {
  try {
    const { adminEmail, spaceDid, buyer, premium } = data;
    
    // Login to Storacha
    const loginResult = await loginToStoracha(adminEmail);
    if (!loginResult.success) {
      throw new Error(loginResult.error);
    }
    
    const { client, account } = loginResult;
    
    // Get or create space with specific DID
    const space = await getOrCreateSpace(client, account, spaceDid);
    
    // Prepare data structure
    const uploadData = {
      type: 'premium',
      buyer: {
        id: buyer.id,
        full_name: buyer.full_name,
        email: buyer.email,
        wallet_address: buyer.wallet_address,
        national_id: buyer.national_id
      },
      premium: {
        transaction_hash: premium.transaction_hash,
        amount_eth: premium.amount_eth,
        block_timestamp: premium.block_timestamp,
        status: premium.status
      },
      uploaded_at: new Date().toISOString()
    };
    
    // Upload data
    const cid = await uploadDataToStoracha(client, space, uploadData);
    
    return { cid };
  } catch (error) {
    console.error('❌ Premium upload failed:', error.message);
    throw error;
  }
}

// Main function
async function main() {
  try {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
      console.error('Usage: node storacha_client.js <operation> <data_file>');
      process.exit(1);
    }
    
    const operation = args[0];
    const dataFilePath = args[1];
    
    // Read data from file
    const data = JSON.parse(fs.readFileSync(dataFilePath, 'utf8'));
    
    let result;
    
    switch (operation) {
      case 'login':
        result = await handleLogin(data);
        break;
      case 'upload_claim':
        result = await uploadClaimData(data);
        break;
      case 'upload_premium':
        result = await uploadPremiumData(data);
        break;
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
    
    // Output result as JSON
    console.log(JSON.stringify(result));
  } catch (error) {
    console.error('❌ Storacha client error:', error.message);
    process.exit(1);
  }
}

// Run main function if this script is executed directly
if (require.main === module) {
  main();
}