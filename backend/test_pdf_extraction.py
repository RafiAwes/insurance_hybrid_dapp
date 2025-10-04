import sys
import os
import django
from unittest.mock import patch, Mock
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import the extraction function
from insurance.views import extract_claim_data_from_pdf

# Create a mock PDF file with test content
pdf_content = """
INVOICE
=======
Transaction ID: WM9pe6ds
Patient Name: John Doe
Service Date: 2025-10-04
Description: Medical treatment
Amount: $10,000.00
Total: $10,000.00
"""

# Mock the PyPDF2.PdfReader to return our test content
class MockPdfReader:
    def __init__(self, file):
        self.pages = [MockPage()]
    
class MockPage:
    def extract_text(self):
        return pdf_content

# Test the extraction function
print("Testing PDF extraction...")
with patch('insurance.views.PyPDF2.PdfReader', MockPdfReader):
    # Create a mock file object
    mock_file = BytesIO(b"fake pdf content")
    mock_file.name = "test.pdf"
    
    result = extract_claim_data_from_pdf(mock_file)
    print("Extraction result:", result)
    print("Transaction ID:", result.get('transaction_id'))
    print("Amount:", result.get('amount'))