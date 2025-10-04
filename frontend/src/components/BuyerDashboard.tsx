import React, { useState, useEffect } from 'react';
import { payPremiumOnChain, checkBuyerRegistration } from '../services/contract';
import { uploadEncryptedToStoracha } from '../utils/encryption';
import { getAccount } from '../services/web3';

export default function BuyerDashboard() {
  const [premiumStatus, setPremiumStatus] = useState('');
  const [claimStatus, setClaimStatus] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isRegistered, setIsRegistered] = useState<boolean | null>(null);
  const [currentAccount, setCurrentAccount] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [claimHistory, setClaimHistory] = useState<any[]>([]);
  const [premiumHistory, setPremiumHistory] = useState<any[]>([]);
  
  useEffect(() => {
    checkRegistrationStatus();
  }, []);

  const checkRegistrationStatus = async () => {
    try {
      setIsLoading(true);
      const account = await getAccount();
      if (account) {
        setCurrentAccount(account);
        const registered = await checkBuyerRegistration(account);
        setIsRegistered(registered);
      }
    } catch (error) {
      console.error('Error checking registration:', error);
      setIsRegistered(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePayPremium = async () => {
    try {
      setPremiumStatus('Processing payment...');
      
      if (!isRegistered) {
        setPremiumStatus('❌ Error: You are not registered as a buyer. Please contact admin to register your address: ' + currentAccount);
        return;
      }
      
      await payPremiumOnChain();
      setPremiumStatus('✅ Premium paid successfully!');
    } catch (error: any) {
      console.error('Payment error:', error);
      
      let errorMessage = 'Payment failed: ';
      if (error?.message?.includes('Internal JSON-RPC error')) {
        errorMessage += 'Internal JSON-RPC error. Check console for detailed logs.';
      } else if (error?.message?.includes('insufficient funds')) {
        errorMessage += 'Insufficient funds. You need at least 0.1 ETH plus gas fees.';
      } else if (error?.message?.includes('User denied')) {
        errorMessage += 'Transaction was rejected by user.';
      } else {
        errorMessage += error?.message || 'Unknown error occurred';
      }
      
      setPremiumStatus('❌ ' + errorMessage);
    }
  };

  const handleSubmitClaim = async () => {
    if (!file) {
      setClaimStatus('Please select a file');
      return;
    }
    
    if (!isRegistered) {
      setClaimStatus('❌ You must be registered to submit claims. Please contact admin.');
      return;
    }
    
    try {
      setClaimStatus('🔄 Submitting claim...');
      
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('buyer_address', currentAccount);
      formData.append('claim_description', 'Medical claim submission');
      
      // Submit claim with PDF file
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/submit-claim/`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit claim');
      }
      
      const result = await response.json();
      console.log('✅ Claim submitted:', result);
      
      setClaimStatus(`✅ Claim submitted successfully!
📋 Claim ID: ${result.claim_id}
💳 Transaction ID: ${result.transaction_id}
💰 Claim Amount: $${result.claim_amount}
🔍 Verification Status: ${result.verification_status}

Admin will review your claim and update the status.`);
      
      // Clear the file input
      setFile(null);
      
    } catch (error) {
      console.error('Claim submission error:', error);
      setClaimStatus('❌ Claim submission failed: ' + (error as Error).message);
    }
  };

  const fetchClaimHistory = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/buyer-history/${currentAccount}/`);
      if (!response.ok) {
        throw new Error('Failed to fetch claim history');
      }
      
      const data = await response.json();
      setClaimHistory(data.claims || []);
    } catch (error) {
      console.error('Error fetching claim history:', error);
    }
  };

  const fetchPremiumHistory = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/fetch-premiums/${currentAccount}/`);
      if (!response.ok) {
        throw new Error('Failed to fetch premium history');
      }
      
      const data = await response.json();
      setPremiumHistory(data || []);
    } catch (error) {
      console.error('Error fetching premium history:', error);
    }
  };

  // Add useEffect to fetch claim history when the component loads
  useEffect(() => {
    if (currentAccount) {
      fetchClaimHistory();
      fetchPremiumHistory();
    }
  }, [currentAccount]);

  if (isLoading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6">Buyer Dashboard</h2>
        <div className="text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Buyer Dashboard</h2>
      
      {/* Account Status */}
      <div className="card bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Account Status</h3>
        <div className="space-y-2">
          <p><strong>Address:</strong> {currentAccount}</p>
          <p><strong>Registration Status:</strong>
            <span className={`ml-2 px-2 py-1 rounded text-sm ${
              isRegistered
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {isRegistered ? '✅ Registered' : '❌ Not Registered'}
            </span>
          </p>
          {!isRegistered && (
            <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mt-4">
              <p className="font-bold">⚠️ Registration Required</p>
              <p>You need to be registered by an admin before you can pay premiums. Please contact the admin with your address: <code className="bg-gray-200 px-1 rounded">{currentAccount}</code></p>
            </div>
          )}
        </div>
      </div>
      
      <div className="card bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-4">Pay Monthly Premium</h3>
        <button
          onClick={handlePayPremium}
          disabled={!isRegistered}
          className={`px-6 py-2 rounded text-white ${
            isRegistered
              ? 'bg-green-600 hover:bg-green-700'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          Pay 0.1 ETH Premium
        </button>
        {premiumStatus && (
          <div className="mt-4 p-3 rounded bg-gray-50">
            <p className="whitespace-pre-wrap">{premiumStatus}</p>
          </div>
        )}
      </div>

      <div className="card bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Submit Insurance Claim</h3>
        
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Secure Document Upload:</strong> Your documents are automatically encrypted and stored securely.
                No email required - the system uses a centralized secure storage account.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Medical Document
            </label>
            <input
              type="file"
              accept=".pdf,image/*,.doc,.docx"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Supported formats: PDF, Images (JPG, PNG), Word documents
            </p>
          </div>
          
          <button
            onClick={handleSubmitClaim}
            disabled={!file || !isRegistered}
            className={`w-full py-3 px-4 rounded-lg font-medium ${
              file && isRegistered
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {!isRegistered ? 'Registration Required' : 'Submit Encrypted Claim'}
          </button>
        </div>
        
        {claimStatus && (
          <div className={`mt-4 p-4 rounded-lg ${
            claimStatus.includes('✅')
              ? 'bg-green-50 text-green-800 border border-green-200'
              : claimStatus.includes('❌')
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'bg-blue-50 text-blue-800 border border-blue-200'
          }`}>
            <p className="whitespace-pre-wrap text-sm">{claimStatus}</p>
          </div>
        )}
      </div>

      {/* Claim History */}
      <div className="card bg-white p-6 rounded-lg shadow-md mt-6">
        <h3 className="text-xl font-semibold mb-4">Claim History</h3>
        
        {claimHistory.length === 0 ? (
          <p className="text-gray-500">No claims submitted yet.</p>
        ) : (
          <div className="space-y-4">
            {claimHistory.map((claim) => (
              <div key={claim.claim_id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">Claim ID: {claim.claim_id}</h4>
                    <p className="text-sm text-gray-600 mt-1">${claim.amount} - {new Date(claim.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    claim.status === 'accepted' ? 'bg-green-100 text-green-800' :
                    claim.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    claim.status === 'not_approved' ? 'bg-red-100 text-red-800' :
                    claim.status === 'verified' ? 'bg-blue-100 text-blue-800' :
                    claim.status === 'unverified' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {claim.status_message || claim.status}
                  </span>
                </div>
                <p className="text-sm mt-2">{claim.description}</p>
                {claim.hospital_transaction_id && (
                  <p className="text-xs text-gray-500 mt-1">Transaction ID: {claim.hospital_transaction_id}</p>
                )}
                {claim.storacha_cid && (
                  <div className="mt-2">
                    <a 
                      href={`https://${claim.storacha_cid}.ipfs.storacha.link`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View on Storacha
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Premium Payment History */}
      <div className="card bg-white p-6 rounded-lg shadow-md mt-6">
        <h3 className="text-xl font-semibold mb-4">Premium Payment History</h3>
        
        {premiumHistory.length === 0 ? (
          <p className="text-gray-500">No premium payments recorded yet.</p>
        ) : (
          <div className="space-y-4">
            {premiumHistory.map((premium) => (
              <div key={premium.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">Transaction: {premium.transaction_hash.substring(0, 10)}...{premium.transaction_hash.substring(premium.transaction_hash.length - 8)}</h4>
                    <p className="text-sm text-gray-600 mt-1">{premium.amount_eth} ETH - {new Date(premium.block_timestamp).toLocaleDateString()}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    premium.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                    premium.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {premium.status.charAt(0).toUpperCase() + premium.status.slice(1)}
                  </span>
                </div>
                {premium.storacha_cid && (
                  <div className="mt-2">
                    <a 
                      href={`https://${premium.storacha_cid}.ipfs.storacha.link`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View on Storacha
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
