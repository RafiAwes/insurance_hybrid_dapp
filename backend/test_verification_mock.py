import sys
import os
import django
from unittest.mock import patch, Mock
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

# Mock the requests.get function to simulate API response
def mock_get_success(*args, **kwargs):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "paid", 
        "message": "Transaction verified successfully", 
        "transaction_id": "WM9pe6ds", 
        "amount": "10000.00", 
        "date": "2025-10-04T09:52:05.730083+00:00"
    }
    return mock_response

def mock_get_failure(*args, **kwargs):
    mock_response = Mock()
    mock_response.status_code = 404
    return mock_response

# Test with successful response
print("Testing with successful API response...")
with patch('requests.get', side_effect=mock_get_success):
    result = verify_transaction_id('WM9pe6ds')
    print("Verification result:", result)
    print("Success status:", result.get('success'))

print("\nTesting with failed API response...")
with patch('requests.get', side_effect=mock_get_failure):
    result = verify_transaction_id('WM9pe6ds')
    print("Verification result:", result)
    print("Success status:", result.get('success'))