import { useState } from 'react';
import { getAccount } from '../services/web3';
import { loginToStoracha } from '../services/storacha';

interface BuyerLoginProps {
  onBuyerLogin: (buyerData: any) => void;
}

interface BuyerData {
  id: string;
  email: string;
  full_name: string;
  wallet_address: string;
  wallet_verified: boolean;
}

export default function BuyerLogin({ onBuyerLogin }: BuyerLoginProps) {
  const [step, setStep] = useState<'login' | 'wallet'>('login');
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [buyerData, setBuyerData] = useState<BuyerData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api'}/buyer/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Automatically login to Storacha using the specific email
        try {
          await loginToStoracha();
          console.log('Storacha login for buyer: ✅ Success');
        } catch (storachaError) {
          console.error('Error logging into Storacha:', storachaError);
        }
        
        setBuyerData(data.buyer);
        setStep('wallet');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleWalletVerification = async () => {
    if (!buyerData) return;

    setLoading(true);
    setError(null);

    try {
      // First, request MetaMask connection
      if (!window || !(window as any).ethereum) {
        setError('MetaMask is not installed. Please install MetaMask to continue.');
        return;
      }

      const ethereum = (window as any).ethereum;
      
      // Request account access from MetaMask
      const accounts = await ethereum.request({
        method: "eth_requestAccounts"
      });

      if (!accounts || accounts.length === 0) {
        setError('No MetaMask accounts found. Please check your MetaMask.');
        return;
      }

      const walletAddress = accounts[0];

      // Verify wallet address with backend
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api'}/buyer/verify-wallet/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          buyer_id: buyerData.id
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Address verified successfully - now MetaMask is connected
        const verifiedBuyerData = {
          ...buyerData,
          wallet_verified: true,
          connected_wallet: walletAddress
        };
        onBuyerLogin(verifiedBuyerData);
      } else {
        setError(data.error || 'Wallet address verification failed. Please use your registered wallet.');
      }
    } catch (err: any) {
      console.error('Wallet verification error:', err);
      
      if (err.code === 4001) {
        setError('MetaMask connection rejected by user.');
      } else if (err.code === -32002) {
        setError('MetaMask connection request already pending. Please check MetaMask.');
      } else {
        setError('Failed to connect MetaMask. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const resetLogin = () => {
    setStep('login');
    setBuyerData(null);
    setFormData({ email: '', password: '' });
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">
            👤 Buyer Login
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Health Insurance DApp - Buyer Portal
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {step === 'login' ? (
            <form onSubmit={handleEmailLogin} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="buyer@example.com"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="mt-1">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={handleInputChange}
                    className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    loading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                  }`}
                >
                  {loading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Logging in...
                    </div>
                  ) : (
                    'Login'
                  )}
                </button>
              </div>

              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <button
                    type="button"
                    className="font-medium text-green-600 hover:text-green-500"
                    onClick={() => setError('Registration feature coming soon!')}
                  >
                    Register here
                  </button>
                </p>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              <div className="text-center">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <h3 className="text-lg font-medium text-green-800 mb-2">
                    ✅ Email Verified
                  </h3>
                  <p className="text-sm text-green-700">
                    Welcome, {buyerData?.full_name}!
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    {buyerData?.email}
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-blue-800 mb-2">
                    🦊 Wallet Verification Required
                  </h3>
                  <p className="text-sm text-blue-700 mb-4">
                    Please connect with your registered MetaMask wallet to complete authentication.
                  </p>
                  <p className="text-xs text-blue-600 mb-4">
                    Required wallet: {buyerData?.wallet_address}
                  </p>
                  
                  <button
                    onClick={handleWalletVerification}
                    disabled={loading}
                    className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                      loading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                    }`}
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Verifying Wallet...
                      </div>
                    ) : (
                      '🦊 Verify MetaMask Wallet'
                    )}
                  </button>
                </div>
              </div>

              <div className="text-center">
                <button
                  onClick={resetLogin}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  ← Back to Login
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Buyer access requires both email/password and MetaMask wallet verification</p>
        </div>
      </div>
    </div>
  );
}