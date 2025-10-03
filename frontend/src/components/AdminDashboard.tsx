import { useState, useEffect } from 'react';
import { getWeb3, getAccount } from '../services/web3';
import { registerBuyerOnChain, checkBuyerRegistration } from '../services/contract';

interface Claim {
  claim_id: string;
  buyer: string;
  claim_amount: string;
  claim_description: string;
  claim_status: string;
  created_at: string;
  hospital_transaction_id: string;
}

interface Buyer {
  id: number;
  wallet_address: string;
  name: string;
  email: string;
  created_at: string;
}

interface AdminDashboardProps {
  adminData?: {
    id: string;
    email: string;
    full_name: string;
    wallet_verified: boolean;
  };
}

export default function AdminDashboard({ adminData }: AdminDashboardProps) {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [buyers, setBuyers] = useState<Buyer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'claims' | 'buyers' | 'analytics' | 'registration'>('registration');
  const [newBuyerAddress, setNewBuyerAddress] = useState('');
  const [registrationStatus, setRegistrationStatus] = useState('');
  const [checkAddress, setCheckAddress] = useState('');
  const [checkResult, setCheckResult] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // In a real implementation, you would fetch from your Django API
      // For now, we'll use mock data
      
      // Mock claims data
      const mockClaims: Claim[] = [
        {
          claim_id: 'CLM-001',
          buyer: '0x1234...5678',
          claim_amount: '1000',
          claim_description: 'Emergency surgery',
          claim_status: 'pending',
          created_at: '2025-01-01T10:00:00Z',
          hospital_transaction_id: 'HSP-001'
        },
        {
          claim_id: 'CLM-002',
          buyer: '0x9876...5432',
          claim_amount: '500',
          claim_description: 'Routine checkup',
          claim_status: 'verified',
          created_at: '2025-01-01T11:00:00Z',
          hospital_transaction_id: 'HSP-002'
        }
      ];

      // Mock buyers data
      const mockBuyers: Buyer[] = [
        {
          id: 1,
          wallet_address: '0x1234...5678',
          name: 'John Doe',
          email: 'john@example.com',
          created_at: '2024-12-01T10:00:00Z'
        },
        {
          id: 2,
          wallet_address: '0x9876...5432',
          name: 'Jane Smith',
          email: 'jane@example.com',
          created_at: '2024-12-02T10:00:00Z'
        }
      ];

      setClaims(mockClaims);
      setBuyers(mockBuyers);
    } catch (err) {
      setError('Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimAction = async (claimId: string, action: 'approve' | 'reject') => {
    try {
      // In a real implementation, you would call your Django API
      console.log(`${action} claim ${claimId}`);
      
      // Update local state
      setClaims(claims.map(claim => 
        claim.claim_id === claimId 
          ? { ...claim, claim_status: action === 'approve' ? 'verified' : 'rejected' }
          : claim
      ));
      
      alert(`Claim ${claimId} has been ${action}d successfully!`);
    } catch (err) {
      console.error(`Error ${action}ing claim:`, err);
      alert(`Failed to ${action} claim`);
    }
  };

  const handleRegisterBuyer = async () => {
    if (!newBuyerAddress || newBuyerAddress.length !== 42) {
      setRegistrationStatus('❌ Please enter a valid wallet address (42 characters)');
      return;
    }

    try {
      setRegistrationStatus('🔄 Registering buyer on blockchain...');
      
      // First check if already registered
      const isAlreadyRegistered = await checkBuyerRegistration(newBuyerAddress);
      if (isAlreadyRegistered) {
        setRegistrationStatus('⚠️ Buyer is already registered on the blockchain');
        return;
      }

      // Register the buyer
      const result = await registerBuyerOnChain(newBuyerAddress);
      setRegistrationStatus(`✅ Buyer registered successfully!\nTransaction Hash: ${result.transactionHash}\nAddress: ${newBuyerAddress}`);
      
      // Clear the input
      setNewBuyerAddress('');
      
    } catch (error: any) {
      console.error('Registration error:', error);
      let errorMessage = '❌ Registration failed: ';
      
      if (error?.message?.includes('Only admin')) {
        errorMessage += 'Only admin can register buyers. Make sure you are connected with the admin wallet.';
      } else if (error?.message?.includes('User denied')) {
        errorMessage += 'Transaction was rejected by user.';
      } else if (error?.message?.includes('insufficient funds')) {
        errorMessage += 'Insufficient funds for gas fees.';
      } else {
        errorMessage += error?.message || 'Unknown error occurred';
      }
      
      setRegistrationStatus(errorMessage);
    }
  };

  const handleCheckRegistration = async () => {
    if (!checkAddress || checkAddress.length !== 42) {
      setCheckResult('❌ Please enter a valid wallet address (42 characters)');
      return;
    }

    try {
      const isRegistered = await checkBuyerRegistration(checkAddress);
      setCheckResult(
        isRegistered
          ? `✅ Address is registered and can pay premiums\n${checkAddress}`
          : `❌ Address is NOT registered\n${checkAddress}\nThis buyer needs to be registered before paying premiums.`
      );
    } catch (error: any) {
      console.error('Check registration error:', error);
      setCheckResult(`❌ Error checking registration: ${error?.message || 'Unknown error'}`);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800',
      verified: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button 
          onClick={fetchData}
          className="mt-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🛡️ Admin Dashboard
        </h2>
        <p className="text-gray-600">
          Manage insurance claims, buyers, and system analytics
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'registration', label: 'Buyer Registration', icon: '🔐' },
              { id: 'claims', label: 'Claims Management', icon: '📋' },
              { id: 'buyers', label: 'Buyers', icon: '👥' },
              { id: 'analytics', label: 'Analytics', icon: '📊' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Buyer Registration Tab */}
          {activeTab === 'registration' && (
            <div className="space-y-6">
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700">
                      <strong>Important:</strong> Buyers must be registered on the blockchain before they can pay premiums.
                      The payment error "Internal JSON-RPC error" occurs when unregistered buyers try to pay.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Register New Buyer */}
                <div className="bg-white border rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">🔐 Register New Buyer</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Buyer Wallet Address
                      </label>
                      <input
                        type="text"
                        value={newBuyerAddress}
                        onChange={(e) => setNewBuyerAddress(e.target.value)}
                        placeholder="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Enter the complete wallet address (42 characters starting with 0x)
                      </p>
                    </div>
                    <button
                      onClick={handleRegisterBuyer}
                      disabled={!newBuyerAddress || newBuyerAddress.length !== 42}
                      className={`w-full py-3 px-4 rounded-lg font-medium ${
                        newBuyerAddress && newBuyerAddress.length === 42
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      Register Buyer on Blockchain
                    </button>
                    {registrationStatus && (
                      <div className={`p-3 rounded-lg ${
                        registrationStatus.includes('✅')
                          ? 'bg-green-50 text-green-800'
                          : registrationStatus.includes('❌')
                          ? 'bg-red-50 text-red-800'
                          : 'bg-blue-50 text-blue-800'
                      }`}>
                        <p className="whitespace-pre-wrap">{registrationStatus}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Check Registration Status */}
                <div className="bg-white border rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">🔍 Check Registration Status</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Wallet Address to Check
                      </label>
                      <input
                        type="text"
                        value={checkAddress}
                        onChange={(e) => setCheckAddress(e.target.value)}
                        placeholder="0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <button
                      onClick={handleCheckRegistration}
                      disabled={!checkAddress || checkAddress.length !== 42}
                      className={`w-full py-3 px-4 rounded-lg font-medium ${
                        checkAddress && checkAddress.length === 42
                          ? 'bg-green-600 hover:bg-green-700 text-white'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      Check Registration Status
                    </button>
                    {checkResult && (
                      <div className={`p-3 rounded-lg ${
                        checkResult.includes('✅')
                          ? 'bg-green-50 text-green-800'
                          : 'bg-red-50 text-red-800'
                      }`}>
                        <p>{checkResult}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="font-semibold mb-4">🚀 Quick Actions</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => {
                      setNewBuyerAddress('0x70997970C51812dc3A010C7d01b50e0d17dc79C8');
                      setCheckAddress('0x70997970C51812dc3A010C7d01b50e0d17dc79C8');
                    }}
                    className="p-3 bg-blue-100 hover:bg-blue-200 rounded-lg text-blue-800 text-sm"
                  >
                    📝 Use Reported Address (0x70997970C51812dc3A010C7d01b50e0d17dc79C8)
                  </button>
                  <button
                    onClick={async () => {
                      const account = await getAccount();
                      if (account) {
                        setNewBuyerAddress(account);
                        setCheckAddress(account);
                      }
                    }}
                    className="p-3 bg-green-100 hover:bg-green-200 rounded-lg text-green-800 text-sm"
                  >
                    🔗 Use Current Connected Account
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Claims Management Tab */}
          {activeTab === 'claims' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Claims Management</h3>
                <div className="text-sm text-gray-500">
                  Total Claims: {claims.length}
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Claim ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Buyer
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {claims.map((claim) => (
                      <tr key={claim.claim_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {claim.claim_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {claim.buyer}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${claim.claim_amount}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {claim.claim_description}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(claim.claim_status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          {claim.claim_status === 'pending' && (
                            <div className="space-x-2">
                              <button
                                onClick={() => handleClaimAction(claim.claim_id, 'approve')}
                                className="text-green-600 hover:text-green-900"
                              >
                                ✅ Approve
                              </button>
                              <button
                                onClick={() => handleClaimAction(claim.claim_id, 'reject')}
                                className="text-red-600 hover:text-red-900"
                              >
                                ❌ Reject
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Buyers Tab */}
          {activeTab === 'buyers' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Registered Buyers</h3>
                <div className="text-sm text-gray-500">
                  Total Buyers: {buyers.length}
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Wallet Address
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Registered
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {buyers.map((buyer) => (
                      <tr key={buyer.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {buyer.wallet_address}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {buyer.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {buyer.email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(buyer.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold">System Analytics</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="text-2xl font-bold text-blue-600">
                    {claims.length}
                  </div>
                  <div className="text-sm text-blue-800">Total Claims</div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-6">
                  <div className="text-2xl font-bold text-green-600">
                    {claims.filter(c => c.claim_status === 'verified').length}
                  </div>
                  <div className="text-sm text-green-800">Approved Claims</div>
                </div>
                
                <div className="bg-yellow-50 rounded-lg p-6">
                  <div className="text-2xl font-bold text-yellow-600">
                    {claims.filter(c => c.claim_status === 'pending').length}
                  </div>
                  <div className="text-sm text-yellow-800">Pending Claims</div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="font-semibold mb-4">Recent Activity</h4>
                <div className="space-y-2">
                  {claims.slice(0, 5).map((claim) => (
                    <div key={claim.claim_id} className="flex justify-between items-center text-sm">
                      <span>Claim {claim.claim_id} - {claim.claim_description}</span>
                      <span className="text-gray-500">
                        {new Date(claim.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}