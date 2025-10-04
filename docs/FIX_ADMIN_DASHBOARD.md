# Fix for Admin Dashboard Claim Data Display

## Problem
The admin dashboard was showing mock data instead of fetching real claim data from the NeonDB database.

## Solution
Implemented proper data fetching from the backend API endpoints.

## Changes Made

### 1. Backend Changes

#### Updated API Endpoints
- **File**: `backend/insurance/views.py`
- **Changes**:
  - Implemented `admin_get_claims` function to fetch all claims from database
  - Implemented `admin_get_buyers` function to fetch all buyers from database
  - Added proper serialization of claim and buyer data with all required fields

#### Updated CORS Settings
- **File**: `backend/backend/settings.py`
- **Changes**:
  - Added `http://localhost:3001` to `CORS_ALLOWED_ORIGINS` to allow frontend requests

### 2. Frontend Changes

#### Updated Admin Dashboard
- **File**: `frontend/src/components/AdminDashboard.tsx`
- **Changes**:
  - Removed mock data and implemented real API calls to fetch claims and buyers
  - Updated interface definitions to match backend data structure
  - Modified claims table to display buyer name in addition to wallet address
  - Updated analytics section to use correct status values
  - Added proper error handling with fallback to mock data if API fails

### 3. Database Configuration
- **File**: `backend/.env`
- **Changes**:
  - Created .env file with proper NeonDB connection string
  - Updated `backend/backend/settings.py` to use `dj_database_url` for parsing DATABASE_URL

### 4. Dependencies
- **File**: `backend/requirements.txt`
- **Changes**:
  - Added `dj-database-url>=2.1.0` for database URL parsing

## Testing
1. Verified that the backend API endpoints return correct data:
   - `/api/admin/claims/` returns claim data with buyer information
   - `/api/admin/buyers/` returns buyer data with all relevant fields

2. Verified that the frontend correctly fetches and displays data:
   - Claims are displayed with buyer names and wallet addresses
   - Status badges show correct claim statuses
   - Analytics section shows accurate counts

## How It Works Now
1. Admin dashboard loads and makes API calls to:
   - `http://localhost:8000/api/admin/claims/` for claim data
   - `http://localhost:8000/api/admin/buyers/` for buyer data

2. Backend fetches data from NeonDB and returns properly formatted JSON

3. Frontend displays real data instead of mock data

4. All claim management functionality (approve/reject) continues to work with real data

## Verification
To verify the fix is working:
1. Ensure both backend (port 8000) and frontend (port 3001) servers are running
2. Log in as admin
3. Navigate to Claims Management tab
4. You should see real claims from the database instead of mock data