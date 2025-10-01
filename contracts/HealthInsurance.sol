// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract HealthInsurance {
    address public admin;

    struct Claim {
        string claimId;
        address buyer;
        uint256 amount;
        string hospitalTransactionId;
        bool verified;
        uint256 submittedAt;
    }

    mapping(string => Claim) public claims;
    mapping(address => bool) public registeredBuyer;

    event PremiumPaid(address indexed buyer, uint256 amount, uint256 timestamp);
    event ClaimSubmitted(address indexed buyer, string claimId, uint256 amount);
    event ClaimVerified(string claimId, bool status);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function registerBuyer(address buyer) external onlyAdmin {
        registeredBuyer[buyer] = true;
    }

    function payPremium() external payable {
        require(registeredBuyer[msg.sender], "Not registered buyer");
        require(msg.value > 0, "Value > 0");
        emit PremiumPaid(msg.sender, msg.value, block.timestamp);
    }

    function submitClaim(string calldata _claimId, uint256 _amount, string calldata _hospitalTxnId) external {
        require(registeredBuyer[msg.sender], "Not registered buyer");
        claims[_claimId] = Claim(_claimId, msg.sender, _amount, _hospitalTxnId, false, block.timestamp);
        emit ClaimSubmitted(msg.sender, _claimId, _amount);
    }

    function verifyClaim(string calldata _claimId, bool _status) external onlyAdmin {
        Claim storage c = claims[_claimId];
        c.verified = _status;
        emit ClaimVerified(_claimId, _status);
    }
}