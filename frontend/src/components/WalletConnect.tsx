import { Web3 } from "web3";
import { useState, useEffect } from "react";

interface WalletConnectProps {
  onAccountChange?: (account: string | null) => void;
}

export default function WalletConnect({ onAccountChange }: WalletConnectProps) {
  const [account, setAccount] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chainId, setChainId] = useState<string | null>(null);

  // Check if already connected on component mount
  useEffect(() => {
    checkConnection();
    setupEventListeners();
  }, []);

  // Check if MetaMask is already connected
  async function checkConnection() {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      try {
        const web3 = new Web3((window as any).ethereum);
        const accounts = await web3.eth.getAccounts();
        const currentChainId = await web3.eth.getChainId();
        
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          setChainId(currentChainId.toString());
          onAccountChange?.(accounts[0]);
        }
      } catch (error) {
        console.error("Error checking connection:", error);
      }
    }
  }

  // Setup MetaMask event listeners
  function setupEventListeners() {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      const ethereum = (window as any).ethereum;

      // Listen for account changes
      ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          onAccountChange?.(accounts[0]);
          setError(null);
        } else {
          setAccount(null);
          onAccountChange?.(null);
        }
      });

      // Listen for chain changes
      ethereum.on('chainChanged', (chainId: string) => {
        setChainId(chainId);
        // Reload the page when chain changes (recommended by MetaMask)
        window.location.reload();
      });

      // Listen for connection
      ethereum.on('connect', (connectInfo: { chainId: string }) => {
        setChainId(connectInfo.chainId);
        setError(null);
      });

      // Listen for disconnection
      ethereum.on('disconnect', () => {
        setAccount(null);
        setChainId(null);
        onAccountChange?.(null);
      });
    }
  }

  async function connectWallet() {
    if (!window || !(window as any).ethereum) {
      setError("MetaMask is not installed. Please install MetaMask to continue.");
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      const ethereum = (window as any).ethereum;
      
      // Request account access
      const accounts = await ethereum.request({
        method: "eth_requestAccounts"
      });

      if (accounts.length > 0) {
        const web3 = new Web3(ethereum);
        const currentChainId = await web3.eth.getChainId();
        
        setAccount(accounts[0]);
        setChainId(currentChainId.toString());
        onAccountChange?.(accounts[0]);
        
        console.log("Wallet connected successfully:", accounts[0]);
        console.log("Chain ID:", currentChainId.toString());
      } else {
        setError("No accounts found. Please check your MetaMask.");
      }
    } catch (error: any) {
      console.error("Failed to connect wallet:", error);
      
      if (error.code === 4001) {
        setError("Connection rejected by user.");
      } else if (error.code === -32002) {
        setError("Connection request already pending. Please check MetaMask.");
      } else {
        setError("Failed to connect to MetaMask. Please try again.");
      }
    } finally {
      setIsConnecting(false);
    }
  }

  async function disconnectWallet() {
    setAccount(null);
    setChainId(null);
    onAccountChange?.(null);
    // Note: MetaMask doesn't have a programmatic disconnect method
    // Users need to disconnect manually from MetaMask
  }

  function getNetworkName(chainId: string): string {
    const networks: { [key: string]: string } = {
      '1': 'Ethereum Mainnet',
      '3': 'Ropsten Testnet',
      '4': 'Rinkeby Testnet',
      '5': 'Goerli Testnet',
      '11155111': 'Sepolia Testnet',
      '31337': 'Hardhat Local',
      '1337': 'Ganache Local'
    };
    return networks[chainId] || `Chain ID: ${chainId}`;
  }

  return (
    <div className="p-4">
      <div className="flex flex-col items-center space-y-2">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded text-sm max-w-md">
            {error}
          </div>
        )}
        
        {account ? (
          <div className="text-center">
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded mb-2">
              <div className="font-semibold">✅ Wallet Connected</div>
              <div className="text-sm">
                {account.slice(0, 6)}...{account.slice(-4)}
              </div>
              {chainId && (
                <div className="text-xs mt-1">
                  Network: {getNetworkName(chainId)}
                </div>
              )}
            </div>
            <button
              onClick={disconnectWallet}
              className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm transition duration-200"
            >
              Disconnect
            </button>
          </div>
        ) : (
          <button
            onClick={connectWallet}
            disabled={isConnecting}
            className={`px-6 py-3 rounded-lg font-semibold transition duration-200 ${
              isConnecting
                ? "bg-gray-400 cursor-not-allowed text-white"
                : "bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg"
            }`}
          >
            {isConnecting ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Connecting...</span>
              </div>
            ) : (
              "🦊 Connect MetaMask"
            )}
          </button>
        )}
      </div>
    </div>
  );
}