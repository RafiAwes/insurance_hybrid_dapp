import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from insurance.models import Buyer

# Get all buyers
buyers = Buyer.objects.all()

print("Buyers in database:")
for buyer in buyers:
    print(f"Wallet: {buyer.wallet_address} - Name: {buyer.full_name} - Email: {buyer.email}")