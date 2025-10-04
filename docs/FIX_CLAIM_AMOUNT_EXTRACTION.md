# Fix for Claim Amount Extraction from PDF

## Problem
The claim amount was hardcoded to 1000.00 in the frontend and not being extracted from the PDF file. When the PDF contained an amount of 10,000, it was still showing as 1,000.00 in the system.

## Solution Implemented

### 1. Backend Changes
**File**: `backend/insurance/views.py`

#### Added New Function
Created `extract_claim_data_from_pdf()` function to extract both transaction ID and amount from PDF files:

```python
def extract_claim_data_from_pdf(file):
    """
    Extract claim data (transaction ID and amount) from PDF file content
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Extract transaction ID
        transaction_id_patterns = [
            r'Transaction\s*ID[:\s]*([A-Za-z0-9\-_]+)',
            r'TXN[:\s]*([A-Za-z0-9\-_]+)',
            r'Transaction[:\s]*([A-Za-z0-9\-_]+)',
            r'ID[:\s]*([A-Za-z0-9\-_]+)'
        ]
        
        transaction_id = None
        for pattern in transaction_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                transaction_id = match.group(1)
                break
        
        # Extract amount
        amount_patterns = [
            r'Amount[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'Total[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'Claim\s*Amount[:\s]*\$?([0-9,]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)'
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')  # Remove commas
                try:
                    amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        return {
            'transaction_id': transaction_id,
            'amount': amount
        }
    except Exception as e:
        print(f"Error extracting claim data from PDF: {str(e)}")
        return {
            'transaction_id': None,
            'amount': None
        }
```

#### Updated submit_claim Function
Modified the `submit_claim` function to:
1. Use the new extraction function
2. Use amount from PDF if available, fallback to form data if not
3. Return the extracted amount in the response

```python
@api_view(['POST'])
def submit_claim(request):
    """
    Submit a claim with PDF file upload
    Expected payload: {
        "buyer_address": "0x...",
        "claim_description": "Medical treatment",
        "file": PDF file
    }
    """
    try:
        buyer_address = request.data.get('buyer_address')
        claim_description = request.data.get('claim_description')
        file = request.FILES.get('file')
        
        if not all([buyer_address, claim_description, file]):
            return Response({
                'error': 'Missing required fields: buyer_address, claim_description, file'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        if not file.name.endswith('.pdf'):
            return Response({
                'error': 'Only PDF files are allowed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get buyer
        buyer = get_object_or_404(Buyer, wallet_address=buyer_address)
        
        # Extract claim data from PDF
        claim_data = extract_claim_data_from_pdf(file)
        transaction_id = claim_data.get('transaction_id')
        pdf_amount = claim_data.get('amount')
        
        if not transaction_id:
            return Response({
                'error': 'Could not extract transaction ID from PDF file'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use amount from PDF if available, otherwise use form data
        claim_amount = pdf_amount if pdf_amount is not None else request.data.get('claim_amount', '0')
        
        # Create claim
        claim_id = f"CLM-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        claim = Claim.objects.create(
            claim_id=claim_id,
            buyer=buyer,
            claim_amount=claim_amount,
            claim_description=claim_description,
            hospital_transaction_id=transaction_id,
            claim_status='submitted'
        )
        
        # Verify transaction ID
        verification_result = verify_transaction_id(transaction_id)
        claim_status = 'verified' if verification_result.get('success', False) else 'unverified'
        claim.claim_status = claim_status
        if claim_status == 'verified':
            claim.verified_at = timezone.now()
        claim.save()
        
        return Response({
            'success': True,
            'message': 'Claim submitted successfully',
            'claim_id': claim_id,
            'transaction_id': transaction_id,
            'claim_amount': str(claim_amount),
            'verification_status': claim_status
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to submit claim: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### 2. Frontend Changes
**File**: `frontend/src/components/BuyerDashboard.tsx`

#### Updated handleSubmitClaim Function
Removed hardcoded claim amount and updated success message to show extracted amount:

```typescript
const handleSubmitClaim = async () => {
  if (!file) {
    setClaimStatus('Please select a file');
    return;
  }
  
  if (!isRegistered) {
    setClaimStatus('❌ You must be registered to submit claims. Please contact admin.');
    return;
  }
  
  try {
    setClaimStatus('🔄 Submitting claim...');
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('buyer_address', currentAccount);
    formData.append('claim_description', 'Medical claim submission');
    
    // Submit claim with PDF file
    const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/submit-claim/`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to submit claim');
    }
    
    const result = await response.json();
    console.log('✅ Claim submitted:', result);
    
    setClaimStatus(`✅ Claim submitted successfully!
📋 Claim ID: ${result.claim_id}
💳 Transaction ID: ${result.transaction_id}
💰 Claim Amount: $${result.claim_amount}
🔍 Verification Status: ${result.verification_status}

Admin will review your claim and update the status.`);
    
    // Clear the file input
    setFile(null);
    
  } catch (error) {
    console.error('Claim submission error:', error);
    setClaimStatus('❌ Claim submission failed: ' + (error as Error).message);
  }
};
```

## How It Works Now
1. When a buyer submits a claim with a PDF file:
   - System extracts both transaction ID and amount from the PDF
   - Uses the extracted amount (e.g., 10,000) instead of hardcoded value
   - If amount extraction fails, falls back to form data (0 by default)

2. PDF Extraction Patterns Supported:
   - Transaction ID: "Transaction ID: WM9pe6ds", "TXN: WM9pe6ds", etc.
   - Amount: "Amount: $10,000.00", "Total: $10,000.00", "$10,000.00", etc.

3. The extracted amount is:
   - Saved in the database with the claim record
   - Returned in the API response
   - Displayed in the success message to the user

## Testing
Created test script `test_pdf_extraction.py` to verify the extraction works correctly:
- Input: PDF with "Transaction ID: WM9pe6ds" and "Amount: $10,000.00"
- Output: `{'transaction_id': 'WM9pe6ds', 'amount': 10000.0}`

## Impact
- Claims now show the correct amount extracted from PDF files
- System is more accurate and reduces manual data entry errors
- Better user experience with automatic data extraction
- Maintains backward compatibility with form-based submission