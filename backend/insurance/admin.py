from django.contrib import admin
from .models import Buyer, Policy, Claim, HospitalTxnRecord, ClaimDoc

@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('wallet_address', 'full_name', 'email', 'national_id')
    search_fields = ('wallet_address', 'full_name', 'email', 'national_id')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('wallet_address', 'national_id', 'full_name', 'email', 'phone')
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

# Customize admin site
admin.site.site_header = "Health Insurance DApp Administration"
admin.site.site_title = "Health Insurance Admin"
admin.site.index_title = "Welcome to Health Insurance DApp Administration"
