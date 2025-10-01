# Health Insurance DApp - Project Instructions

## Project Architecture Overview

This project is a decentralized application (DApp) for managing health insurance claims on the blockchain. It combines traditional web development with blockchain and decentralized storage to ensure secure, transparent, and tamper-proof handling of insurance data. The architecture is modular, with clear separation of concerns across frontend, backend, smart contracts, database, and storage layers.

### Key Components and Layers

1. **Smart Contracts (Blockchain Layer)**:
   - **Technology**: Solidity (v0.8.20) with Hardhat framework.
   - **Location**: `contracts/HealthInsurance.sol`, `scripts/deploy.js`, `test/HealthInsurance.test.js`, `hardhat.config.js`.
   - **Purpose**: Core business logic for insurance operations, such as premium payments, claim submissions, and verifications. The `HealthInsurance` contract handles:
     - Buyer registration and premium payments (using ETH or tokens).
     - Claim submission with encrypted document hashes.
     - Admin verification of claims.
     - Event emissions for blockchain-to-backend synchronization (e.g., `ClaimSubmitted`, `PremiumPaid`).
   - **Deployment**: Local Hardhat node (http://127.0.0.1:8545) for development; configurable for testnets/mainnets.
   - **Interactions**: Accessed via Web3 libraries from frontend (Web3.js) and backend (Web3.py). MetaMask wallet signs transactions.

2. **Frontend (User Interface Layer)**:
   - **Technology**: React (18.x) with Vite build tool, TailwindCSS for styling, TypeScript for type safety, Web3.js for blockchain integration.
   - **Location**: `frontend/` directory, including `src/App.tsx`, `src/components/` (e.g., `BuyerDashboard.tsx`, `WalletConnect.tsx`), `src/services/` (e.g., `web3.ts`, `contract.ts`), `src/utils/` (e.g., `encryption.ts` for client-side encryption).
   - **Purpose**: Provides user interfaces for:
     - Buyers: Connect wallet (MetaMask), pay premiums, submit claims with file uploads (encrypted client-side), view history.
     - Hospitals: Upload encrypted transaction records.
     - Admins: Verify claims via dashboard.
   - **Interactions**:
     - Wallet connection via MetaMask for signing transactions.
     - Direct calls to smart contracts for blockchain operations.
     - API calls to backend for user data, claim status, and document storage.
     - Client-side encryption of sensitive documents (AES-GCM) before upload to decentralized storage.
   - **Development Server**: Runs on http://localhost:3000.

3. **Backend (API and Synchronization Layer)**:
   - **Technology**: Django (with Django REST Framework for APIs), Python 3.10+, Web3.py for blockchain integration, PostgreSQL for database.
   - **Location**: `backend/` directory, including `backend/settings.py`, `myapp/models.py` (e.g., Buyer, Claim models), `myapp/views.py` (API endpoints), `myapp/serializers.py`, `myapp/services/storacha_service.py` (storage stubs), `myapp/event_listener.py` (blockchain event syncing).
   - **Purpose**: Handles off-chain data management, authentication, and synchronization:
     - User management (buyers, admins, hospitals) stored in DB.
     - API endpoints for claim submission, verification, and history retrieval.
     - Event listener (`event_listener.py`) monitors smart contract events and updates DB (e.g., sync premium payments, claim statuses).
     - Stubbed integration with Storacha for decentralized storage of encrypted documents.
   - **Interactions**:
     - Listens to blockchain events via Web3.py connected to Hardhat RPC.
     - Exposes REST APIs (e.g., `/api/claims/`, `/api/buyers/`) secured with session/token auth.
     - Stores metadata (e.g., claim IDs, CIDs from Storacha) in PostgreSQL.
   - **Development Server**: Runs on http://localhost:8000. Admin panel at http://localhost:8000/admin/.

4. **Database (Persistence Layer)**:
   - **Technology**: PostgreSQL (local via Docker or Neon cloud).
   - **Configuration**: Defined in `backend/settings.py` with env vars (e.g., `DATABASE_URL` or individual DB creds).
   - **Purpose**: Stores relational data like user profiles, claim details, transaction records. Does not store sensitive documents (encrypted and offloaded to Storacha).
   - **Migrations**: Managed via Django (`python manage.py migrate`).
   - **Docker Support**: `docker-compose.yml` spins up a Postgres container with DB `health_insurance_db`.

5. **Decentralized Storage (Document Layer)**:
   - **Technology**: Storacha (IPFS-based, stubbed implementation).
   - **Location**: Stubs in `backend/myapp/services/storacha_service.py` and `frontend/src/utils/encryption.ts`.
   - **Purpose**: Stores encrypted claim documents and hospital records as Content-Identifiable (CID) blobs. Ensures data integrity and decentralization.
   - **Workflow**:
     - Client encrypts files (AES-GCM with IV).
     - Uploads to Storacha via SDK (stubbed: generates fake CID).
     - CID and metadata stored in backend DB; hash pinned to blockchain.
   - **Integration**: Uses @storacha/client in frontend for client-side uploads. Backend stores CIDs and metadata.
   - **Workflow**:
     - Client encrypts files (AES-GCM with IV) in frontend.
     - Logs in to Storacha with email (requires manual confirmation link for first time).
     - Creates/provisions a space (requires selecting a payment plan via email/dashboard).
     - Uploads encrypted Blob to Storacha, receiving a CID.
     - CID and IV (base64) stored in backend DB via API; hash may be pinned to blockchain.

6. **Orchestration and Tools**:
   - **Docker**: `docker-compose.yml` for Postgres and Hardhat node.
   - **Environment**: `.env.example` for config (e.g., contract address, RPC URL, DB creds). No API key for Storacha; uses email-based auth.
   - **Wallet Integration**: MetaMask for all blockchain interactions; supports local Hardhat chain.
   - **Security**: Client-side encryption prevents backend access to sensitive data. Wallet signatures for auth.

### Data Flow Example (Buyer Submits Claim)
1. Buyer connects MetaMask in frontend → Signs transaction to call `submitClaim` on smart contract → Emits `ClaimSubmitted` event.
2. Event listener in backend detects event → Updates DB with claim status.
3. Buyer uploads encrypted document via frontend → Encrypted blob to Storacha → CID returned and stored in DB via API.
4. Admin views claim in backend admin panel → Verifies → Calls `verifyClaim` on smart contract → Payout triggered.
5. All on-chain actions logged immutably; off-chain data synced for UI.

### High-Level Diagram
```
[MetaMask Wallet] <--> [Frontend (React + Web3.js)] <--> [Smart Contracts (Hardhat/Solidity)]
                          |                                 |
                          | API Calls / Events              | RPC / Event Listener
                          v                                 v
                    [Backend (Django + Web3.py)] <--> [PostgreSQL DB]
                          |
                          v
                   [Storacha (Decentralized Storage)]
```

This architecture ensures:
- **Decentralization**: Core logic and documents on blockchain/IPFS.
- **Privacy**: Encryption for sensitive data.
- **Scalability**: Off-chain DB for queries, on-chain for trust.
- **Security**: Wallet-based auth, no central key storage.

## Setup and Run Instructions

### Prerequisites
- **OS**: Windows 11 (as per system info), but cross-platform compatible.
- **Node.js**: v18+ (for frontend and Hardhat).
- **Python**: 3.10+ (for backend).
- **PostgreSQL**: Local install or use Docker/Neon.
- **MetaMask**: Browser extension installed and configured for local network (RPC: http://127.0.0.1:8545, Chain ID: 31337).
- **Git**: For cloning (if needed).
- **Docker**: Optional, for easy DB and node setup.
- Install global tools: `npm install -g hardhat`, `pip install virtualenv` (if needed).

### Step 1: Clone and Prepare Environment
1. Ensure you're in the project root: `f:/web3/hybrid_Insurance  reviced`.
2. Copy `.env.example` to `.env` in root, `backend/`, and `frontend/` (create if missing).
3. Edit `.env` files:
   - **Root/Backend**:
     ```
     SECRET_KEY=your-django-secret-key-here  # Generate a secure one
     DEBUG=True
     DB_NAME=health_insurance_db
     DB_USER=postgres
     DB_PASSWORD=password  # Change for security
     DB_HOST=localhost
     DB_PORT=5432
     HARDHAT_RPC_URL=http://127.0.0.1:8545
     CONTRACT_ADDRESS=  # Will be filled after deployment
     # No STORACHA_API_KEY needed; uses @storacha/client with email login
     ```
   - **Frontend** (`frontend/.env`):
     ```

### Storacha Setup (Before Running Frontend)
1. Install client (already done via `npm install @storacha/client` in frontend).
2. For first use:
   - Prepare a valid email for login (e.g., Gmail; must confirm links).
   - When uploading in app, provide email; check email for confirmation link and click it (await in console).
   - If prompted, select a payment plan (free tier if available; requires account setup).
3. In production: Handle login/space per user (store credentials securely, e.g., via wallet-derived keys); avoid fixed space name.
4. Testing: Upload returns CID; view at https://[CID].ipfs.storacha.link. Fallback to stub if issues.
5. Docs: See @storacha/client README for advanced options (e.g., custom gateways, directories).
     VITE_CONTRACT_ADDRESS=  # Will be filled after deployment
     VITE_BACKEND_URL=http://localhost:8000
     VITE_RPC_URL=http://127.0.0.1:8545
     ```
4. For Neon Postgres (cloud): Update `DATABASE_URL=postgresql://user:pass@neon-host/dbname` in backend `.env`.

### Step 2: Set Up and Run Smart Contracts (Hardhat)
1. Install dependencies:
   ```
   npm install
   ```
2. Start local blockchain node (in one terminal):
   ```
   npx hardhat node
   ```
   - This runs on http://127.0.0.1:8545. Keep it running.
   - Note the private keys for test accounts (e.g., Account #0: 0xac0974...).
3. Deploy contract (in another terminal):
   ```
   npx hardhat run scripts/deploy.js --network localhost
   ```
   - Console will output the `HealthInsurance` contract address (e.g., `0x5FbD...`).
   - Copy this address to `CONTRACT_ADDRESS` in backend `.env` and `VITE_CONTRACT_ADDRESS` in frontend `.env`.
4. Run tests (optional):
   ```
   npx hardhat test
   ```

**Alternative with Docker** (if using docker-compose.yml):
```
docker-compose up postgres hardhat-node
```
- Then deploy as above.

### Step 3: Set Up and Run Backend (Django)
1. Navigate to backend:
   ```
   cd backend
   ```
2. Create virtual environment and install dependencies:
   ```
   python -m venv venv
   # Activate: On Windows: venv\Scripts\activate
   pip install -r requirements.txt  # If exists; else:
   pip install django djangorestframework psycopg2-binary web3 python-dotenv celery redis  # Add if needed for tasks
   ```
   - Note: `requirements.txt` may not exist; install manually as listed.
3. Apply migrations and create superuser:
   ```
   python manage.py migrate
   python manage.py createsuperuser  # Username/password for admin
   ```
4. Start Django server (in one terminal):
   ```
   python manage.py runserver
   ```
   - Access API at http://localhost:8000/api/ (e.g., http://localhost:8000/admin/ for dashboard).
5. Start event listener (in another terminal, from backend dir):
   ```
   python myapp/event_listener.py
   ```
   - This syncs blockchain events to DB. Keep running.
6. Seed initial data (optional, via Django shell):
   ```
   python manage.py shell
   ```
   Then in shell:
   ```python
   from myapp.models import Buyer
   buyer = Buyer.objects.create(wallet_address="0xYourTestWallet", national_id="ID123", full_name="John Doe")
   print(buyer)
   exit()
   ```

### Step 4: Set Up and Run Frontend (React)
1. Navigate to frontend:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start dev server:
   ```
   npm run dev
   ```
   - Runs on http://localhost:3000. Open in browser with MetaMask.

### Step 5: Running the Full Stack
1. Ensure all services are running:
   - Hardhat node (terminal 1).
   - Django server (terminal 2).
   - Event listener (terminal 3).
   - Frontend dev server (terminal 4).
2. Configure MetaMask:
   - Add network: RPC URL `http://127.0.0.1:8545`, Chain ID `31337`, Currency `ETH`.
   - Import test account private key from Hardhat output (e.g., `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`).
   - Fund account via Hardhat console if needed.
3. Interact:
   - Open http://localhost:3000.
   - Connect wallet → Pay premium → Submit claim (upload file) → View in admin panel.
4. Test Encryption/Storage:
   - For Storacha: Provide email in upload flow (e.g., via UI prompt); confirm email link if first time, select payment plan. Check console for real CID.
   - Documents encrypted client-side; accessible via https://{cid}.ipfs.storacha.link.

### Troubleshooting
- **Hardhat Node Not Starting**: Ensure port 8545 free; check `hardhat.config.js`.
- **DB Connection Error**: Verify Postgres running (`docker-compose up postgres` or local service). Check env vars.
- **Contract Address Missing**: Redeploy and update .env files; restart services.
- **MetaMask Connection Fails**: Ensure network matches; clear cache.
- **API 404/500**: Run `python manage.py migrate`; check Django logs.
- **Encryption Errors**: Use valid key; runtime is browser-only (Web Crypto API).
- **No Event Sync**: Ensure listener connected to correct RPC; check Web3.py logs.
- **Storacha Upload Fails**:
  - Email confirmation timeout: Check inbox/spam for link; login expires after ~15 min.
  - Payment Plan: After email confirm, select a plan via Storacha dashboard/email prompt.
  - Space Creation: Fixed name 'insurance-dapp-space'; recreate if access lost (but risk data loss).
  - Fallback: Code falls back to fake CID if real upload fails.
  - View Uploads: Use https://{cid}.ipfs.storacha.link in browser.
- **Large Files**: Base64 encoding may hit limits; optimize for production.
- **Production Deployment**:
  - Contracts: `npx hardhat run scripts/deploy.js --network sepolia` (testnet).
  - Backend: Heroku/Railway with Neon Postgres.
  - Frontend: Vercel/Netlify; build with `npm run build`.
  - Storacha: Already integrated in frontend; for backend uploads, find Python equivalent or proxy via frontend.
  - Implement JWT/wallet sig auth for APIs.
  - Secure keys with env/secrets manager.

For questions, refer to README.md or expand this file. Project is demo-ready; production needs security audits.