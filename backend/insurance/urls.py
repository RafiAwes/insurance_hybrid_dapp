from django.urls import path
from .views import (
    add_buyer, submit_claim, claim_history, verify_claim,
    upload_transaction_record, upload_claim_doc,
    admin_register, admin_login, admin_verify_wallet,
    admin_get_claims, admin_get_buyers, admin_update_claim_status
)

urlpatterns = [
    # Buyer endpoints
    path('add-buyer/', add_buyer, name='add_buyer'),
    path('submit-claim/', submit_claim, name='submit_claim'),
    path('claim-history/', claim_history, name='claim_history'),
    path('verify-claim/', verify_claim, name='verify_claim'),
    path('upload-transaction/', upload_transaction_record, name='upload_transaction_record'),
    path('upload-claim-doc/', upload_claim_doc, name='upload_claim_doc'),
    
    # Admin endpoints
    path('admin/register/', admin_register, name='admin_register'),
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/verify-wallet/', admin_verify_wallet, name='admin_verify_wallet'),
    path('admin/claims/', admin_get_claims, name='admin_get_claims'),
    path('admin/buyers/', admin_get_buyers, name='admin_get_buyers'),
    path('admin/update-claim-status/', admin_update_claim_status, name='admin_update_claim_status'),
]