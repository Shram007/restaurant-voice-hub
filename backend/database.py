import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

# Fallback for local dev if not set (user should set these in env)
if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")

supabase: Client = create_client(url, key)
