import { Web3 } from "web3";

let web3: Web3 | null = null;

export async function initWeb3(): Promise<Web3> {
  if ((window as any).ethereum) {
    web3 = new Web3((window as any).ethereum);
    try {
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
    throw new Error("Web3 not initialized. Call initWeb3 first.");
  }
  return web3;
}

export async function getAccount(): Promise<string | null> {
  if (!web3) return null;
  try {
    const accounts = await web3.eth.getAccounts();
    return accounts[0] || null;
  } catch (error) {
    console.error("Failed to get accounts:", error);
    return null;
  }
}