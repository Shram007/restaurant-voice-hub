import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    # Prefer Service Key for backend operations
    SUPABASE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY", "")
    
    DEFAULT_RESTAURANT_ID: str = "demo_restaurant"
    TAX_RATE: float = 0.08875
    
    # Defaults for calculations
    BASE_ETA_MINUTES: int = 30
    
settings = Settings()
