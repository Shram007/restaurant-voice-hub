import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

# Fallback for local dev if not set (user should set these in env)
if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_API_KEY not found in environment variables.")

supabase: Client = create_client(url, key)
