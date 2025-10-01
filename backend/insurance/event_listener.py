from web3 import Web3
import json
import time
from django.conf import settings
from .models import Buyer, Claim

w3 = Web3(Web3.HTTPProvider(settings.HARDHAT_RPC_URL))

# Load ABI - replace with actual ABI from Hardhat artifacts
HEALTH_INSURANCE_ABI = json.loads('''[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"buyer","type":"address"},{"indexed":false,"internalType":"string","name":"claimId","type":"string"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"ClaimSubmitted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"claimId","type":"string"},{"indexed":false,"internalType":"bool","name":"status","type":"bool"}],"name":"ClaimVerified","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"buyer","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"PremiumPaid","type":"event"}]''')

contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=HEALTH_INSURANCE_ABI)


def handle_claim_submitted(event):
    args = event['args']
    claim_id = args['claimId']
    buyer_address = args['buyer']
    amount = args['amount']

    # Sync with DB - find or create claim
    try:
        buyer = Buyer.objects.get(wallet_address=buyer_address)
        Claim.objects.update_or_create(
            claim_id=claim_id,
            defaults={
                'buyer': buyer,
                'claim_amount': amount / 10**18,  # Convert from wei
                'claim_status': 'submitted',
            }
        )
        print(f"Claim {claim_id} synced for buyer {buyer_address}")
    except Buyer.DoesNotExist:
        print(f"Buyer {buyer_address} not found for claim {claim_id}")


def handle_claim_verified(event):
    args = event['args']
    claim_id = args['claimId']
    status = args['status']

    try:
        claim = Claim.objects.get(claim_id=claim_id)
        claim.claim_status = 'verified' if status else 'rejected'
        claim.save()
        print(f"Claim {claim_id} verified as {claim.claim_status}")
    except Claim.DoesNotExist:
        print(f"Claim {claim_id} not found for verification")


def handle_premium_paid(event):
    args = event['args']
    buyer_address = args['buyer']
    amount = args['amount']

    # Update policy or create premium record if needed
    try:
        buyer = Buyer.objects.get(wallet_address=buyer_address)
        # Assume we have a Premium model or update policy status
        print(f"Premium paid by {buyer_address}: {amount / 10**18} ETH")
    except Buyer.DoesNotExist:
        print(f"Buyer {buyer_address} not found for premium payment")


def listen_to_events():
    if not settings.CONTRACT_ADDRESS:
        print("Contract address not set. Cannot listen to events.")
        return

    # Create event filters
    claim_submitted_filter = contract.events.ClaimSubmitted.createFilter(fromBlock='latest')
    claim_verified_filter = contract.events.ClaimVerified.createFilter(fromBlock='latest')
    premium_paid_filter = contract.events.PremiumPaid.createFilter(fromBlock='latest')

    while True:
        # Check for new events
        for event in claim_submitted_filter.get_new_entries():
            handle_claim_submitted(event)
        for event in claim_verified_filter.get_new_entries():
            handle_claim_verified(event)
        for event in premium_paid_filter.get_new_entries():
            handle_premium_paid(event)
        
        time.sleep(2)  # Poll every 2 seconds


if __name__ == "__main__":
    listen_to_events()