from rest_framework import serializers
from .models import Buyer, Policy, Claim, HospitalTxnRecord, ClaimDoc, Admin
from django.utils import timezone

class BuyerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Buyer
        fields = ['id', 'wallet_address', 'national_id', 'full_name', 'email', 'password', 'phone', 'is_active', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'last_login': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        buyer = Buyer(**validated_data)
        if password:
            buyer.set_password(password)
        buyer.save()
        return buyer

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'buyer', 'policy_number', 'monthly_premium', 'status', 'created_at']


class ClaimSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer(read_only=True)
    policy = PolicySerializer(read_only=True)

    class Meta:
        model = Claim
        fields = ['id', 'claim_id', 'buyer', 'policy', 'claim_amount', 'claim_status', 'claim_description', 'hospital_transaction_id', 'created_at']


class HospitalTxnRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalTxnRecord
        fields = ['hospitalTransactionId', 'encrypted_transaction_blob', 'storacha_cid', 'created_at']


class ClaimDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDoc
        fields = ['id', 'claim', 'storacha_cid', 'encrypted_doc_blob', 'uploaded_at']


class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Admin
        fields = ['id', 'email', 'password', 'full_name', 'is_active', 'created_at', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'last_login': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        admin = Admin(**validated_data)
        admin.set_password(password)
        admin.save()
        return admin


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                admin = Admin.objects.get(email=email, is_active=True)
                if not admin.check_password(password):
                    raise serializers.ValidationError('Invalid email or password.')
                
                # Update last login
                admin.last_login = timezone.now()
                admin.save()
                
                data['admin'] = admin
                return data
            except Admin.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Email and password are required.')


class AdminWalletVerificationSerializer(serializers.Serializer):
    wallet_address = serializers.CharField(max_length=42)
    admin_id = serializers.UUIDField()

    def validate_wallet_address(self, value):
        # Basic Ethereum address validation
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum address format.')
        return value.lower()


class BuyerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                buyer = Buyer.objects.get(email=email, is_active=True)
                if not buyer.check_password(password):
                    raise serializers.ValidationError('Invalid email or password.')
                
                # Update last login
                buyer.last_login = timezone.now()
                buyer.save()
                
                data['buyer'] = buyer
                return data
            except Buyer.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Email and password are required.')


class BuyerWalletVerificationSerializer(serializers.Serializer):
    wallet_address = serializers.CharField(max_length=42)
    buyer_id = serializers.UUIDField()

    def validate_wallet_address(self, value):
        # Basic Ethereum address validation
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum address format.')
        return value.lower()

    def validate(self, data):
        wallet_address = data.get('wallet_address')
        buyer_id = data.get('buyer_id')
        
        # Verify the buyer exists and the wallet address matches
        try:
            buyer = Buyer.objects.get(id=buyer_id, is_active=True)
            if buyer.wallet_address.lower() != wallet_address:
                raise serializers.ValidationError('Wallet address does not match registered address.')
            data['buyer'] = buyer
            return data
        except Buyer.DoesNotExist:
            raise serializers.ValidationError('Buyer not found or inactive.')