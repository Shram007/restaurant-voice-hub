import random
from typing import Optional
from datetime import datetime

class POSService:
    @staticmethod
    def verify_connection(provider: str, api_key: str) -> bool:
        """
        Mock verification logic for POS providers.
        In a real app, this would make an API call to the provider.
        """
        if not api_key or len(api_key) < 8:
            return False
        
        # Simulating a successful connection for any key starting with 'sk_'
        # or just random success for now since it's a setup phase.
        if api_key.startswith("sk_") or api_key.startswith("pk_") or "test" in api_key.lower():
            return True
            
        return False

    @staticmethod
    def get_provider_name(provider_id: str) -> str:
        providers = {
            "shift4": "Shift4",
            "square": "Square",
            "clover": "Clover"
        }
        return providers.get(provider_id, provider_id.capitalize())
