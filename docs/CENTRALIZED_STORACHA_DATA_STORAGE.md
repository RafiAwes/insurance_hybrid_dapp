# Centralized Storacha Data Storage System

## 🔄 Updated System Architecture

Based on your requirements, the system now uses a **centralized Storacha account** (`rafiaweshan4897@gmail.com`) for all document storage, with premium payments and claim CIDs tracked in the buyer's database record.

## 📊 Data Storage Locations

### 1. **Premium Payments**

**Blockchain Storage (Primary)**:
- Smart contract emits [`PremiumPaid`](contracts/HealthInsurance.sol:19) events
- Immutable record on Ethereum blockchain

**Database Storage (Secondary)**:
- [`Premium`](backend/insurance/models.py:110) model for detailed records
- [`Buyer`](backend/insurance/models.py:5) model tracks payment summary:
  ```python
  total_premiums_paid = DecimalField()      # Total ETH paid
  last_premium_payment = DateTimeField()    # Last payment date
  premium_payment_count = IntegerField()    # Number of payments
  ```

### 2. **Claim Documents**

**Storacha Storage (Primary)**:
- **Account**: `rafiaweshan4897@gmail.com` (centralized admin account)
- **Encryption**: All documents encrypted before upload
- **Organization**: Separate spaces per buyer for organization

**Database Storage (Secondary)**:
- [`Buyer.claim_documents`](backend/insurance/models.py:18) JSON field stores:
  ```json
  [
    {
      "claim_id": "claim-1704067200000",
      "cid": "bafybeiexample123...",
      "filename": "medical_report.pdf",
      "file_size": 1024000,
      "timestamp": "2025-01-01T10:00:00Z",
      "status": "submitted"
    }
  ]
  ```

## 🔄 Updated User Flow

### **Premium Payment Flow**:
1. User pays premium → Smart contract emits event
2. Event listener creates [`Premium`](backend/insurance/models.py:110) record
3. Buyer's payment summary updated automatically
4. History viewable in admin dashboard and buyer profile

### **Claim Submission Flow**:
1. User selects document (no email input required)
2. Document encrypted and uploaded to centralized Storacha account
3. CID stored in buyer's [`claim_documents`](backend/insurance/models.py:18) field via API
4. Admin can view all claims and documents in dashboard

## 🛠️ Technical Implementation

### **Frontend Changes**:
- **Removed**: Email input requirement for claims
- **Added**: Automatic CID storage via API call
- **Updated**: [`uploadEncryptedToStoracha()`](frontend/src/utils/encryption.ts:67) uses centralized account
- **Enhanced**: Better user feedback and status messages

### **Backend Changes**:
- **Added**: [`store_claim_document`](backend/insurance/views.py:11) API endpoint
- **Added**: [`get_buyer_history`](backend/insurance/views.py:44) API endpoint
- **Added**: [`get_buyer_claims`](backend/insurance/views.py:85) API endpoint
- **Updated**: [`Buyer`](backend/insurance/models.py:5) model with tracking fields
- **Enhanced**: Event listener updates buyer payment summary

### **Database Schema**:
```sql
-- Buyer table additions
ALTER TABLE insurance_buyer ADD COLUMN total_premiums_paid DECIMAL(30,18) DEFAULT 0;
ALTER TABLE insurance_buyer ADD COLUMN last_premium_payment TIMESTAMP NULL;
ALTER TABLE insurance_buyer ADD COLUMN premium_payment_count INTEGER DEFAULT 0;
ALTER TABLE insurance_buyer ADD COLUMN claim_documents JSONB DEFAULT '[]';
```

## 📋 API Endpoints

### **Store Claim Document**:
```http
POST /api/store-claim-document/
Content-Type: application/json

{
  "buyer_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
  "claim_id": "claim-1704067200000",
  "cid": "bafybeiexample123...",
  "filename": "medical_report.pdf",
  "file_size": 1024000
}
```

### **Get Buyer History**:
```http
GET /api/buyer-history/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/

Response:
{
  "buyer_info": {
    "wallet_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "total_premiums_paid": "0.300000000000000000",
    "premium_payment_count": 3,
    "last_premium_payment": "2025-01-01T10:00:00Z"
  },
  "premium_payments": [...],
  "claims": [...],
  "claim_documents": [...]
}
```

## 🔐 Security & Privacy

### **Document Security**:
- All documents encrypted before upload using AES-GCM
- Encryption keys managed securely (not stored with documents)
- Only authorized admin account has Storacha access

### **Data Privacy**:
- Personal information only in database (not on blockchain)
- Wallet addresses are pseudonymous on blockchain
- Document contents encrypted and not readable without keys

## 👥 User Experience

### **For Buyers**:
- ✅ No email input required for claims
- ✅ Automatic secure document storage
- ✅ Clear status messages and feedback
- ✅ Payment history tracked automatically

### **For Admins**:
- ✅ Centralized document management
- ✅ Complete buyer payment history
- ✅ Easy claim document access
- ✅ Comprehensive admin dashboard

## 🔄 Migration Steps

To implement this system:

1. **Database Migration**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Environment Setup**:
   ```bash
   # Add to .env
   STORACHA_ADMIN_EMAIL=rafiaweshan4897@gmail.com
   ```

3. **Start Event Listener**:
   ```bash
   python manage.py shell
   >>> from insurance.event_listener import listen_to_events
   >>> listen_to_events()
   ```

4. **Frontend Build**:
   ```bash
   cd frontend
   npm run build
   ```

## 📈 Benefits

### **Operational**:
- Simplified user experience (no email required)
- Centralized document management
- Automated payment tracking
- Comprehensive audit trail

### **Technical**:
- Reduced complexity for users
- Better data organization
- Improved scalability
- Enhanced security through centralization

### **Business**:
- Lower user friction
- Better data insights
- Easier compliance management
- Streamlined admin operations

## 🔍 Monitoring

### **Payment Tracking**:
- Real-time blockchain event monitoring
- Automatic database synchronization
- Payment history analytics
- Failed transaction alerts

### **Document Management**:
- Upload success/failure tracking
- Storage usage monitoring
- Document access logs
- Encryption key management

The system now provides a seamless experience where users don't need to manage Storacha accounts, while maintaining security and providing comprehensive tracking of all premium payments and claim documents in the buyer's database record.