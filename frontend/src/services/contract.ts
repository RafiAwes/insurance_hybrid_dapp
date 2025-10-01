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
  // Add more ABI entries as needed
];

const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS || "0x5FbDB2315678afecb367f032d93F642f64180aa3";

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
  const web3 = getWeb3();
  const accounts = await web3.eth.getAccounts();
  const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
  
  const premium = web3.utils.toWei("0.1", "ether");
  const result = await contract.methods.payPremium()
    .send({ from: accounts[0], value: premium });
  
  return result;
}

export async function verifyClaimOnChain(claimId: string, status: boolean) {
  const web3 = getWeb3();
  const accounts = await web3.eth.getAccounts();
  const contract = new web3.eth.Contract(HEALTH_INSURANCE_ABI, CONTRACT_ADDRESS);
  
  const result = await contract.methods.verifyClaim(claimId, status)
    .send({ from: accounts[0] });
  
  return result;
}