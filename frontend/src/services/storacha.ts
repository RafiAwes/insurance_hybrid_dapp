/**
 * Storacha service for frontend integration
 * Handles automatic login and session management
 */

import { create } from "@storacha/client";

// Use only the specific email provided
const STORACHA_ADMIN_EMAIL = 'rafiaweshan4897@gmail.com';
// Use the specific space DID provided
const SPACE_DID = 'did:key:z6Mks2sfn2CcTcEXho661oVoB26hwjd4NdAR1UQ1JiHVdKPZ';

// Store Storacha client and account in memory
let storachaClient: any = null;
let storachaAccount: any = null;

/**
 * Login to Storacha with the specific admin email
 * @returns Promise<boolean> - Whether login was successful
 */
export async function loginToStoracha(): Promise<boolean> {
  try {
    console.log(`🔐 Logging into Storacha with email: ${STORACHA_ADMIN_EMAIL}`);
    
    // Create client
    storachaClient = await create();
    
    // Login with the specific email
    storachaAccount = await storachaClient.login(STORACHA_ADMIN_EMAIL as `${string}@${string}`);
    
    console.log('✅ Storacha login successful');
    return true;
  } catch (error) {
    console.error('❌ Storacha login failed:', error);
    storachaClient = null;
    storachaAccount = null;
    return false;
  }
}

/**
 * Check if user is logged into Storacha
 * @returns boolean - Whether user is logged in
 */
export function isStorachaLoggedIn(): boolean {
  return storachaClient !== null && storachaAccount !== null;
}

/**
 * Get Storacha client and account
 * @returns Object with client and account, or null if not logged in
 */
export function getStorachaSession() {
  if (!isStorachaLoggedIn()) {
    return null;
  }
  return {
    client: storachaClient,
    account: storachaAccount
  };
}

/**
 * Initialize Storacha session (call this on app startup or login)
 */
export async function initStorachaSession() {
  // Try to login with the specific admin account
  const success = await loginToStoracha();
  return success;
}

/**
 * Upload data to Storacha using the specific space
 * @param data - Data to upload (string or Blob)
 * @param metadata - Optional metadata
 * @returns Promise<string> - CID of uploaded data
 */
export async function uploadToStoracha(data: string | Blob, metadata?: Record<string, any>): Promise<string> {
  if (!isStorachaLoggedIn()) {
    const loginSuccess = await loginToStoracha();
    if (!loginSuccess) {
      throw new Error('Failed to login to Storacha');
    }
  }

  try {
    const session = getStorachaSession();
    if (!session) {
      throw new Error('No Storacha session available');
    }

    const { client, account } = session;

    // Wait for payment plan selection (user must complete via email/dashboard if prompted)
    await account.plan.wait({ interval: 1000, timeout: 15 * 60 * 1000 }); // 15 min timeout
    console.log('Payment plan ready.');

    // Create space for insurance claims (using fixed name)
    const spaceName = 'health-insurance-space';
    const space = await client.createSpace(spaceName, { account });
    console.log('Storacha space created:', space.did());
    
    await client.setCurrentSpace(space.did());

    // Convert data to Blob if it's a string
    const blob = typeof data === 'string' ? new Blob([data], { type: 'application/json' }) : data;

    // Upload file with metadata
    const cidObj = await client.uploadFile(blob);
    const cid = cidObj.toString();
    console.log(`Uploaded data to Storacha, CID: ${cid}`);

    return cid;
  } catch (error) {
    console.error('Storacha upload failed:', error);
    throw error;
  }
}

// Initialize Storacha session when module is loaded
initStorachaSession().then(success => {
  if (success) {
    console.log('✅ Storacha session initialized successfully');
  } else {
    console.log('❌ Failed to initialize Storacha session');
  }
}).catch(error => {
  console.error('Error initializing Storacha session:', error);
});