from rest_framework import serializers
from .models import Buyer, Policy, Claim, HospitalTxnRecord, ClaimDoc

class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = ['id', 'wallet_address', 'national_id', 'full_name', 'email', 'phone']

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