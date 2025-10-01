const { ethers } = require("hardhat");
const hre = require("hardhat");

async function main() {
  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  
  console.log("Deploying contracts with the account:", deployer.address);

  // Get account balance - compatible with both Ethers v5 and v6
  try {
    const balance = await deployer.provider.getBalance(deployer.address);
    console.log("Account balance:", ethers.formatEther(balance), "ETH");
  } catch (error) {
    console.log("Could not fetch balance:", error.message);
  }

  // Deploy the HealthInsurance contract
  console.log("Deploying HealthInsurance contract...");
  const HealthInsurance = await ethers.getContractFactory("HealthInsurance");
  const healthInsurance = await HealthInsurance.deploy();

  // Wait for deployment to complete
  await healthInsurance.waitForDeployment();

  // Get the deployed contract address
  const contractAddress = await healthInsurance.getAddress();
  console.log("HealthInsurance deployed to:", contractAddress);
  
  // Additional deployment info
  console.log("Transaction hash:", healthInsurance.deploymentTransaction().hash);
  console.log("Deployment completed successfully!");
  
  // Save deployment info to a file for easy reference
  const fs = require('fs');
  const deploymentInfo = {
    contractAddress: contractAddress,
    deployerAddress: deployer.address,
    network: hre.network.name,
    timestamp: new Date().toISOString(),
    transactionHash: healthInsurance.deploymentTransaction().hash
  };
  
  fs.writeFileSync('deployment-info.json', JSON.stringify(deploymentInfo, null, 2));
  console.log("Deployment info saved to deployment-info.json");
  
  return contractAddress;
}

// Execute the deployment
main()
  .then((contractAddress) => {
    console.log(`\n🎉 Deployment successful!`);
    console.log(`📋 Contract Address: ${contractAddress}`);
    console.log(`📝 Update your .env file with:`);
    console.log(`   CONTRACT_ADDRESS=${contractAddress}`);
    process.exitCode = 0;
  })
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exitCode = 1;
  });