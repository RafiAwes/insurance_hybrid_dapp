from web3 import Web3
import json
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from .models import Buyer, Claim, Premium, Policy

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
    """Handle PremiumPaid event and store in database"""
    print(f"[PREMIUM EVENT] Processing PremiumPaid event...")

    try:
        args = event['args']
        buyer_address = args['buyer']
        amount_wei = args['amount']
        timestamp = args['timestamp']

        print(f"[PREMIUM EVENT] Buyer: {buyer_address}")
        print(f"[PREMIUM EVENT] Amount: {amount_wei / 10**18} ETH ({amount_wei} wei)")
        print(f"[PREMIUM EVENT] Timestamp: {timestamp}")

        # Get transaction details
        tx_hash = event['transactionHash'].hex()
        block_number = event['blockNumber']

        print(f"[PREMIUM EVENT] Transaction hash: {tx_hash}")
        print(f"[PREMIUM EVENT] Block number: {block_number}")

        # Get transaction receipt for additional details
        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
        tx_details = w3.eth.get_transaction(tx_hash)

        gas_used = tx_receipt['gasUsed']
        gas_price = tx_details['gasPrice']

        print(f"[PREMIUM EVENT] Gas used: {gas_used}, Gas price: {gas_price}")

        # Find buyer
        print(f"[PREMIUM EVENT] Looking up buyer in database...")
        buyer = Buyer.objects.get(wallet_address=buyer_address)
        print(f"[PREMIUM EVENT] Found buyer: {buyer.full_name} ({buyer.email})")

        # Get or create policy for this buyer
        policy, created = Policy.objects.get_or_create(
            buyer=buyer,
            defaults={
                'policy_number': f'POL-{buyer.id.hex[:8].upper()}',
                'monthly_premium': float(amount_wei) / 10**18,
                'status': 'active'
            }
        )

        if created:
            print(f"[PREMIUM EVENT] Created new policy: {policy.policy_number}")
        else:
            print(f"[PREMIUM EVENT] Using existing policy: {policy.policy_number}")

        # Convert timestamp to datetime
        block_datetime = timezone.make_aware(datetime.fromtimestamp(timestamp))
        print(f"[PREMIUM EVENT] Block timestamp: {block_datetime}")

        # Create premium record
        premium, created = Premium.objects.get_or_create(
            transaction_hash=tx_hash,
            defaults={
                'buyer': buyer,
                'policy': policy,
                'amount_eth': float(amount_wei) / 10**18,
                'amount_wei': str(amount_wei),
                'block_number': block_number,
                'block_timestamp': block_datetime,
                'gas_used': gas_used,
                'gas_price': str(gas_price),
                'status': 'confirmed'
            }
        )

        if created:
            print(f"[PREMIUM EVENT] Created new premium record")
            # Update buyer's premium tracking
            buyer.total_premiums_paid = F('total_premiums_paid') + premium.amount_eth
            buyer.last_premium_payment = block_datetime
            buyer.premium_payment_count = F('premium_payment_count') + 1
            buyer.save(update_fields=['total_premiums_paid', 'last_premium_payment', 'premium_payment_count'])

            print(f"[PREMIUM EVENT] Updated buyer payment history:")
            print(f"   Total paid: {buyer.total_premiums_paid} ETH")
            print(f"   Payment count: {buyer.premium_payment_count}")
            print(f"   Last payment: {buyer.last_premium_payment}")
            
            # Upload premium data to Storacha
            try:
                from .services.storacha_node_service import StorachaNodeService
                storacha_service = StorachaNodeService()
                
                # Prepare buyer data
                buyer_data = {
                    'id': str(buyer.id),
                    'full_name': buyer.full_name,
                    'email': buyer.email,
                    'wallet_address': buyer.wallet_address,
                    'national_id': buyer.national_id
                }
                
                # Prepare premium data
                premium_data = {
                    'transaction_hash': premium.transaction_hash,
                    'amount_eth': str(premium.amount_eth),
                    'block_timestamp': premium.block_timestamp.isoformat(),
                    'status': premium.status
                }
                
                # Upload to Storacha
                cid = storacha_service.upload_premium_data(buyer_data, premium_data)
                
                # Save CID to premium
                premium.storacha_cid = cid
                premium.save(update_fields=['storacha_cid'])
                
                print(f"[PREMIUM EVENT] Premium data uploaded to Storacha with CID: {cid}")
            except Exception as e:
                print(f"[PREMIUM EVENT] Error uploading premium to Storacha: {str(e)}")
        else:
            print(f"[PREMIUM EVENT] Premium payment already exists: {tx_hash}")

    except Buyer.DoesNotExist:
        print(f"[PREMIUM EVENT] ERROR: Buyer {buyer_address} not found in database!")
        print(f"   Available buyers: {list(Buyer.objects.values_list('wallet_address', flat=True))}")
        print(f"   Please ensure the buyer wallet address matches the database")

    except Exception as e:
        print(f"[PREMIUM EVENT] ERROR: Error processing premium payment {tx_hash}: {str(e)}")
        import traceback
        traceback.print_exc()


def listen_to_events():
    print("[EVENT LISTENER] Starting event listener...")
    print(f"[EVENT LISTENER] Contract address: {settings.CONTRACT_ADDRESS}")
    print(f"[EVENT LISTENER] RPC URL: {settings.HARDHAT_RPC_URL}")

    if not settings.CONTRACT_ADDRESS:
        print("[EVENT LISTENER] ERROR: Contract address not set. Cannot listen to events.")
        return

    try:
        # Test connection to blockchain
        block_number = w3.eth.block_number
        print(f"[EVENT LISTENER] Connected to blockchain. Current block: {block_number}")

        # Create event filters
        print("[EVENT LISTENER] Creating event filters...")
        claim_submitted_filter = contract.events.ClaimSubmitted.create_filter(from_block='latest')
        claim_verified_filter = contract.events.ClaimVerified.create_filter(from_block='latest')
        premium_paid_filter = contract.events.PremiumPaid.create_filter(from_block='latest')
        print("[EVENT LISTENER] Event filters created successfully")

    except Exception as e:
        print(f"[EVENT LISTENER] ERROR: Failed to initialize event filters: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("[EVENT LISTENER] Listening for events... (polling every 2 seconds)")

    while True:
        try:
            # Check for new events
            claim_events = claim_submitted_filter.get_new_entries()
            verified_events = claim_verified_filter.get_new_entries()
            premium_events = premium_paid_filter.get_new_entries()

            if claim_events:
                print(f"[EVENT LISTENER] Found {len(claim_events)} claim submitted events")
                for event in claim_events:
                    handle_claim_submitted(event)

            if verified_events:
                print(f"[EVENT LISTENER] Found {len(verified_events)} claim verified events")
                for event in verified_events:
                    handle_claim_verified(event)

            if premium_events:
                print(f"[EVENT LISTENER] Found {len(premium_events)} premium paid events")
                for event in premium_events:
                    handle_premium_paid(event)

            # Only print heartbeat if no events found
            if not claim_events and not verified_events and not premium_events:
                print(".", end="", flush=True)

        except Exception as e:
            print(f"[EVENT LISTENER] ERROR: Error polling events: {str(e)}")
            print("[EVENT LISTENER] Retrying in 5 seconds...")
            time.sleep(5)
            continue

        time.sleep(2)  # Poll every 2 seconds


if __name__ == "__main__":
    listen_to_events()