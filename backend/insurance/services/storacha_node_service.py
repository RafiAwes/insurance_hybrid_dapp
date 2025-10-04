import os
import json
import subprocess
import tempfile
from django.conf import settings

class StorachaNodeService:
    def __init__(self):
        # Get Storacha admin email from environment variables
        self.admin_email = os.getenv('STORACHA_ADMIN_EMAIL', 'admin@healthinsurance.com')
        self.space_did = 'did:key:z6Mks2sfn2CcTcEXho661oVoB26hwjd4NdAR1UQ1JiHVdKPZ'
        
    def login(self, email):
        """
        Login to Storacha using Node.js service
        """
        try:
            # Prepare data for Node.js service
            data = {
                'email': email
            }
            
            # Call Node.js service for login
            result = self._call_node_service('login', data)
            return result
        except Exception as e:
            print(f"Error logging into Storacha: {str(e)}")
            raise e
    
    def upload_claim_data(self, buyer_data, claim_data):
        """
        Upload claim data to Storacha using Node.js service
        """
        try:
            # Prepare data for Node.js service
            data = {
                'adminEmail': self.admin_email,
                'spaceDid': self.space_did,
                'buyer': buyer_data,
                'claim': claim_data
            }
            
            # Call Node.js service
            result = self._call_node_service('upload_claim', data)
            return result.get('cid')
        except Exception as e:
            print(f"Error uploading claim data to Storacha: {str(e)}")
            raise e
    
    def upload_premium_data(self, buyer_data, premium_data):
        """
        Upload premium data to Storacha using Node.js service
        """
        try:
            # Prepare data for Node.js service
            data = {
                'adminEmail': self.admin_email,
                'spaceDid': self.space_did,
                'buyer': buyer_data,
                'premium': premium_data
            }
            
            # Call Node.js service
            result = self._call_node_service('upload_premium', data)
            return result.get('cid')
        except Exception as e:
            print(f"Error uploading premium data to Storacha: {str(e)}")
            raise e
    
    def fetch_from_cid(self, cid):
        """
        Fetch data from Storacha using CID
        """
        try:
            # For now, we'll return a stub implementation
            # In production, this would fetch from https://${cid}.ipfs.storacha.link
            print(f"Fetching data from Storacha CID: {cid}")
            # This would be implemented to fetch from the gateway
            return None
        except Exception as e:
            print(f"Error fetching data from Storacha: {str(e)}")
            raise e
    
    def _call_node_service(self, operation, data):
        """
        Call Node.js service to perform Storacha operations
        """
        try:
            # Create temporary file with data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(data, temp_file)
                temp_file_path = temp_file.name
            
            # Get the path to the Node.js service script
            node_script_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'services',
                'storacha_client.js'
            )
            
            # Call Node.js service
            result = subprocess.run([
                'node', 
                node_script_path, 
                operation, 
                temp_file_path
            ], capture_output=True, text=True, timeout=30)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if result.returncode != 0:
                raise Exception(f"Node.js service failed: {result.stderr}")
            
            # Parse result
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Error calling Node.js service: {str(e)}")
            raise e