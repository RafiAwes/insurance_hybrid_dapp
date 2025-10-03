from django.contrib import admin
from .models import Buyer, Policy, Claim, HospitalTxnRecord, ClaimDoc, Premium, Admin

@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('wallet_address', 'full_name', 'email', 'premium_payment_count', 'total_premiums_paid', 'last_premium_payment')
    search_fields = ('wallet_address', 'full_name', 'email', 'national_id')
    list_filter = ('is_active', 'last_premium_payment', 'created_at')
    readonly_fields = ('total_premiums_paid', 'last_premium_payment', 'premium_payment_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('wallet_address', 'national_id', 'full_name', 'email', 'phone', 'is_active')
        }),
        ('Premium Payment History', {
            'fields': ('total_premiums_paid', 'premium_payment_count', 'last_premium_payment'),
            'classes': ('collapse',)
        }),
        ('Claim Documents', {
            'fields': ('claim_documents',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'policy_number', 'monthly_premium', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__wallet_address', 'buyer__full_name', 'policy_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Policy Details', {
            'fields': ('buyer', 'policy_number', 'monthly_premium', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_id', 'buyer', 'claim_amount', 'claim_status', 'created_at')
    list_filter = ('claim_status', 'created_at')
    search_fields = ('claim_id', 'buyer__wallet_address', 'buyer__name', 'hospital_transaction_id')
    readonly_fields = ('claim_id', 'created_at')
    
    fieldsets = (
        ('Claim Information', {
            'fields': ('claim_id', 'buyer', 'claim_amount', 'claim_description', 'hospital_transaction_id')
        }),
        ('Status', {
            'fields': ('claim_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_claims', 'reject_claims']
    
    def approve_claims(self, request, queryset):
        updated = queryset.update(claim_status='verified')
        self.message_user(request, f'{updated} claims were approved.')
    approve_claims.short_description = "Approve selected claims"
    
    def reject_claims(self, request, queryset):
        updated = queryset.update(claim_status='rejected')
        self.message_user(request, f'{updated} claims were rejected.')
    reject_claims.short_description = "Reject selected claims"

@admin.register(HospitalTxnRecord)
class HospitalTxnRecordAdmin(admin.ModelAdmin):
    list_display = ('hospitalTransactionId', 'storacha_cid', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('hospitalTransactionId', 'storacha_cid')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('hospitalTransactionId', 'encrypted_transaction_blob', 'storacha_cid')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ClaimDoc)
class ClaimDocAdmin(admin.ModelAdmin):
    list_display = ('claim', 'storacha_cid', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('claim__claim_id', 'storacha_cid')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        ('Document Details', {
            'fields': ('claim', 'encrypted_doc_blob', 'storacha_cid')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Premium)
class PremiumAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'amount_eth', 'status', 'block_timestamp', 'transaction_hash_short')
    list_filter = ('status', 'block_timestamp', 'created_at')
    search_fields = ('buyer__full_name', 'buyer__wallet_address', 'transaction_hash')
    readonly_fields = ('transaction_hash', 'amount_wei', 'block_number', 'block_timestamp', 'gas_used', 'gas_price', 'created_at')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('buyer', 'policy', 'amount_eth', 'status')
        }),
        ('Blockchain Details', {
            'fields': ('transaction_hash', 'amount_wei', 'block_number', 'block_timestamp', 'gas_used', 'gas_price'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def buyer_name(self, obj):
        """Display buyer's full name"""
        return obj.buyer.full_name
    buyer_name.short_description = 'Buyer'
    buyer_name.admin_order_field = 'buyer__full_name'
    
    def transaction_hash_short(self, obj):
        """Display shortened transaction hash"""
        return f"{obj.transaction_hash[:10]}...{obj.transaction_hash[-8:]}"
    transaction_hash_short.short_description = 'Transaction Hash'

@admin.register(Admin)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_active', 'created_at', 'last_login')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'full_name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Admin Information', {
            'fields': ('email', 'full_name', 'password', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site
admin.site.site_header = "Health Insurance DApp Administration"
admin.site.site_title = "Health Insurance Admin"
admin.site.index_title = "Welcome to Health Insurance DApp Administration"
