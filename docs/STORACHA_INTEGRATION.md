# Storacha Storage Integration for Claim and Premium Records

## Overview
This document describes the implementation of Storacha storage integration for claim and premium records in the Hybrid Insurance dApp. The integration automatically stores claim and premium data in Storacha when records are created or updated.

## Features Implemented

### 1. Database Model Updates
**File**: `backend/insurance/models.py`

#### Added Storacha CID Fields
- Added `storacha_cid` field to `Claim` model (CharField, blank=True)
- Added `storacha_cid` field to `Premium` model (CharField, blank=True)

### 2. Database Migration
**File**: `backend/insurance/migrations/0007_claim_storacha_cid_premium_storacha_cid.py`

#### Migration Changes
- Added `storacha_cid` field to `Claim` table
- Added `storacha_cid` field to `Premium` table

### 3. Storacha Service Implementation
**Files**: 
- `backend/insurance/services/storacha_node_service.py`
- `backend/insurance/services/storacha_client.js`

#### Node.js Service
- Created Node.js service using `@storacha/client`
- Implemented login with admin email from environment variables
- Created or used existing space named "health-insurance-space"
- Added functions for uploading claim and premium data
- Added function for fetching data from CID

#### Python Service Wrapper
- Created Python wrapper for Node.js service
- Implemented `upload_claim_data()` function
- Implemented `upload_premium_data()` function
- Implemented `fetch_from_cid()` function

### 4. Backend API Endpoints
**File**: `backend/insurance/views.py`

#### New Endpoints
1. **POST `/upload-claim/`** - Upload claim data to Storacha
2. **POST `/upload-premium/`** - Upload premium data to Storacha
3. **GET `/fetch-accepted-claims/`** - Fetch all accepted claims with Storacha CIDs
4. **GET `/fetch-premiums/<wallet_address>/`** - Fetch all premiums for a buyer with Storacha CIDs

#### Enhanced Functions
- Updated `admin_update_claim_status()` to upload to Storacha when claim is accepted
- Updated `submit_claim()` to automatically upload claim data to Storacha
- Updated `handle_premium_paid()` in event listener to upload premium data to Storacha

### 5. Frontend Integration
**Files**: 
- `frontend/src/components/BuyerDashboard.tsx`
- `frontend/src/components/AdminDashboard.tsx`

#### Buyer Dashboard
- Added "Premium Payment History" section
- Fetch and display premium payments with Storacha CIDs
- Added "View on Storacha" links for claims and premiums

#### Admin Dashboard
- Added "Accepted Claims" tab
- Fetch and display accepted claims with Storacha CIDs
- Added "View on Storacha" links for claims

## Data Format

### Claim Data Structure
```json
{
  "type": "claim",
  "buyer": {
    "id": "...",
    "full_name": "...",
    "email": "...",
    "wallet_address": "...",
    "national_id": "..."
  },
  "claim": {
    "claim_id": "...",
    "amount": "...",
    "status": "...",
    "description": "...",
    "created_at": "..."
  },
  "uploaded_at": "..."
}
```

### Premium Data Structure
```json
{
  "type": "premium",
  "buyer": {
    "id": "...",
    "full_name": "...",
    "email": "...",
    "wallet_address": "...",
    "national_id": "..."
  },
  "premium": {
    "transaction_hash": "...",
    "amount_eth": "...",
    "block_timestamp": "...",
    "status": "..."
  },
  "uploaded_at": "..."
}
```

## Gateway Access
- Use `https://${cid}.ipfs.storacha.link` to view uploaded data
- Added "View on Storacha" buttons in both admin and buyer UI

## Workflow

### Claim Submission
1. Buyer submits claim with PDF
2. System extracts data and creates claim record
3. Claim data automatically uploaded to Storacha
4. CID stored in `Claim.storacha_cid`

### Claim Acceptance
1. Admin accepts claim
2. Claim status updated to "accepted"
3. Claim data re-uploaded to Storacha (if needed)
4. CID updated in database

### Premium Payment
1. Buyer pays premium on blockchain
2. Event listener detects payment
3. Premium record created in database
4. Premium data automatically uploaded to Storacha
5. CID stored in `Premium.storacha_cid`

## Environment Configuration
**File**: `.env`

### Required Variables
- `STORACHA_ADMIN_EMAIL` - Admin email for Storacha login

## Implementation Details

### Automatic Uploads
- Claims are automatically uploaded when submitted
- Premiums are automatically uploaded when payment is confirmed
- No manual intervention required for basic operation

### Error Handling
- Errors in Storacha upload don't prevent claim/premium creation
- Errors are logged for debugging
- UI gracefully handles missing CID data

### Performance Considerations
- Uploads happen in background
- No blocking operations in critical paths
- Caching opportunities for fetched data

## Testing

### Manual Testing Steps
1. Submit a claim and verify Storacha CID is stored
2. Accept a claim and verify it appears in "Accepted Claims" tab
3. Pay a premium and verify Storacha CID is stored
4. Check "View on Storacha" links work correctly
5. Verify data formats match specifications

### Edge Cases Handled
- Storacha service unavailable
- Network timeouts
- Invalid data formats
- Missing environment variables

## Future Enhancements

### Performance Improvements
- Add Celery or async task for background upload
- Add caching for fetched Storacha data (Redis or Django cache)

### Security Enhancements
- Add authentication for Storacha service
- Encrypt sensitive data before upload

### UI Improvements
- Add loading states for Storacha fetch operations
- Add retry mechanisms for failed fetches
- Improve error messaging for users

## Dependencies

### Backend
- `@storacha/client` (Node.js package)
- `subprocess` for calling Node.js service
- Django models and views

### Frontend
- React components
- Fetch API for backend communication
- Tailwind CSS for styling

## Deployment Instructions

1. Install Node.js dependencies:
   ```bash
   cd backend/insurance/services
   npm install @storacha/client
   ```

2. Set environment variables:
   ```bash
   STORACHA_ADMIN_EMAIL=admin@healthinsurance.com
   ```

3. Apply database migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

4. Restart backend services

## Troubleshooting

### Common Issues
1. **Node.js service not found**: Ensure `@storacha/client` is installed
2. **Storacha login failed**: Check admin email configuration
3. **CID not stored**: Check error logs for upload failures
4. **UI not showing data**: Verify backend endpoints are working

### Debugging Steps
1. Check backend logs for Storacha service errors
2. Verify Node.js service is executable
3. Test Storacha client manually with sample data
4. Check network connectivity to Storacha gateway