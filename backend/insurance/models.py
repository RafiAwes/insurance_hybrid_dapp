import uuid
from django.db import models

class Buyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_address = models.CharField(max_length=128, unique=True)
    national_id = models.CharField(max_length=128, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.full_name


class Policy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=100, unique=True)
    monthly_premium = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.policy_number


class Claim(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim_id = models.CharField(max_length=200, unique=True)  # matches on-chain claimId
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.SET_NULL, null=True, blank=True)
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    claim_status = models.CharField(max_length=50, default='submitted', choices=STATUS_CHOICES)
    claim_description = models.TextField(blank=True)
    hospital_transaction_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.claim_id


class HospitalTxnRecord(models.Model):
    hospitalTransactionId = models.CharField(max_length=200, primary_key=True)
    encrypted_transaction_blob = models.TextField(blank=True)
    storacha_cid = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hospitalTransactionId


class ClaimDoc(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    storacha_cid = models.CharField(max_length=100, blank=True)
    encrypted_doc_blob = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc for {self.claim.claim_id}"
