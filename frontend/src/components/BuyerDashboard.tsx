import React, { useState } from 'react';
import { payPremiumOnChain } from '../services/contract';
import { uploadEncryptedToStoracha } from '../utils/encryption';

export default function BuyerDashboard() {
  const [premiumStatus, setPremiumStatus] = useState('');
  const [claimStatus, setClaimStatus] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState('');

  const handlePayPremium = async () => {
    try {
      setPremiumStatus('Processing...');
      await payPremiumOnChain();
      setPremiumStatus('Premium paid successfully!');
    } catch (error) {
      setPremiumStatus('Payment failed: ' + (error as Error).message);
    }
  };

  const handleSubmitClaim = async () => {
    if (!file || !email) {
      setClaimStatus('Please select a file and enter your email');
      return;
    }
    try {
      setClaimStatus('Submitting claim...');
      const metadata = { claimId: 'claim-' + Date.now() };
      const { cid } = await uploadEncryptedToStoracha(file, metadata, email);
      // TODO: Call submitClaimOnChain with amount, claimId, hospitalTxnId
      setClaimStatus(`Claim submitted with CID: ${cid}. Check email for Storacha confirmation if first time.`);
    } catch (error) {
      setClaimStatus('Claim submission failed: ' + (error as Error).message);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Buyer Dashboard</h2>
      
      <div className="card bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Pay Monthly Premium</h3>
        <button 
          onClick={handlePayPremium}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded"
        >
          Pay 0.1 ETH Premium
        </button>
        {premiumStatus && <p className="mt-2">{premiumStatus}</p>}
      </div>

      <div className="card bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Submit Claim</h3>
        <input
          type="email"
          placeholder="Enter your email for Storacha login"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mb-4 p-2 border rounded w-full"
        />
        <input
          type="file"
          accept=".pdf,image/*"
          onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
          className="mb-4 p-2 border rounded w-full"
        />
        <button
          onClick={handleSubmitClaim}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
          disabled={!file || !email}
        >
          Submit Claim with Document
        </button>
        {claimStatus && <p className="mt-2">{claimStatus}</p>}
      </div>
    </div>
  );
}