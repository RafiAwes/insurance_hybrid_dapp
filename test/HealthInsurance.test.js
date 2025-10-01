const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("HealthInsurance", function () {
  let healthInsurance;
  let owner;
  let buyer;
  let hospital;

  beforeEach(async function () {
    [owner, buyer, hospital] = await ethers.getSigners();

    const HealthInsurance = await ethers.getContractFactory("HealthInsurance");
    healthInsurance = await HealthInsurance.deploy();
    await healthInsurance.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await healthInsurance.admin()).to.equal(owner.address);
    });
  });

  describe("Buyer Registration", function () {
    it("Should register a buyer by admin", async function () {
      await healthInsurance.connect(owner).registerBuyer(buyer.address);

      expect(await healthInsurance.registeredBuyer(buyer.address)).to.be.true;
    });

    it("Should not allow non-admin to register buyer", async function () {
      await expect(healthInsurance.connect(buyer).registerBuyer(hospital.address)).to.be.revertedWith("Only admin");
    });
  });

  describe("Premium Payment", function () {
    beforeEach(async function () {
      await healthInsurance.connect(owner).registerBuyer(buyer.address);
    });

    it("Should allow registered buyer to pay premium", async function () {
      const premium = ethers.parseEther("0.1");

      await expect(healthInsurance.connect(buyer).payPremium({ value: premium }))
        .to.emit(healthInsurance, "PremiumPaid")
        .withArgs(buyer.address, premium, await ethers.provider.getBlock("latest").then(b => b.timestamp));
    });

    it("Should not allow unregistered buyer to pay premium", async function () {
      const premium = ethers.parseEther("0.1");
      await expect(healthInsurance.connect(hospital).payPremium({ value: premium })).to.be.revertedWith("Not registered buyer");
    });

    it("Should not allow zero value premium", async function () {
      await expect(healthInsurance.connect(buyer).payPremium({ value: 0 })).to.be.revertedWith("Value > 0");
    });
  });

  describe("Claim Submission", function () {
    beforeEach(async function () {
      await healthInsurance.connect(owner).registerBuyer(buyer.address);
    });

    it("Should allow registered buyer to submit claim", async function () {
      const claimId = "claim-123";
      const amount = ethers.parseEther("1.0");
      const hospitalTxnId = "txn-456";

      await expect(healthInsurance.connect(buyer).submitClaim(claimId, amount, hospitalTxnId))
        .to.emit(healthInsurance, "ClaimSubmitted")
        .withArgs(buyer.address, claimId, amount);

      const claim = await healthInsurance.claims(claimId);
      expect(claim.buyer).to.equal(buyer.address);
      expect(claim.amount).to.equal(amount);
      expect(claim.hospitalTransactionId).to.equal(hospitalTxnId);
      expect(claim.verified).to.be.false;
    });

    it("Should not allow unregistered buyer to submit claim", async function () {
      const claimId = "claim-123";
      const amount = ethers.parseEther("1.0");
      const hospitalTxnId = "txn-456";

      await expect(healthInsurance.connect(hospital).submitClaim(claimId, amount, hospitalTxnId)).to.be.revertedWith("Not registered buyer");
    });
  });

  describe("Claim Verification", function () {
    beforeEach(async function () {
      await healthInsurance.connect(owner).registerBuyer(buyer.address);
      await healthInsurance.connect(buyer).submitClaim("claim-123", ethers.parseEther("1.0"), "txn-456");
    });

    it("Should allow admin to verify claim", async function () {
      await expect(healthInsurance.connect(owner).verifyClaim("claim-123", true))
        .to.emit(healthInsurance, "ClaimVerified")
        .withArgs("claim-123", true);

      const claim = await healthInsurance.claims("claim-123");
      expect(claim.verified).to.be.true;
    });

    it("Should not allow non-admin to verify claim", async function () {
      await expect(healthInsurance.connect(buyer).verifyClaim("claim-123", true)).to.be.revertedWith("Only admin");
    });
  });
});