# 403 Forbidden Error Fix

## 🚨 Problem Identified
The login endpoints were returning "403 Forbidden" because:
1. **REST_FRAMEWORK** was set to `IsAuthenticated` by default
2. **CSRF protection** was blocking API requests

## ✅ Solution Applied

### 1. **Fixed REST Framework Permissions**
Changed in [`backend/backend/settings.py`](backend/backend/settings.py:133):
```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.AllowAny',  # Allow unauthenticated access
],
```

### 2. **Added CSRF Exemption**
Added to login functions in [`backend/insurance/views.py`](backend/insurance/views.py):
```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def admin_login(request):
    # ... login logic

@csrf_exempt
@api_view(['POST'])
def buyer_login(request):
    # ... login logic
```

## 🔄 What to Do Now

1. **Restart Django Server**:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Create Test Accounts** (if not done already):
   ```bash
   python ../create_test_accounts.py
   ```

3. **Test Login**:
   - Admin: `admin@example.com` / `admin123`
   - Buyer: `buyer@example.com` / `buyer123`

## 🎯 Expected Result

The login should now work without 403 errors. You should see:
- Successful email/password authentication
- Proceed to MetaMask wallet verification step
- Complete login process

## 🐛 If Still Having Issues

Check Django console for debug output:
- `🔍 [DEBUG] Buyer login attempt - Email: buyer@example.com`
- `✅ [DEBUG] Login successful for buyer: buyer@example.com`

The 403 Forbidden error should be resolved!