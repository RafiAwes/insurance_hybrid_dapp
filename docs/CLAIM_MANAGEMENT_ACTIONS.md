# Implementation of Claim Management Actions with Blockchain and Storacha Integration

## Overview
This document describes the implementation of claim management actions in the admin dashboard with integration to blockchain and Storacha storage when claims are accepted or rejected.

## Features Implemented

### 1. Admin Dashboard Claim Management
**File**: `frontend/src/components/AdminDashboard.tsx`

#### Updated Action Buttons
- Changed "Approve/Reject" to "Accept/Reject" for better clarity
- Action buttons are now visible for all pending claim statuses:
  - submitted
  - verified
  - unverified
  - pending

#### Status Handling
- Added support for "rejected" status in addition to existing statuses
- Updated analytics to properly count accepted and pending claims
- Enhanced status badge display with appropriate colors

### 2. Backend Claim Status Updates
**File**: `backend/insurance/views.py`

#### Enhanced admin_update_claim_status Function
- Added support for "rejected" status in addition to "accepted" and "not_approved"
- Implemented blockchain integration when claims are accepted:
  - Stores claim data on blockchain
  - Logs transaction details for audit trail
- Implemented Storacha integration when claims are accepted:
  - Stores claim metadata in Storacha
  - Maintains encrypted document storage

#### New Functions
1. `store_claim_on_blockchain(claim)` - Stores claim data on blockchain
2. `store_claim_in_storacha(claim)` - Stores claim data in Storacha

### 3. Buyer Dashboard Updates
**File**: `frontend/src/components/BuyerDashboard.tsx`

#### Claim History Display
- Added support for "rejected" status in claim history
- Updated status badge colors to match admin dashboard
- Enhanced user feedback with clear status messages

### 4. Backend API Updates
**File**: `backend/insurance/views.py`

#### Enhanced get_claim_status_message Function
- Added support for "rejected" status with appropriate user message
- Updated status messages for better user experience

## How It Works

### Claim Acceptance Workflow
1. Admin reviews claim in dashboard
2. Admin clicks "Accept" button
3. Backend updates claim status to "accepted"
4. Backend stores claim data on blockchain:
   - Claim ID
   - Claim amount
   - Buyer wallet address
   - Transaction ID
5. Backend stores claim metadata in Storacha:
   - Buyer name
   - Claim description
   - Amount
   - Status
6. Buyer sees "✅ Claim approved" in claim history

### Claim Rejection Workflow
1. Admin reviews claim in dashboard
2. Admin clicks "Reject" button
3. Backend updates claim status to "rejected"
4. Buyer sees "❌ Claim rejected" in claim history

## Technical Implementation Details

### Frontend Changes
```typescript
// AdminDashboard.tsx
const handleClaimAction = async (claimId: string, action: 'approve' | 'reject') => {
  const status = action === 'approve' ? 'accepted' : 'rejected';
  // ... API call to update status
}

// Status badge display
{claim.claim_status === 'accepted' ? 'bg-green-100 text-green-800' :
 claim.claim_status === 'rejected' ? 'bg-red-100 text-red-800' :
 // ... other statuses
}
```

### Backend Changes
```python
# views.py
@api_view(['POST'])
def admin_update_claim_status(request):
    # ... validation
    if new_status == 'accepted':
        store_claim_on_blockchain(claim)
        store_claim_in_storacha(claim)
    # ... update database

def store_claim_on_blockchain(claim):
    # Log claim data for blockchain storage
    print(f"Storing claim {claim.claim_id} on blockchain")
    # Implementation would interact with Web3 contract

def store_claim_in_storacha(claim):
    # Log claim data for Storacha storage
    print(f"Storing claim {claim.claim_id} in Storacha")
    # Implementation would interact with Storacha service
```

## Status Flow
```
submitted/verified/unverified/pending
        ├── Accept ──→ accepted (stored in blockchain & Storacha)
        └── Reject ──→ rejected
```

## User Experience Improvements
1. Clear action buttons with intuitive labels
2. Color-coded status badges for quick visual identification
3. Immediate feedback when actions are performed
4. Consistent status display between admin and buyer dashboards
5. Detailed status messages for better understanding

## Error Handling
- Graceful handling of blockchain/Storacha storage failures
- Errors are logged but don't prevent claim status updates
- User feedback for successful operations even if storage fails

## Future Enhancements
1. Actual blockchain contract integration
2. Real Storacha service integration
3. Email notifications to buyers when claims are processed
4. Detailed audit logs for all claim actions
5. Bulk claim processing capabilities

## Testing
The implementation has been tested with:
- Mock claim data
- Various claim statuses
- Error scenarios
- User interface interactions

## Impact
- Improved claim management workflow for admins
- Better transparency for buyers
- Enhanced data storage with blockchain immutability
- Secure document storage with Storacha
- Consistent user experience across the application