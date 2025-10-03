#!/usr/bin/env python
"""
Quick script to create test admin and buyer accounts
Run this from the backend directory: python ../create_test_accounts.py
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup Django
django.setup()

from insurance.models import Admin, Buyer
from django.utils import timezone

def create_admin():
    """Create test admin account"""
    email = "admin@example.com"
    password = "admin123"
    full_name = "System Admin"
    
    # Check if admin already exists
    if Admin.objects.filter(email=email).exists():
        print(f"✅ Admin {email} already exists")
        return
    
    # Create admin
    admin = Admin(
        email=email,
        full_name=full_name,
        is_active=True
    )
    admin.set_password(password)
    admin.save()
    
    print(f"✅ Created admin: {email}")
    print(f"   Password: {password}")
    print(f"   Required wallet: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

def create_buyer():
    """Create test buyer account"""
    email = "buyer@example.com"
    password = "buyer123"
    full_name = "Test Buyer"
    wallet_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    national_id = "123456789"
    
    # Check if buyer already exists
    if Buyer.objects.filter(email=email).exists():
        print(f"✅ Buyer {email} already exists")
        return
    
    if Buyer.objects.filter(wallet_address=wallet_address).exists():
        print(f"✅ Buyer with wallet {wallet_address} already exists")
        return
    
    # Create buyer
    buyer = Buyer(
        email=email,
        full_name=full_name,
        wallet_address=wallet_address,
        national_id=national_id,
        phone="",
        is_active=True,
        # Initialize new fields with defaults
        total_premiums_paid=0,
        premium_payment_count=0,
        claim_documents=[]
    )
    buyer.set_password(password)
    buyer.save()
    
    print(f"✅ Created buyer: {email}")
    print(f"   Password: {password}")
    print(f"   Wallet: {wallet_address}")

if __name__ == "__main__":
    print("🔧 Creating test accounts...")
    
    try:
        create_admin()
        create_buyer()
        print("\n🎉 Test accounts created successfully!")
        print("\n📋 Login Credentials:")
        print("Admin: admin@example.com / admin123")
        print("Buyer: buyer@example.com / buyer123")
        print("\n🦊 MetaMask Wallets:")
        print("Admin: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
        print("Buyer: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8")
        
    except Exception as e:
        print(f"❌ Error creating accounts: {e}")
        print("Make sure you're running this from the project root and Django is properly configured.")