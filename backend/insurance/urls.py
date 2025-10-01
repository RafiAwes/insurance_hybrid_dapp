from django.urls import path
from .views import add_buyer, submit_claim, claim_history, verify_claim, upload_transaction_record, upload_claim_doc

urlpatterns = [
    path('add-buyer/', add_buyer, name='add_buyer'),
    path('submit-claim/', submit_claim, name='submit_claim'),
    path('claim-history/', claim_history, name='claim_history'),
    path('verify-claim/', verify_claim, name='verify_claim'),
    path('upload-transaction/', upload_transaction_record, name='upload_transaction_record'),
    path('upload-claim-doc/', upload_claim_doc, name='upload_claim_doc'),
]