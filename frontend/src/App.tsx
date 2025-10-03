import { useState, useEffect } from 'react'
import WalletConnect from './components/WalletConnect'
import BuyerDashboard from './components/BuyerDashboard'
import BuyerLogin from './components/BuyerLogin'
import AdminLogin from './components/AdminLogin'
import AdminDashboard from './components/AdminDashboard'
import { isMetaMaskInstalled } from './services/web3'
import './App.css'

function App() {
  const [connectedAccount, setConnectedAccount] = useState<string | null>(null)
  const [isMetaMaskAvailable, setIsMetaMaskAvailable] = useState(false)
  const [currentView, setCurrentView] = useState<'buyer' | 'admin'>('buyer')
  const [adminData, setAdminData] = useState<any>(null)
  const [buyerData, setBuyerData] = useState<any>(null)

  useEffect(() => {
    // Check if MetaMask is installed
    setIsMetaMaskAvailable(isMetaMaskInstalled())
  }, [])

  const handleAccountChange = (account: string | null) => {
    setConnectedAccount(account)
    console.log('Account changed:', account)
  }

  const handleAdminLogin = (admin: any) => {
    setAdminData(admin)
    setBuyerData(null) // Clear buyer data when admin logs in
    console.log('Admin logged in:', admin)
  }

  const handleBuyerLogin = (buyer: any) => {
    setBuyerData(buyer)
    setAdminData(null) // Clear admin data when buyer logs in
    console.log('Buyer logged in:', buyer)
  }

  const handleLogout = () => {
    setAdminData(null)
    setBuyerData(null)
    setConnectedAccount(null)
    setCurrentView('buyer')
  }

  // Determine if user is logged in
  const isLoggedIn = (adminData && adminData.wallet_verified) || (buyerData && buyerData.wallet_verified)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">
                🏥 Health Insurance DApp
              </h1>
              
              {/* View Toggle - Only show if not logged in */}
              {!isLoggedIn && (
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setCurrentView('buyer')}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      currentView === 'buyer'
                        ? 'bg-white text-green-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    👤 Buyer
                  </button>
                  <button
                    onClick={() => setCurrentView('admin')}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      currentView === 'admin'
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    🛡️ Admin
                  </button>
                </div>
              )}

              {/* Show current user type when logged in */}
              {isLoggedIn && (
                <div className="bg-gray-100 rounded-lg px-3 py-1">
                  <span className="text-sm font-medium text-gray-700">
                    {adminData ? '🛡️ Admin Portal' : '👤 Buyer Portal'}
                  </span>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Welcome message */}
              {adminData && (
                <div className="text-sm text-gray-600">
                  Welcome, {adminData.full_name}
                </div>
              )}
              {buyerData && (
                <div className="text-sm text-gray-600">
                  Welcome, {buyerData.full_name}
                </div>
              )}
              
              {/* No automatic wallet connect - MetaMask connects during verification only */}
              
              {/* Logout button */}
              {(adminData || buyerData || connectedAccount) && (
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Logout
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'admin' ? (
          // Admin Section
          adminData && adminData.wallet_verified ? (
            <AdminDashboard adminData={adminData} />
          ) : (
            <AdminLogin onAdminLogin={handleAdminLogin} />
          )
        ) : (
          // Buyer Section
          buyerData && buyerData.wallet_verified ? (
            // Buyer logged in - show buyer dashboard
            <div className="space-y-8">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">
                  Welcome back, {buyerData.full_name}!
                </h2>
                <p className="text-gray-600">
                  Manage your insurance policies, submit claims, and track your history.
                </p>
                <div className="mt-2 text-sm text-gray-500">
                  Wallet: {buyerData.wallet_address}
                </div>
              </div>

              {/* Buyer Dashboard */}
              <BuyerDashboard />

              {/* Additional Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    📋 Submit Claims
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Submit insurance claims with encrypted medical documents stored on IPFS.
                  </p>
                </div>
                
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    📊 Track History
                  </h3>
                  <p className="text-gray-600 text-sm">
                    View your complete insurance history and claim status on the blockchain.
                  </p>
                </div>
                
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    🔒 Secure & Private
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Your medical data is encrypted and stored securely using blockchain technology.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            // Buyer not logged in - show login form
            <BuyerLogin onBuyerLogin={handleBuyerLogin} />
          )
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-500 text-sm">
            <p>Health Insurance DApp - Powered by Blockchain Technology</p>
            {connectedAccount && currentView === 'buyer' && (
              <p className="mt-1">
                Connected: {connectedAccount.slice(0, 6)}...{connectedAccount.slice(-4)}
              </p>
            )}
            {adminData && currentView === 'admin' && (
              <p className="mt-1">
                Admin: {adminData.email} | Wallet Verified: {adminData.wallet_verified ? '✅' : '❌'}
              </p>
            )}
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App