from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Buyer, Policy, Claim, HospitalTxnRecord, ClaimDoc, Admin
from .serializers import (
    BuyerSerializer, PolicySerializer, ClaimSerializer,
    HospitalTxnRecordSerializer, ClaimDocSerializer,
    AdminSerializer, AdminLoginSerializer, AdminWalletVerificationSerializer
)
from django.conf import settings
from web3 import Web3
from django.conf import settings
import uuid
import json


w3 = Web3(Web3.HTTPProvider(settings.HARDHAT_RPC_URL))

# Temporary minimal ABI to fix JSON parsing error - replace with full ABI after compilation
HEALTH_INSURANCE_ABI = [
    {
        "inputs": [],
        "name": "admin",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "buyer", "type": "address"}],
        "name": "registerBuyer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_claimId", "type": "string"},
            {"internalType": "uint256", "name": "_amount", "type": "uint256"},
            {"internalType": "string", "name": "_hospitalTxnId", "type": "string"}
        ],
        "name": "submitClaim",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_claimId", "type": "string"},
            {"internalType": "bool", "name": "_status", "type": "bool"}
        ],
        "name": "verifyClaim",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Initialize contract only if valid address is provided
contract = None
if settings.CONTRACT_ADDRESS and settings.CONTRACT_ADDRESS.startswith('0x') and len(settings.CONTRACT_ADDRESS) == 42:
    try:
        contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=HEALTH_INSURANCE_ABI)
    except Exception as e:
        print(f"Warning: Could not initialize contract: {e}")
        contract = None


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Assume admin authentication
def add_buyer(request):
    serializer = BuyerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_claim(request):
    buyer_address = request.data.get('wallet_address')
    try:
        buyer = Buyer.objects.get(wallet_address=buyer_address)
    except Buyer.DoesNotExist:
        return Response({'error': 'Buyer not found'}, status=status.HTTP_404_NOT_FOUND)

    claim_id = str(uuid.uuid4())
    claim_data = {
        'claim_id': claim_id,
        'buyer': buyer.id,
        'claim_amount': request.data.get('amount'),
        'claim_description': request.data.get('description', ''),
        'hospital_transaction_id': request.data.get('hospitalTransactionId', ''),
    }
    serializer = ClaimSerializer(data=claim_data)
    if serializer.is_valid():
        claim = serializer.save()

        # Call smart contract
        if contract is not None:
            try:
                txn = contract.functions.submitClaim(
                    claim_id,
                    w3.to_wei(claim_data['claim_amount'], 'ether'),
                    claim_data['hospital_transaction_id']
                ).transact({'from': buyer_address})
                w3.eth.wait_for_transaction_receipt(txn)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def claim_history(request):
    buyer_address = request.query_params.get('wallet_address')
    try:
        buyer = Buyer.objects.get(wallet_address=buyer_address)
        claims = Claim.objects.filter(buyer=buyer).order_by('-created_at')
        serializer = ClaimSerializer(claims, many=True)
        return Response(serializer.data)
    except Buyer.DoesNotExist:
        return Response({'error': 'Buyer not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Admin
def verify_claim(request):
    claim_id = request.data.get('claimId')
    status_verified = request.data.get('status', True)
    try:
        claim = Claim.objects.get(claim_id=claim_id)
        claim.claim_status = 'verified' if status_verified else 'rejected'
        claim.save()

        # Call smart contract to verify
        if contract is not None:
            try:
                txn = contract.functions.verifyClaim(
                    claim_id,
                    status_verified
                ).transact({'from': 'admin_address'})  # Use admin wallet
                w3.eth.wait_for_transaction_receipt(txn)
            except Exception as e:
                print(f"Warning: Could not verify claim on blockchain: {e}")

        serializer = ClaimSerializer(claim)
        return Response(serializer.data)
    except Claim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Hospital
def upload_transaction_record(request):
    hospital_txn_id = request.data.get('hospitalTransactionId')
    encrypted_blob = request.data.get('encryptedBlob', '')
    cid = request.data.get('storachaCid', '')

    data = {
        'hospitalTransactionId': hospital_txn_id,
        'encrypted_transaction_blob': encrypted_blob,
        'storacha_cid': cid,
    }
    serializer = HospitalTxnRecordSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Buyer
def upload_claim_doc(request):
    claim_id = request.data.get('claimId')
    encrypted_blob = request.data.get('encryptedBlob', '')
    cid = request.data.get('storachaCid', '')

    try:
        claim = Claim.objects.get(claim_id=claim_id)
        data = {
            'claim': claim.id,
            'encrypted_doc_blob': encrypted_blob,
            'storacha_cid': cid,
        }
        serializer = ClaimDocSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Claim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)


# Admin Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_register(request):
    """Register a new admin user"""
    serializer = AdminSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.save()
        return Response({
            'message': 'Admin registered successfully',
            'admin': {
                'id': admin.id,
                'email': admin.email,
                'full_name': admin.full_name
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Admin login with email and password"""
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.validated_data['admin']
        return Response({
            'message': 'Login successful',
            'admin': {
                'id': admin.id,
                'email': admin.email,
                'full_name': admin.full_name,
                'last_login': admin.last_login
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_verify_wallet(request):
    """Verify admin wallet address matches the configured admin wallet"""
    serializer = AdminWalletVerificationSerializer(data=request.data)
    if serializer.is_valid():
        wallet_address = serializer.validated_data['wallet_address']
        admin_id = serializer.validated_data['admin_id']
        
        # Get the admin wallet address from environment
        admin_wallet = settings.ADMIN_WALLET_ADDRESS.lower() if hasattr(settings, 'ADMIN_WALLET_ADDRESS') else None
        
        if not admin_wallet:
            return Response({
                'error': 'Admin wallet address not configured'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Verify the admin exists and is active
        try:
            admin = Admin.objects.get(id=admin_id, is_active=True)
        except Admin.DoesNotExist:
            return Response({
                'error': 'Admin not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if wallet address matches
        if wallet_address == admin_wallet:
            return Response({
                'message': 'Wallet verified successfully',
                'admin': {
                    'id': admin.id,
                    'email': admin.email,
                    'full_name': admin.full_name,
                    'wallet_verified': True
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Wallet address does not match admin wallet'
            }, status=status.HTTP_403_FORBIDDEN)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Management Views
@api_view(['GET'])
@permission_classes([AllowAny])  # We'll handle admin verification in the view
def admin_get_claims(request):
    """Get all claims for admin review"""
    claims = Claim.objects.all().order_by('-created_at')
    serializer = ClaimSerializer(claims, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_get_buyers(request):
    """Get all buyers for admin review"""
    buyers = Buyer.objects.all().order_by('-id')
    serializer = BuyerSerializer(buyers, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_update_claim_status(request):
    """Update claim status (approve/reject)"""
    claim_id = request.data.get('claim_id')
    new_status = request.data.get('status')  # 'verified' or 'rejected'
    admin_id = request.data.get('admin_id')
    
    if not all([claim_id, new_status, admin_id]):
        return Response({
            'error': 'claim_id, status, and admin_id are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify admin exists
    try:
        admin = Admin.objects.get(id=admin_id, is_active=True)
    except Admin.DoesNotExist:
        return Response({
            'error': 'Admin not found or inactive'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Update claim status
    try:
        claim = Claim.objects.get(claim_id=claim_id)
        claim.claim_status = new_status
        claim.save()
        
        # Call smart contract to verify (if contract is available)
        if contract is not None and new_status in ['verified', 'rejected']:
            try:
                status_bool = new_status == 'verified'
                txn = contract.functions.verifyClaim(
                    claim_id,
                    status_bool
                ).transact({'from': settings.ADMIN_WALLET_ADDRESS})
                w3.eth.wait_for_transaction_receipt(txn)
            except Exception as e:
                print(f"Warning: Could not update claim on blockchain: {e}")
        
        serializer = ClaimSerializer(claim)
        return Response({
            'message': f'Claim {new_status} successfully',
            'claim': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Claim.DoesNotExist:
        return Response({
            'error': 'Claim not found'
        }, status=status.HTTP_404_NOT_FOUND)