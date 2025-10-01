import { Web3 } from "web3";

let web3: Web3 | null = null;

export async function initWeb3(): Promise<Web3> {
  if (typeof window !== 'undefined' && (window as any).ethereum) {
    web3 = new Web3((window as any).ethereum);
    try {
      // Request account access if needed
      await (window as any).ethereum.request({ method: "eth_requestAccounts" });
      return web3;
    } catch (error) {
      console.error("Failed to connect to MetaMask:", error);
      throw error;
    }
  } else {
    throw new Error("MetaMask not found. Please install MetaMask.");
  }
}

export function getWeb3(): Web3 {
  if (!web3) {
    // Try to initialize web3 if MetaMask is available
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      web3 = new Web3((window as any).ethereum);
      return web3;
    }
    throw new Error("Web3 not initialized and MetaMask not found.");
  }
  return web3;
}

export async function getAccount(): Promise<string | null> {
  try {
    const web3Instance = getWeb3();
    const accounts = await web3Instance.eth.getAccounts();
    return accounts[0] || null;
  } catch (error) {
    console.error("Failed to get accounts:", error);
    return null;
  }
}

export async function getBalance(address: string): Promise<string> {
  try {
    const web3Instance = getWeb3();
    const balance = await web3Instance.eth.getBalance(address);
    return web3Instance.utils.fromWei(balance, 'ether');
  } catch (error) {
    console.error("Failed to get balance:", error);
    return '0';
  }
}

export async function getChainId(): Promise<number> {
  try {
    const web3Instance = getWeb3();
    const chainId = await web3Instance.eth.getChainId();
    return Number(chainId);
  } catch (error) {
    console.error("Failed to get chain ID:", error);
    return 0;
  }
}

export function isMetaMaskInstalled(): boolean {
  return typeof window !== 'undefined' && typeof (window as any).ethereum !== 'undefined';
}

export async function switchToNetwork(chainId: string): Promise<boolean> {
  if (!isMetaMaskInstalled()) return false;
  
  try {
    await (window as any).ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId }],
    });
    return true;
  } catch (error: any) {
    console.error("Failed to switch network:", error);
    
    // If the network doesn't exist, try to add it (for custom networks)
    if (error.code === 4902) {
      // This would be for adding custom networks like Hardhat local
      // For now, just return false
      return false;
    }
    return false;
  }
}

// Network configurations
export const NETWORKS = {
  ETHEREUM_MAINNET: {
    chainId: '0x1',
    name: 'Ethereum Mainnet',
    rpcUrl: 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY'
  },
  SEPOLIA_TESTNET: {
    chainId: '0xaa36a7',
    name: 'Sepolia Testnet',
    rpcUrl: 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY'
  },
  HARDHAT_LOCAL: {
    chainId: '0x7a69',
    name: 'Hardhat Local',
    rpcUrl: 'http://127.0.0.1:8545'
  }
};