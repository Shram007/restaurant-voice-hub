from supabase import create_client, Client
from backend.config import settings

# Fallback for local dev if not set
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_API_KEY not found in environment variables.")

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
