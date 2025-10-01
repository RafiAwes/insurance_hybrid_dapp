from django.conf import settings

class StorachaService:
    def __init__(self):
        # No API key needed; uploads via frontend JS client. Backend handles metadata/CID storage.
        # If Python client available, integrate here; for now, stub for compatibility.
        self.client = None  # Placeholder

    def upload_encrypted_blob(self, blob, metadata=None):
        """
        Store CID/metadata for Storacha upload (actual upload done client-side).
        blob: Not used; placeholder for compatibility (frontend provides CID).
        metadata: dict with CID from frontend upload, plus 'hospitalTransactionId' or 'doc_id'
        """
        # Since uploads are client-side, this stores/validates CID.
        # For backend-initiated uploads, implement Python client if available.
        if not metadata or 'cid' not in metadata:
            raise ValueError("CID required from client-side upload")
        
        cid = metadata['cid']
        print(f"[Storacha] Stored CID {cid} for metadata: {metadata}")
        
        return {
            'cid': cid,
            'size': len(blob) if blob else 0,  # Approximate from frontend if passed
            'id': metadata.get('id') if metadata else None,
        }

    def download_blob(self, cid):
        """
        Fetch blob from Storacha by CID (for verification; decryption client-side).
        """
        # Stub: In prod, use gateway URL e.g., requests.get(f"https://{cid}.ipfs.storacha.link")
        # Return raw bytes; decryption handled by caller with IV.
        print(f"[Storacha] Fetching {cid} (stub; use gateway in prod)")
        fake_blob = f"Encrypted data for CID {cid}".encode()
        return fake_blob