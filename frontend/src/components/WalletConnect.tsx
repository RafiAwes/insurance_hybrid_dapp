import Web3 from "web3";
import { useState } from "react";

export default function WalletConnect() {
  const [account, setAccount] = useState<string | null>(null);

  async function connectWallet() {
    if ((window as any).ethereum) {
      const web3 = new Web3((window as any).ethereum);
      try {
        await (window as any).ethereum.request({ method: "eth_requestAccounts" });
        const accounts = await web3.eth.getAccounts();
        setAccount(accounts[0]);
      } catch (error) {
        console.error("Failed to connect wallet:", error);
      }
    } else {
      alert("Please install MetaMask!");
    }
  }

  return (
    <div className="p-4">
      <button 
        onClick={connectWallet} 
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition duration-200"
      >
        {account ? `Connected: ${account.slice(0,6)}...${account.slice(-4)}` : "Connect Wallet"}
      </button>
    </div>
  );
}