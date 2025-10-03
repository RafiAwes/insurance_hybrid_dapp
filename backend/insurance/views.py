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
                    'created_at': claim.created_at
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
    """Submit a claim - placeholder function"""
    return Response({'message': 'submit_claim function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
def claim_history(request):
    """Get claim history - placeholder function"""
    return Response({'message': 'claim_history function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
def verify_claim(request):
    """Verify a claim - placeholder function"""
    return Response({'message': 'verify_claim function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

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
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'admin': {
                'id': str(admin.id),
                'email': admin.email,
                'full_name': admin.full_name,
                'wallet_verified': False  # Will be verified in next step
            }
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
    """Get claims for admin - placeholder function"""
    return Response({'message': 'admin_get_claims function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
def admin_get_buyers(request):
    """Get buyers for admin - placeholder function"""
    return Response({'message': 'admin_get_buyers function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['POST'])
def admin_update_claim_status(request):
    """Update claim status - placeholder function"""
    return Response({'message': 'admin_update_claim_status function - implement as needed'}, status=status.HTTP_501_NOT_IMPLEMENTED)

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
            }
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