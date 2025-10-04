from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Buyer, Claim, Admin
from .serializers import BuyerSerializer, ClaimSerializer
import json
import PyPDF2
import re
import requests
from .services.storacha_node_service import StorachaNodeService

# Initialize Storacha service
storacha_service = StorachaNodeService()


@api_view(['POST'])
def store_claim_document(request):
    """
    Store claim document CID in buyer's record
    Expected payload: {
        "buyer_address": "0x...",
        "claim_id": "claim-123",
        "cid": "bafybei...",
        "filename": "medical_report.pdf",
        "file_size": 1024000
    }
    """
    try:
        data = request.data
        buyer_address = data.get('buyer_address')
        claim_id = data.get('claim_id')
        cid = data.get('cid')
        filename = data.get('filename', 'document')
        file_size = data.get('file_size', 0)
        
        if not all([buyer_address, claim_id, cid]):
            return Response({
                'error': 'Missing required fields: buyer_address, claim_id, cid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get buyer
        buyer = get_object_or_404(Buyer, wallet_address=buyer_address)
        
        # Create claim document entry
        claim_doc = {
            'claim_id': claim_id,
            'cid': cid,
            'filename': filename,
            'file_size': file_size,
            'timestamp': timezone.now().isoformat(),
            'status': 'submitted'
        }
        
        # Add to buyer's claim_documents list
        if not buyer.claim_documents:
            buyer.claim_documents = []
        
        buyer.claim_documents.append(claim_doc)
        buyer.save(update_fields=['claim_documents'])
        
        return Response({
            'success': True,
            'message': 'Claim document stored successfully',
            'claim_id': claim_id,
            'cid': cid
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to store claim document: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_buyer_history(request, wallet_address):
    """
    Get buyer's premium payment and claim history
    """
    try:
        buyer = get_object_or_404(Buyer, wallet_address=wallet_address)
        
        # Get premium payments
        premiums = buyer.premiums.all().order_by('-created_at')
        
        # Get claims
        claims = buyer.claim_set.all().order_by('-created_at')
        
        history_data = {
            'buyer_info': {
                'wallet_address': buyer.wallet_address,
                'full_name': buyer.full_name,
                'email': buyer.email,
                'total_premiums_paid': str(buyer.total_premiums_paid),
                'premium_payment_count': buyer.premium_payment_count,
                'last_premium_payment': buyer.last_premium_payment
            },
            'premium_payments': [
                {
                    'amount_eth': str(premium.amount_eth),
                    'transaction_hash': premium.transaction_hash,
                    'block_timestamp': premium.block_timestamp,
                    'status': premium.status
                }
                for premium in premiums
            ],
            'claims': [
                {
                    'claim_id': claim.claim_id,
                    'amount': str(claim.claim_amount),
                    'status': claim.claim_status,
                    'description': claim.claim_description,
                    'created_at': claim.created_at,
                    'hospital_transaction_id': claim.hospital_transaction_id,
                    'verified_at': claim.verified_at,
                    'accepted_at': claim.accepted_at,
                    'status_message': get_claim_status_message(claim)
                }
                for claim in claims
            ],
            'claim_documents': buyer.claim_documents or []
        }
        
        return Response(history_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get buyer history: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_claim_status_message(claim):
    """
    Generate a user-friendly status message for claims
    """
    status_messages = {
        'submitted': 'Claim submitted and pending verification',
        'verified': 'Claim verified successfully',
        'unverified': 'Claim could not be verified',
        'accepted': '✅ Claim approved',
        'not_approved': '❌ Claim not approved',
        'rejected': '❌ Claim rejected',
        'paid': '💰 Claim paid'
    }
    
    return status_messages.get(claim.claim_status, claim.claim_status)

@api_view(['GET'])
def get_buyer_claims(request, wallet_address):
    """
    Get buyer's claim documents from their record
    """
    try:
        buyer = get_object_or_404(Buyer, wallet_address=wallet_address)
        
        return Response({
            'buyer_address': buyer.wallet_address,
            'claim_documents': buyer.claim_documents or []
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get buyer claims: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Legacy API functions (placeholders - implement as needed)
@api_view(['POST'])
def add_buyer(request):
    """Add a new buyer - placeholder function"""
    return Response({'message': 'add_buyer function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
def submit_claim(request):
    """
    Submit a claim with PDF file upload
    Expected payload: {
        "buyer_address": "0x...",
        "claim_description": "Medical treatment",
        "file": PDF file
    }
    """
    try:
        buyer_address = request.data.get('buyer_address')
        claim_description = request.data.get('claim_description')
        file = request.FILES.get('file')
        
        if not all([buyer_address, claim_description, file]):
            return Response({
                'error': 'Missing required fields: buyer_address, claim_description, file'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        if not file.name.endswith('.pdf'):
            return Response({
                'error': 'Only PDF files are allowed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get buyer
        buyer = get_object_or_404(Buyer, wallet_address=buyer_address)
        
        # Extract claim data from PDF
        claim_data = extract_claim_data_from_pdf(file)
        transaction_id = claim_data.get('transaction_id')
        pdf_amount = claim_data.get('amount')
        
        if not transaction_id:
            return Response({
                'error': 'Could not extract transaction ID from PDF file'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use amount from PDF if available, otherwise use form data
        claim_amount = pdf_amount if pdf_amount is not None else request.data.get('claim_amount', '0')
        
        # Create claim
        claim_id = f"CLM-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        claim = Claim.objects.create(
            claim_id=claim_id,
            buyer=buyer,
            claim_amount=claim_amount,
            claim_description=claim_description,
            hospital_transaction_id=transaction_id,
            claim_status='submitted'
        )
        
        # Verify transaction ID
        verification_result = verify_transaction_id(transaction_id)
        claim_status = 'verified' if verification_result.get('success', False) else 'unverified'
        claim.claim_status = claim_status
        if claim_status == 'verified':
            claim.verified_at = timezone.now()
        claim.save()
        
        # Upload claim data to Storacha
        try:
            # Prepare buyer data
            buyer_data = {
                'id': str(buyer.id),
                'full_name': buyer.full_name,
                'email': buyer.email,
                'wallet_address': buyer.wallet_address,
                'national_id': buyer.national_id
            }
            
            # Prepare claim data
            claim_data = {
                'claim_id': claim.claim_id,
                'amount': str(claim.claim_amount),
                'status': claim.claim_status,
                'description': claim.claim_description,
                'created_at': claim.created_at.isoformat()
            }
            
            # Upload to Storacha
            cid = storacha_service.upload_claim_data(buyer_data, claim_data)
            
            # Save CID to claim
            claim.storacha_cid = cid
            claim.save(update_fields=['storacha_cid'])
        except Exception as e:
            print(f"Error uploading claim to Storacha: {str(e)}")
            # Continue anyway - the claim was created successfully
        
        return Response({
            'success': True,
            'message': 'Claim submitted successfully',
            'claim_id': claim_id,
            'transaction_id': transaction_id,
            'claim_amount': str(claim_amount),
            'verification_status': claim_status,
            'storacha_cid': claim.storacha_cid
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to submit claim: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def extract_transaction_id_from_pdf(file):
    """
    Extract transaction ID from PDF file content
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Look for transaction ID pattern (you can adjust this regex based on your PDF format)
        # This looks for patterns like "Transaction ID: XXX" or "TXN: XXX"
        patterns = [
            r'Transaction\s*ID[:\s]*([A-Za-z0-9\-_]+)',
            r'TXN[:\s]*([A-Za-z0-9\-_]+)',
            r'Transaction[:\s]*([A-Za-z0-9\-_]+)',
            r'ID[:\s]*([A-Za-z0-9\-_]+)'
        ]
        
        transaction_id = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                transaction_id = match.group(1)
                break
        
        return transaction_id
    except Exception as e:
        print(f"Error extracting transaction ID from PDF: {str(e)}")
        return None


def extract_claim_data_from_pdf(file):
    """
    Extract claim data (transaction ID and amount) from PDF file content
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Extract transaction ID
        transaction_id_patterns = [
            r'Transaction\s*ID[:\s]*([A-Za-z0-9\-_]+)',
            r'TXN[:\s]*([A-Za-z0-9\-_]+)',
            r'Transaction[:\s]*([A-Za-z0-9\-_]+)',
            r'ID[:\s]*([A-Za-z0-9\-_]+)'
        ]
        
        transaction_id = None
        for pattern in transaction_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                transaction_id = match.group(1)
                break
        
        # Extract amount
        amount_patterns = [
            r'Amount[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'Total[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'Claim\s*Amount[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)'
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')  # Remove commas
                try:
                    amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        return {
            'transaction_id': transaction_id,
            'amount': amount
        }
    except Exception as e:
        print(f"Error extracting claim data from PDF: {str(e)}")
        return {
            'transaction_id': None,
            'amount': None
        }


@api_view(['POST'])
def verify_claim(request):
    """
    Verify a claim by checking transaction ID against billing API
    Expected payload: {
        "claim_id": "CLM-20250101120000"
    }
    """
    try:
        claim_id = request.data.get('claim_id')
        
        if not claim_id:
            return Response({
                'error': 'Missing required field: claim_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get claim
        claim = get_object_or_404(Claim, claim_id=claim_id)
        
        # Verify transaction ID
        verification_result = verify_transaction_id(claim.hospital_transaction_id)
        
        # Update claim status based on verification
        if verification_result.get('success', False):
            claim.claim_status = 'verified'
            message = 'Claim verified successfully'
        else:
            claim.claim_status = 'unverified'
            message = 'Claim could not be verified'
        
        claim.save()
        
        return Response({
            'success': True,
            'message': message,
            'verification_result': verification_result,
            'claim_status': claim.claim_status
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to verify claim: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def verify_transaction_id(transaction_id):
    """
    Verify transaction ID against billing API
    """
    try:
        # Call the verification API
        url = f"http://127.0.0.1:8080/billing/api/verify-transaction/{transaction_id}/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Check if transaction is successful based on status field
            # Handle different possible success indicators
            is_success = (
                data.get('status') == 'paid' or 
                data.get('success') == True or
                data.get('status') == 'success'
            )
            return {
                'success': is_success,
                'data': data
            }
        else:
            return {
                'success': False,
                'error': f'API returned status code {response.status_code}'
            }
    except requests.exceptions.RequestException as e:
        # If the primary API is not available, try the fallback (8000)
        try:
            url = f"http://127.0.0.1:8000/billing/api/verify-transaction/{transaction_id}/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Check if transaction is successful based on status field
                is_success = (
                    data.get('status') == 'paid' or 
                    data.get('success') == True or
                    data.get('status') == 'success'
                )
                return {
                    'success': is_success,
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned status code {response.status_code}'
                }
        except requests.exceptions.RequestException as fallback_e:
            return {
                'success': False,
                'error': f'API request failed on both ports: {str(e)} and {str(fallback_e)}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


@api_view(['GET'])
def claim_history(request):
    """Get claim history - placeholder function"""
    return Response({'message': 'claim_history function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
def upload_transaction_record(request):
    """Upload transaction record - placeholder function"""
    return Response({'message': 'upload_transaction_record function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
def upload_claim_doc(request):
    """Upload claim document - placeholder function"""
    return Response({'message': 'upload_claim_doc function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

# Admin authentication functions
@api_view(['POST'])
def admin_register(request):
    """Admin registration - placeholder function"""
    return Response({'message': 'admin_register function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@csrf_exempt
@api_view(['POST'])
def admin_login(request):
    """Admin login with email and password"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find admin by email
        try:
            admin = Admin.objects.get(email=email, is_active=True)
        except Admin.DoesNotExist:
            return Response({
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check password
        if not admin.check_password(password):
            return Response({
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Update last login
        admin.last_login = timezone.now()
        admin.save(update_fields=['last_login'])
        
        # Login to Storacha automatically
        storacha_result = login_to_storacha(admin.email)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'admin': {
                'id': str(admin.id),
                'email': admin.email,
                'full_name': admin.full_name,
                'wallet_verified': False  # Will be verified in next step
            },
            'storacha_login': storacha_result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def admin_verify_wallet(request):
    """Admin wallet verification"""
    try:
        wallet_address = request.data.get('wallet_address')
        admin_id = request.data.get('admin_id')
        
        if not wallet_address or not admin_id:
            return Response({
                'error': 'Wallet address and admin ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get admin
        try:
            admin = Admin.objects.get(id=admin_id, is_active=True)
        except Admin.DoesNotExist:
            return Response({
                'error': 'Admin not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if wallet address matches expected admin wallet
        expected_admin_wallet = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Hardhat account #0
        
        if wallet_address.lower() != expected_admin_wallet.lower():
            return Response({
                'error': f'Invalid admin wallet. Expected: {expected_admin_wallet}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': True,
            'message': 'Wallet verified successfully',
            'admin': {
                'id': str(admin.id),
                'email': admin.email,
                'full_name': admin.full_name,
                'wallet_address': wallet_address,
                'wallet_verified': True
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Wallet verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def admin_get_claims(request):
    """Get all claims for admin dashboard"""
    try:
        # Get all claims ordered by creation date
        claims = Claim.objects.select_related('buyer').all().order_by('-created_at')
        
        claims_data = [
            {
                'claim_id': claim.claim_id,
                'buyer': claim.buyer.wallet_address,
                'buyer_name': claim.buyer.full_name,
                'claim_amount': str(claim.claim_amount),
                'claim_description': claim.claim_description,
                'claim_status': claim.claim_status,
                'created_at': claim.created_at,
                'hospital_transaction_id': claim.hospital_transaction_id,
                'verified_at': claim.verified_at,
                'accepted_at': claim.accepted_at
            }
            for claim in claims
        ]
        
        return Response(claims_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get claims: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def admin_get_buyers(request):
    """Get all buyers for admin dashboard"""
    try:
        # Get all buyers ordered by creation date
        buyers = Buyer.objects.all().order_by('-created_at')
        
        buyers_data = [
            {
                'id': str(buyer.id),
                'wallet_address': buyer.wallet_address,
                'name': buyer.full_name,
                'email': buyer.email,
                'created_at': buyer.created_at,
                'is_active': buyer.is_active,
                'last_login': buyer.last_login,
                'total_premiums_paid': str(buyer.total_premiums_paid),
                'premium_payment_count': buyer.premium_payment_count
            }
            for buyer in buyers
        ]
        
        return Response(buyers_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to get buyers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def admin_update_claim_status(request):
    """Update claim status"""
    try:
        claim_id = request.data.get('claim_id')
        new_status = request.data.get('status')  # 'accepted' or 'not_approved' or 'rejected'
        admin_id = request.data.get('admin_id')
        
        if not all([claim_id, new_status, admin_id]):
            return Response({
                'error': 'Missing required fields: claim_id, status, admin_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        if new_status not in ['accepted', 'not_approved', 'rejected']:
            return Response({
                'error': 'Invalid status. Must be "accepted", "not_approved", or "rejected"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get admin
        admin = get_object_or_404(Admin, id=admin_id, is_active=True)
        
        # Get claim
        claim = get_object_or_404(Claim, claim_id=claim_id)
        
        # Update claim status
        old_status = claim.claim_status
        claim.claim_status = new_status
        if new_status in ['accepted', 'rejected']:
            claim.accepted_at = timezone.now()
        claim.save()
        
        # If claim is accepted, store it on blockchain and Storacha
        if new_status == 'accepted':
            try:
                # Store claim data in blockchain
                store_claim_on_blockchain(claim)
                
                # Store claim data in Storacha
                store_claim_in_storacha(claim)
            except Exception as e:
                print(f"Error storing claim data: {str(e)}")
                # We don't return an error here because the status update was successful
                # but we log the error for debugging
        
        return Response({
            'success': True,
            'message': f'Claim status updated from {old_status} to {new_status}',
            'claim_id': claim_id,
            'new_status': new_status
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to update claim status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def store_claim_in_storacha(claim):
    """
    Store claim data in Storacha
    """
    try:
        # Prepare buyer data
        buyer_data = {
            'id': str(claim.buyer.id),
            'full_name': claim.buyer.full_name,
            'email': claim.buyer.email,
            'wallet_address': claim.buyer.wallet_address,
            'national_id': claim.buyer.national_id
        }
        
        # Prepare claim data
        claim_data = {
            'claim_id': claim.claim_id,
            'amount': str(claim.claim_amount),
            'status': claim.claim_status,
            'description': claim.claim_description,
            'created_at': claim.created_at.isoformat()
        }
        
        # Upload to Storacha
        cid = storacha_service.upload_claim_data(buyer_data, claim_data)
        
        # Save CID to claim
        claim.storacha_cid = cid
        claim.save(update_fields=['storacha_cid'])
        
        print(f"✅ Claim {claim.claim_id} stored in Storacha with CID: {cid}")
        return cid
    except Exception as e:
        print(f"Error storing claim in Storacha: {str(e)}")
        raise e


def store_claim_on_blockchain(claim):
    """
    Store claim data on blockchain
    """
    try:
        # In a real implementation, this would interact with the blockchain
        # For now, we'll just log that it would happen
        print(f"Storing claim {claim.claim_id} on blockchain")
        print(f"Claim amount: {claim.claim_amount}")
        print(f"Buyer: {claim.buyer.wallet_address}")
        print(f"Transaction ID: {claim.hospital_transaction_id}")
        
        # This is where you would call the blockchain contract
        # For example:
        # from web3 import Web3
        # w3 = Web3(Web3.HTTPProvider(settings.HARDHAT_RPC_URL))
        # contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=HEALTH_INSURANCE_ABI)
        # result = contract.functions.storeClaim(
        #     claim.claim_id,
        #     int(claim.claim_amount * 10**18),  # Convert to wei
        #     claim.hospital_transaction_id
        # ).transact({'from': admin_wallet_address})
        
        return True
    except Exception as e:
        print(f"Error storing claim on blockchain: {str(e)}")
        raise e


def login_to_storacha(email):
    """
    Login to Storacha and return session info
    """
    try:
        from .services.storacha_node_service import StorachaNodeService
        storacha_service = StorachaNodeService()
        
        # Login to Storacha
        result = storacha_service.login(email)
        
        if result.get('success'):
            print(f"✅ Storacha login successful for {email}")
            return {
                'success': True,
                'message': 'Storacha login successful',
                'email': email
            }
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Storacha login failed for {email}: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    except Exception as e:
        print(f"Error logging into Storacha: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


# Buyer authentication functions
@api_view(['POST'])
def buyer_register(request):
    """Buyer registration - placeholder function"""
    return Response({'message': 'buyer_register function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@csrf_exempt
@api_view(['POST'])
def buyer_login(request):
    """Buyer login with email and password"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        print(f"🔍 [DEBUG] Buyer login attempt - Email: {email}")
        
        if not email or not password:
            print("❌ [DEBUG] Missing email or password")
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if any buyers exist
        buyer_count = Buyer.objects.count()
        print(f"🔍 [DEBUG] Total buyers in database: {buyer_count}")
        
        # Find buyer by email
        try:
            buyer = Buyer.objects.get(email=email, is_active=True)
            print(f"✅ [DEBUG] Found buyer: {buyer.full_name} ({buyer.email})")
        except Buyer.DoesNotExist:
            print(f"❌ [DEBUG] No buyer found with email: {email}")
            # List all buyers for debugging
            all_buyers = Buyer.objects.all().values_list('email', 'is_active')
            print(f"🔍 [DEBUG] All buyers: {list(all_buyers)}")
            return Response({
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check password
        print(f"🔍 [DEBUG] Checking password for buyer: {buyer.email}")
        if not buyer.check_password(password):
            print("❌ [DEBUG] Password check failed")
            return Response({
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        print("✅ [DEBUG] Password check passed")
        
        # Update last login
        buyer.last_login = timezone.now()
        buyer.save(update_fields=['last_login'])
        
        # Login to Storacha automatically
        storacha_result = login_to_storacha(buyer.email)
        
        print(f"✅ [DEBUG] Login successful for buyer: {buyer.email}")
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'buyer': {
                'id': str(buyer.id),
                'email': buyer.email,
                'full_name': buyer.full_name,
                'wallet_address': buyer.wallet_address,
                'wallet_verified': False  # Will be verified in next step
            },
            'storacha_login': storacha_result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ [DEBUG] Login exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def buyer_verify_wallet(request):
    """Buyer wallet verification"""
    try:
        wallet_address = request.data.get('wallet_address')
        buyer_id = request.data.get('buyer_id')
        
        if not wallet_address or not buyer_id:
            return Response({
                'error': 'Wallet address and buyer ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get buyer
        try:
            buyer = Buyer.objects.get(id=buyer_id, is_active=True)
        except Buyer.DoesNotExist:
            return Response({
                'error': 'Buyer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if wallet address matches buyer's registered wallet
        if wallet_address.lower() != buyer.wallet_address.lower():
            return Response({
                'error': f'Invalid wallet. Expected: {buyer.wallet_address}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': True,
            'message': 'Wallet verified successfully',
            'buyer': {
                'id': str(buyer.id),
                'email': buyer.email,
                'full_name': buyer.full_name,
                'wallet_address': wallet_address,
                'wallet_verified': True
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Wallet verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Add new API endpoints for Storacha integration

@api_view(['POST'])
def upload_claim_to_storacha(request):
    """
    Upload claim data to Storacha
    Expected payload: {
        "claim_id": "CLM-20250101120000"
    }
    """
    try:
        claim_id = request.data.get('claim_id')
        
        if not claim_id:
            return Response({
                'error': 'Missing required field: claim_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get claim
        claim = get_object_or_404(Claim, claim_id=claim_id)
        
        # Store claim data in Storacha
        cid = store_claim_in_storacha(claim)
        
        return Response({
            'success': True,
            'message': 'Claim data uploaded to Storacha successfully',
            'claim_id': claim_id,
            'cid': cid
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to upload claim to Storacha: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def upload_premium_to_storacha(request):
    """
    Upload premium data to Storacha
    Expected payload: {
        "premium_id": "premium-uuid"
    }
    """
    try:
        premium_id = request.data.get('premium_id')
        
        if not premium_id:
            return Response({
                'error': 'Missing required field: premium_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get premium
        premium = get_object_or_404(Premium, id=premium_id)
        
        # Prepare buyer data
        buyer_data = {
            'id': str(premium.buyer.id),
            'full_name': premium.buyer.full_name,
            'email': premium.buyer.email,
            'wallet_address': premium.buyer.wallet_address,
            'national_id': premium.buyer.national_id
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
        
        return Response({
            'success': True,
            'message': 'Premium data uploaded to Storacha successfully',
            'premium_id': str(premium_id),
            'cid': cid
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to upload premium to Storacha: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def fetch_accepted_claims(request):
    """
    Fetch all accepted claims with their Storacha CIDs
    """
    try:
        # Get all accepted claims
        claims = Claim.objects.filter(claim_status='accepted').select_related('buyer').order_by('-created_at')
        
        claims_data = []
        for claim in claims:
            claims_data.append({
                'claim_id': claim.claim_id,
                'buyer_name': claim.buyer.full_name,
                'buyer_wallet': claim.buyer.wallet_address,
                'amount': str(claim.claim_amount),
                'status': claim.claim_status,
                'description': claim.claim_description,
                'created_at': claim.created_at.isoformat(),
                'storacha_cid': claim.storacha_cid,
                'storacha_url': f'https://{claim.storacha_cid}.ipfs.storacha.link' if claim.storacha_cid else None
            })
        
        return Response(claims_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch accepted claims: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def fetch_buyer_premiums(request, wallet_address):
    """
    Fetch all premiums for a buyer with their Storacha CIDs
    """
    try:
        # Get buyer
        buyer = get_object_or_404(Buyer, wallet_address=wallet_address)
        
        # Get all premiums for this buyer
        premiums = Premium.objects.filter(buyer=buyer).order_by('-created_at')
        
        premiums_data = []
        for premium in premiums:
            premiums_data.append({
                'id': str(premium.id),
                'transaction_hash': premium.transaction_hash,
                'amount_eth': str(premium.amount_eth),
                'block_timestamp': premium.block_timestamp.isoformat(),
                'status': premium.status,
                'storacha_cid': premium.storacha_cid,
                'storacha_url': f'https://{premium.storacha_cid}.ipfs.storacha.link' if premium.storacha_cid else None
            })
        
        return Response(premiums_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to fetch buyer premiums: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
