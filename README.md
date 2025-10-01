# Health Insurance DApp

A decentralized health insurance platform using React + TailwindCSS for frontend, Solidity with Hardhat for smart contracts, Django REST Framework for backend, Neon PostgreSQL for database, and Storacha for decentralized storage of encrypted documents.

## Stack
- **Frontend**: React (Vite) + TailwindCSS + Web3.js + MetaMask
- **Smart Contracts**: Solidity ^0.8.20 + Hardhat
- **Backend**: Django + Django REST Framework + Web3.py
- **Database**: PostgreSQL (Neon or local)
- **Decentralized Storage**: Storacha (stubbed - replace with real SDK)
- **Wallet**: MetaMask

## Actors & Features
- **Admin**: Add buyer, verify claim
- **Buyer**: Pay premium, submit claim with documents, view history
- **Hospital**: Upload encrypted transaction records

## Project Structure
- `contracts/`: Solidity contracts
- `scripts/`: Deployment scripts
- `test/`: Hardhat tests
- `backend/`: Django project
  - `myapp/`: Main app with models, views, serializers, services
- `frontend/`: React app with Vite
  - `src/components/`: UI components
  - `src/services/`: Web3 and contract interactions
  - `src/utils/`: Encryption utilities

## Setup Instructions

### Prerequisites
- Node.js >=18
- Python 3.10+
- PostgreSQL (local or Neon)
- MetaMask browser extension
- Hardhat (for local blockchain)

### 1. Smart Contracts (Hardhat)
```bash
cd project-root  # root of this repo
npm install
npx hardhat node  # Start local blockchain on http://127.0.0.1:8545
# In another terminal
npx hardhat run scripts/deploy.js --network localhost
```
- Note the deployed contract address from console output.
- Run tests: `npx hardhat test`

### 2. Backend (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django djangorestframework psycopg2-binary web3 python-dotenv
python manage.py migrate
python manage.py createsuperuser  # For admin access
python manage.py runserver  # Run on http://localhost:8000
```

#### Event Listener
In a separate terminal:
```bash
cd backend
python myapp/event_listener.py  # Listens to contract events and syncs with DB
```

#### Seed Data
Create initial data:
```bash
python manage.py shell
```
```python
from myapp.models import Buyer
buyer = Buyer.objects.create(
    wallet_address="0x123...", 
    national_id="ID123", 
    full_name="John Doe"
)
print("Buyer created:", buyer)
```

### 3. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev  # Run on http://localhost:3000
```

### 4. Environment Variables
Copy `.env.example` to `.env` in root and backend/frontend as needed.

### Running the Full Stack
1. Start Hardhat node and deploy contract.
2. Set CONTRACT_ADDRESS in .env files.
3. Run Django server and migrate DB.
4. Run event listener.
5. Run React dev server.
6. Connect MetaMask to localhost:8545.
7. Interact via frontend (connect wallet, pay premium, submit claim).

## Environment (.env.example)
```
# Backend .env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost/health_insurance_db
HARDHAT_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0xYourDeployedAddress
STORACHA_API_KEY=your-storacha-key

# Frontend .env
VITE_CONTRACT_ADDRESS=0xYourDeployedAddress
VITE_BACKEND_URL=http://localhost:8000
```

## Storacha Integration
- Current implementation uses stubs in `backend/myapp/services/storacha_service.py` and `frontend/src/utils/encryption.ts`.
- Replace stubs with real Storacha SDK.
- Documents are encrypted client-side before upload.

## Testing
- Hardhat tests: `npx hardhat test`
- Django API tests: Add to `backend/myapp/tests.py` and run `python manage.py test`
- Frontend: Basic smoke tests can be added with Vitest.

## Deployment Notes
- Smart Contracts: Deploy to testnet/mainnet with Hardhat.
- Backend: Deploy to Heroku/Vercel with Neon Postgres.
- Frontend: Build with `npm run build` and deploy to Vercel/Netlify.
- Event Listener: Run as background service (Celery or separate process).

## Troubleshooting
- MetaMask not connecting: Ensure Hardhat node is running.
- DB connection: Check DATABASE_URL in .env.
- Contract calls failing: Verify CONTRACT_ADDRESS and network.
- Encryption: Key is demo-only; implement proper KMS.

For production, secure keys, use proper authentication (JWT for admin, wallet signatures for users), and integrate real Storacha.