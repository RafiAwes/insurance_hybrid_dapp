# Claim Submission Workflow - Updates and Changes

## Overview
This document describes the updated claim submission workflow for the Hybrid Insurance dApp. The changes implement a new process where buyers submit PDF files for claims, which are then automatically verified and processed according to specific business rules.

## Workflow Changes

### 1. PDF File Submission
- Buyers submit claims with PDF files instead of storing documents in Storacha
- PDF files are stored in the database for processing
- Transaction IDs are extracted from the PDF content using text parsing

### 2. Automatic Transaction Verification
- Upon claim submission, the system automatically extracts the transaction ID from the PDF
- The system calls the verification API: `http://127.0.0.1:8000/billing/api/verify-transaction/<transaction_id>/`
- Based on the API response, claims are tagged as:
  - **Verified**: If the API returns success
  - **Unverified**: If the API returns failure

### 3. Admin Claim Management
- All claims appear in the admin dashboard with their verification status
- Admins can approve or reject claims:
  - **Accepted**: Claim is approved
  - **Not Approved**: Claim is rejected

### 4. Buyer Notification System
- Buyers see status messages in their dashboard:
  - "✅ Claim approved" when a claim is accepted
  - "❌ Claim not approved" when a claim is rejected
- Claim history shows appropriate status tags

## Technical Implementation Details

### Backend Changes

#### Models Updated
- `Claim` model updated with new status choices:
  - `verified`
  - `unverified`
  - `accepted`
  - `not_approved`
- Added timestamp fields:
  - `verified_at`: When the claim was verified
  - `accepted_at`: When the claim was accepted by admin

#### New API Endpoints
1. **POST `/submit-claim/`**
   - Handles PDF file upload
   - Extracts transaction ID from PDF
   - Automatically verifies transaction with billing API
   - Creates claim with appropriate status tag

2. **POST `/admin/update-claim-status/`**
   - Allows admins to accept or reject claims
   - Updates claim status and timestamps

#### PDF Processing
- Uses PyPDF2 library to extract text from PDF files
- Regex patterns to identify transaction IDs in various formats
- Automatic verification upon submission

### Frontend Changes

#### Buyer Dashboard
- Updated claim submission form to handle PDF file uploads
- Added claim history section showing status messages
- Real-time feedback on claim submission process

#### Admin Dashboard
- Enhanced claim listing with verification status badges
- Updated action buttons for claim approval/rejection
- Improved status visualization with color-coded tags

## Database Migration Requirements

A new migration will be needed to update the Claim model with:
- New status choices
- Additional timestamp fields

Run the following command to create and apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Dependency Updates

Added PyPDF2 library to requirements:
```
PyPDF2>=3.0.0
```

Install updated dependencies with:
```bash
pip install -r requirements.txt
```

## API Integration

### Verification API
- Endpoint: `http://127.0.0.1:8000/billing/api/verify-transaction/<transaction_id>/`
- Method: GET
- Expected Response Format:
  ```json
  {
    "success": true/false,
    "message": "Verification result"
  }
  ```

## Testing

### Manual Testing Steps
1. Submit a claim with a PDF containing a valid transaction ID
2. Verify the claim appears in admin dashboard with correct status
3. Approve/reject the claim as admin
4. Check buyer dashboard for appropriate status messages

### Edge Cases Handled
- Invalid PDF files are rejected
- Missing transaction IDs in PDFs are handled gracefully
- API failures during verification are handled
- Network timeouts are managed with appropriate error messages

## Future Improvements

1. Enhanced PDF parsing with more robust regex patterns
2. Support for additional document formats
3. Improved error handling for various PDF structures
4. Async processing for better performance with large files