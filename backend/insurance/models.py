import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Buyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_address = models.CharField(max_length=128, unique=True)
    national_id = models.CharField(max_length=128, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)  # Required for login
    password = models.CharField(max_length=128, default='temp_password')  # Will store hashed password
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Premium payment tracking
    total_premiums_paid = models.DecimalField(max_digits=30, decimal_places=18, default=0)
    last_premium_payment = models.DateTimeField(null=True, blank=True)
    premium_payment_count = models.IntegerField(default=0)
    
    # Claim document storage (JSON field to store CIDs and metadata)
    claim_documents = models.JSONField(default=list, blank=True)  # List of {cid, claimId, timestamp, status}
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        """Hash and set the password"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

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
        ('unverified', 'Unverified'),
        ('accepted', 'Accepted'),
        ('not_approved', 'Not Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim_id = models.CharField(max_length=200, unique=True)  # matches on-chain claimId
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.SET_NULL, null=True, blank=True)
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    claim_status = models.CharField(max_length=50, default='submitted', choices=STATUS_CHOICES)
    claim_description = models.TextField(blank=True)
    hospital_transaction_id = models.CharField(max_length=200, null=True, blank=True)
    storacha_cid = models.CharField(max_length=100, blank=True)  # Storacha CID for claim data
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

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


class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Will store hashed password
    full_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"


class Premium(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='premiums')
    policy = models.ForeignKey(Policy, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Blockchain data
    transaction_hash = models.CharField(max_length=66, unique=True)  # Ethereum tx hash
    amount_eth = models.DecimalField(max_digits=30, decimal_places=18)  # Amount in ETH
    amount_wei = models.CharField(max_length=100)  # Amount in wei (for precision)
    block_number = models.BigIntegerField()
    block_timestamp = models.DateTimeField()
    
    # Transaction details
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.CharField(max_length=100, null=True, blank=True)  # In wei
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    storacha_cid = models.CharField(max_length=100, blank=True)  # Storacha CID for premium data
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Premium {self.amount_eth} ETH by {self.buyer.full_name}"
