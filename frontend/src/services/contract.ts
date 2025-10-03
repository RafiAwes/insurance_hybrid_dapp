import Web3 from "web3";
import { getWeb3 } from "./web3";

// ABI stub - replace with actual ABI from Hardhat compilation
const HEALTH_INSURANCE_ABI = [
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_claimId",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_hospitalTxnId",
        "type": "string"
      }
    ],
    "name": "submitClaim",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_claimId",
        "type": "string"
      },
      {
        "internalType": "bool",
        "name": "_status",
        "type": "bool"
      }
    ],
    "name": "verifyClaim",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "payPremium",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "registeredBuyer",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "buyer",
        "type": "address"
      }
    ],
    "name": "registerBuyer",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];

// Fix the environment variable - it should be the actual contract address, not "CONTRACT_ADDRESS"
const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS || "0x5FbDB2315678afecb367f032d93F642f64180aa3";
console.log("🔍 [DEBUG] Contract address from env:", import.meta.env.VITE_CONTRACT_ADDRESS);
console.log("🔍 [DEBUG] Using contract address:", CONTRACT_ADDRESS);

export async function submitClaimOnChain(claimId: string, amount: number, hospitalTxnId: string) {
  const web3 = getWeb3();
  const accounts = await web3.eth.getAccounts();
  const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
  
  const weiAmount = web3.utils.toWei(amount.toString(), "ether");
  const result = await contract.methods.submitClaim(claimId, weiAmount, hospitalTxnId)
    .send({ from: accounts[0] });
  
  return result;
}

export async function payPremiumOnChain() {
  console.log("🔍 [DEBUG] Starting payPremiumOnChain...");
  
  try {
    const web3 = getWeb3();
    console.log("✅ [DEBUG] Web3 instance obtained");
    
    const accounts = await web3.eth.getAccounts();
    console.log("✅ [DEBUG] Accounts retrieved:", accounts);
    
    if (!accounts || accounts.length === 0) {
      throw new Error("No accounts found. Please connect your wallet.");
    }
    
    const account = accounts[0];
    console.log("🔍 [DEBUG] Using account:", account);
    console.log("🔍 [DEBUG] Contract address:", CONTRACT_ADDRESS);
    
    // Check network
    const chainId = await web3.eth.getChainId();
    console.log("🔍 [DEBUG] Current chain ID:", chainId);
    
    // Check account balance
    const balance = await web3.eth.getBalance(account);
    const balanceEth = web3.utils.fromWei(balance, 'ether');
    console.log("🔍 [DEBUG] Account balance:", balanceEth, "ETH");
    
    if (parseFloat(balanceEth) < 0.1) {
      throw new Error(`Insufficient balance. Required: 0.1 ETH, Available: ${balanceEth} ETH`);
    }
    
    const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
    console.log("✅ [DEBUG] Contract instance created");
    
    // Check if buyer is registered
    try {
      const isRegistered = await contract.methods.registeredBuyer(account).call();
      console.log("🔍 [DEBUG] Is buyer registered:", isRegistered);
      
      if (!isRegistered) {
        throw new Error("Buyer not registered. Please contact admin to register your address: " + account);
      }
    } catch (registrationError) {
      console.error("❌ [DEBUG] Error checking registration:", registrationError);
      throw new Error("Failed to check buyer registration status. Contract might not be deployed correctly.");
    }
    
    const premium = web3.utils.toWei("0.1", "ether");
    console.log("🔍 [DEBUG] Premium amount (wei):", premium);
    
    // Estimate gas first
    try {
      const gasEstimate = await contract.methods.payPremium().estimateGas({
        from: account,
        value: premium
      });
      console.log("🔍 [DEBUG] Gas estimate:", gasEstimate);
    } catch (gasError: any) {
      console.error("❌ [DEBUG] Gas estimation failed:", gasError);
      throw new Error("Transaction will likely fail. Gas estimation error: " + (gasError?.message || gasError));
    }
    
    console.log("🔍 [DEBUG] Sending transaction...");
    const result = await contract.methods.payPremium()
      .send({
        from: account,
        value: premium,
        gas: "300000" // Set explicit gas limit
      });
    
    console.log("✅ [DEBUG] Transaction successful:", result);
    return result;
    
  } catch (error: any) {
    console.error("❌ [DEBUG] payPremiumOnChain failed:", error);
    
    // Enhanced error reporting
    if (error?.message?.includes("Internal JSON-RPC error")) {
      console.error("❌ [DEBUG] This is an Internal JSON-RPC error. Possible causes:");
      console.error("  1. Hardhat network not running");
      console.error("  2. Wrong network selected in MetaMask");
      console.error("  3. Contract not deployed");
      console.error("  4. Buyer not registered");
      console.error("  5. Insufficient gas or balance");
    }
    
    throw error;
  }
}

export async function verifyClaimOnChain(claimId: string, status: boolean) {
  const web3 = getWeb3();
  const accounts = await web3.eth.getAccounts();
  const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
  
  const result = await contract.methods.verifyClaim(claimId, status)
    .send({ from: accounts[0] });
  
  return result;
}

export async function checkBuyerRegistration(address?: string): Promise<boolean> {
  try {
    const web3 = getWeb3();
    const accounts = await web3.eth.getAccounts();
    const buyerAddress = address || accounts[0];
    
    if (!buyerAddress) {
      throw new Error("No account available");
    }
    
    const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
    const isRegistered = await contract.methods.registeredBuyer(buyerAddress).call();
    
    console.log("🔍 [DEBUG] Buyer registration check for", buyerAddress, ":", isRegistered);
    return Boolean(isRegistered);
  } catch (error) {
    console.error("❌ [DEBUG] Error checking buyer registration:", error);
    return false;
  }
}

export async function registerBuyerOnChain(buyerAddress: string) {
  try {
    const web3 = getWeb3();
    const accounts = await web3.eth.getAccounts();
    const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
    
    console.log("🔍 [DEBUG] Registering buyer:", buyerAddress);
    const result = await contract.methods.registerBuyer(buyerAddress)
      .send({ from: accounts[0] });
    
    console.log("✅ [DEBUG] Buyer registered successfully:", result);
    return result;
  } catch (error) {
    console.error("❌ [DEBUG] Error registering buyer:", error);
    throw error;
  }
}