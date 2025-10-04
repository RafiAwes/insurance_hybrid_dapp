import sys
import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import the verification function
from insurance.views import verify_transaction_id

# Test the function
result = verify_transaction_id('WM9pe6ds')
print("Verification result:", result)