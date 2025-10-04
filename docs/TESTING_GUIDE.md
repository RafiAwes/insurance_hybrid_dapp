# Testing Guide - Claim Submission Workflow

## Overview
This guide provides step-by-step instructions for testing the new claim submission workflow implementation.

## Prerequisites
1. Backend server running
2. Frontend application running
3. Database properly migrated
4. PyPDF2 library installed
5. Access to the billing API at `http://127.0.0.1:8000/billing/api/verify-transaction/`

## Test Cases

### Test Case 1: Successful Claim Submission with Verified Transaction

#### Steps:
1. Log in as a buyer user
2. Navigate to the "Submit Insurance Claim" section
3. Create a PDF file with content that includes a transaction ID, for example:
   ```
   Hospital Invoice
   Patient: John Doe
   Date: 2025-10-04
   Transaction ID: TXN-123456789
   Amount: $1000
   ```
4. Select the PDF file and click "Submit Encrypted Claim"
5. Observe the success message with verification status

#### Expected Results:
- Claim is submitted successfully
- System extracts transaction ID "TXN-123456789"
- System calls verification API
- If API returns success, claim status is "verified"
- Success message displayed to user

### Test Case 2: Claim Submission with Unverified Transaction

#### Steps:
1. Log in as a buyer user
2. Navigate to the "Submit Insurance Claim" section
3. Create a PDF file with content that includes a transaction ID that will fail verification
4. Select the PDF file and click "Submit Encrypted Claim"
5. Observe the result message with verification status

#### Expected Results:
- Claim is submitted successfully
- System extracts transaction ID
- System calls verification API
- If API returns failure, claim status is "unverified"
- Appropriate message displayed to user

### Test Case 3: Admin Claim Approval

#### Steps:
1. Log in as an admin user
2. Navigate to the "Claims Management" tab
3. Find a claim with "verified" or "unverified" status
4. Click the "✅ Approve" button for that claim
5. Confirm the action

#### Expected Results:
- Claim status changes to "accepted"
- Success message displayed
- Timestamp recorded for acceptance

### Test Case 4: Admin Claim Rejection

#### Steps:
1. Log in as an admin user
2. Navigate to the "Claims Management" tab
3. Find a claim with "verified" or "unverified" status
4. Click the "❌ Reject" button for that claim
5. Confirm the action

#### Expected Results:
- Claim status changes to "not_approved"
- Success message displayed
- Timestamp recorded for rejection

### Test Case 5: Buyer Claim History

#### Steps:
1. Log in as a buyer user
2. Navigate to the "Claim History" section
3. View the list of submitted claims

#### Expected Results:
- All claims are displayed with appropriate status badges
- Accepted claims show "✅ Claim approved" message
- Not approved claims show "❌ Claim not approved" message
- Verified claims show "Claim verified successfully" message
- Unverified claims show "Claim could not be verified" message

## Edge Case Testing

### Test Case 6: Invalid File Type

#### Steps:
1. Log in as a buyer user
2. Navigate to the "Submit Insurance Claim" section
3. Try to upload a file that is not a PDF (e.g., .txt, .docx)
4. Click "Submit Encrypted Claim"

#### Expected Results:
- Error message: "Only PDF files are allowed"
- File is not uploaded
- Claim is not submitted

### Test Case 7: PDF Without Transaction ID

#### Steps:
1. Log in as a buyer user
2. Navigate to the "Submit Insurance Claim" section
3. Create a PDF file without any recognizable transaction ID
4. Select the PDF file and click "Submit Encrypted Claim"

#### Expected Results:
- Error message: "Could not extract transaction ID from PDF file"
- Claim is not submitted

### Test Case 8: Verification API Unavailable

#### Steps:
1. Ensure the billing API is not running or accessible
2. Log in as a buyer user
3. Navigate to the "Submit Insurance Claim" section
4. Submit a valid PDF file with transaction ID

#### Expected Results:
- Claim is submitted with status "unverified"
- Appropriate error message about API failure
- Claim appears in admin dashboard

## Verification Points

### Backend Verification
1. Check database for new claim records
2. Verify claim status values are correct
3. Confirm timestamp fields are populated
4. Check that PDF files are properly processed

### Frontend Verification
1. Verify UI displays correct status badges
2. Confirm error messages are user-friendly
3. Check that claim history updates in real-time
4. Ensure admin actions update the UI immediately

### API Verification
1. Monitor API calls to verification endpoint
2. Verify correct request/response format
3. Check error handling for various scenarios

## Troubleshooting

### Common Issues

1. **PyPDF2 Module Not Found**
   - Solution: Run `pip install PyPDF2` in the backend environment

2. **Database Migration Issues**
   - Solution: Ensure all migrations are applied with `python manage.py migrate`

3. **Verification API Not Responding**
   - Solution: Check that the billing API is running at the correct endpoint

4. **PDF Parsing Failures**
   - Solution: Ensure PDF files contain readable text (not scanned images)

### Debugging Tips

1. Check browser console for frontend errors
2. Check backend logs for server errors
3. Use Django admin to inspect database records
4. Test verification API directly with curl or Postman

## Success Criteria

The implementation is successful if:
1. All test cases pass as described
2. No errors appear in browser console or backend logs
3. Database records are correctly updated
4. Users can successfully submit claims and receive appropriate feedback
5. Admins can manage claims with proper status tracking