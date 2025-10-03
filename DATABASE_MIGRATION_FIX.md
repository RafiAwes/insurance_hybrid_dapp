# Database Migration Fix

## 🚨 Problem Identified
The error shows that the database columns for the new Buyer model fields don't exist:
```
column insurance_buyer.total_premiums_paid does not exist
```

This means the database migrations haven't been applied yet.

## ✅ Solution Steps

### 1. **Run Database Migrations**
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 2. **If Migration Fails, Reset and Recreate**
If you get migration conflicts, you can reset:

```bash
cd backend
# Remove existing migration files (keep __init__.py)
rm insurance/migrations/0*.py

# Create fresh migrations
python manage.py makemigrations insurance

# Apply migrations
python manage.py migrate
```

### 3. **Create Test Accounts**
After migrations are successful:
```bash
python ../create_test_accounts.py
```

### 4. **Start Server**
```bash
python manage.py runserver
```

## 🔧 Alternative: Manual Database Update

If migrations still fail, you can manually add the columns:

```sql
-- Connect to your PostgreSQL database and run:
ALTER TABLE insurance_buyer ADD COLUMN total_premiums_paid DECIMAL(30,18) DEFAULT 0;
ALTER TABLE insurance_buyer ADD COLUMN last_premium_payment TIMESTAMP NULL;
ALTER TABLE insurance_buyer ADD COLUMN premium_payment_count INTEGER DEFAULT 0;
ALTER TABLE insurance_buyer ADD COLUMN claim_documents JSONB DEFAULT '[]';
ALTER TABLE insurance_buyer ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE insurance_buyer ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
```

## 📋 Complete Setup Sequence

```bash
# 1. Navigate to backend
cd backend

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create test accounts
cd ..
python create_test_accounts.py

# 4. Start server
cd backend
python manage.py runserver
```

## 🎯 Expected Result

After running migrations, you should see:
- ✅ Database tables updated with new columns
- ✅ Login works without database errors
- ✅ Test accounts created successfully
- ✅ Full system functionality

## 🐛 If Still Having Issues

1. **Check Migration Status**:
   ```bash
   python manage.py showmigrations
   ```

2. **Check Database Connection**:
   - Ensure PostgreSQL is running
   - Verify DATABASE_URL in .env file

3. **Reset Database** (if needed):
   ```bash
   python manage.py flush
   python manage.py migrate
   ```

The key issue is that the database schema needs to be updated to match the new Buyer model fields!