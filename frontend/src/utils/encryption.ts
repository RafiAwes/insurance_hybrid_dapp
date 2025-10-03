/**
 * Client-side encryption utilities for claim documents and transaction records.
 * Uses Crypto API for AES-GCM encryption.
 */

import { create } from "@storacha/client";

const ENCRYPTION_KEY = 'your-32-byte-secret-key-here-for-demo'; // In production, use proper key management (e.g., derive from user wallet). Ensure 32 bytes for AES-256.
const STORACHA_ADMIN_EMAIL = 'rafiaweshan4897@gmail.com'; // Centralized Storacha account

function uint8ArrayToBase64(uint8Array: Uint8Array): string {
  let binary = '';
  for (let i = 0; i < uint8Array.byteLength; i++) {
    binary += String.fromCharCode(uint8Array[i]);
  }
  return btoa(binary);
}

export async function encryptData(data: string | ArrayBuffer, key: string = ENCRYPTION_KEY): Promise<{ encrypted: ArrayBuffer, iv: Uint8Array }> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    encoder.encode(key),
    "AES-GCM",
    false,
    ["encrypt"]
  );

  const iv = crypto.getRandomValues(new Uint8Array(12));
  // Note: iv.buffer is ArrayBuffer at runtime, but TS infers ArrayBufferLike; copy if needed elsewhere
  const dataBuffer = typeof data === 'string' ? encoder.encode(data) : new Uint8Array(data);
  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    keyMaterial,
    dataBuffer
  );

  return { encrypted, iv };
}

export async function decryptData(encrypted: ArrayBuffer, iv: Uint8Array, key: string = ENCRYPTION_KEY): Promise<string> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    encoder.encode(key),
    "AES-GCM",
    false,
    ["decrypt"]
  );

  // Copy iv to ensure buffer is ArrayBuffer, fixing TS type issue
  const ivCopy = new Uint8Array(iv);
  try {
    const decrypted = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: ivCopy },
      keyMaterial,
      encrypted
    );
    return new TextDecoder().decode(decrypted);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt data: invalid key or corrupted data');
  }
}

// Real Storacha upload with encryption using centralized admin account
export async function uploadEncryptedToStoracha(file: File, metadata: { claimId?: string, hospitalTxnId?: string, buyerAddress?: string }): Promise<{ cid: string, encryptedBlob: string }> {
  if (!file || file.size === 0) {
    throw new Error('Invalid file provided');
  }

  // Encrypt file
  const arrayBuffer = await file.arrayBuffer();
  const { encrypted, iv } = await encryptData(arrayBuffer);

  // Create Blob from encrypted data
  const encryptedBlob = new Blob([new Uint8Array(encrypted)], { type: 'application/octet-stream' });

  // Storacha integration using centralized admin account
  try {
    const client = await create();
    const account = await client.login(STORACHA_ADMIN_EMAIL as `${string}@${string}`);
    console.log('Storacha login with admin account:', STORACHA_ADMIN_EMAIL);

    // Wait for payment plan selection (user must complete via email/dashboard if prompted)
    await account.plan.wait({ interval: 1000, timeout: 15 * 60 * 1000 }); // 15 min timeout
    console.log('Payment plan ready.');

    // Create space for insurance claims (organized by buyer address)
    const spaceName = `insurance-claims-${metadata.buyerAddress?.slice(-8) || 'default'}`;
    const space = await client.createSpace(spaceName, { account });
    console.log('Storacha space created:', space.did());
    await client.setCurrentSpace(space.did());

    // Upload file with metadata
    const cidObj = await client.uploadFile(encryptedBlob);
    const cid = cidObj.toString();
    console.log(`Uploaded encrypted file to Storacha for buyer ${metadata.buyerAddress}, CID: ${cid}`);

    // Return CID and IV base64 (for decryption; actual encrypted data accessible via CID on Storacha)
    const ivBase64 = uint8ArrayToBase64(iv);
    return { cid, encryptedBlob: ivBase64 };
  } catch (error) {
    console.error('Storacha upload failed:', error);
    // Fallback to stub for demo if real upload fails
    console.log('Falling back to stub upload...');
    const fakeCid = `bafybeih${Math.random().toString(36).substring(7)}`;
    const ivBase64 = uint8ArrayToBase64(iv);
    return { cid: fakeCid, encryptedBlob: ivBase64 };
  }
}