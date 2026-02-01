from fastapi import APIRouter, Depends, HTTPException
from backend.models import POSConnectRequest
from backend.pos_service import POSService
from backend.database import supabase
from datetime import datetime

router = APIRouter(tags=["POS"])

@router.post("/connect")
def connect_pos(req: POSConnectRequest):
    # Verify connection
    is_valid = POSService.verify_connection(req.provider, req.api_key)
    
    if is_valid:
        # Save or update config in Supabase
        pos_data = {
            "provider": req.provider,
            "api_key": req.api_key,
            "is_connected": True,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        try:
            # We'll use upsert based on provider for now
            supabase.table("pos_settings").upsert(pos_data, on_conflict="provider").execute()
            return {"success": True, "message": f"Successfully connected to {POSService.get_provider_name(req.provider)}"}
        except Exception as e:
            print(f"Error saving POS settings: {e}")
            # Even if DB fails, the verification succeeded for the session? 
            # No, let's return error if DB fails.
            raise HTTPException(status_code=500, detail="Failed to save POS settings")
    else:
        return {"success": False, "message": "Invalid API key or connection failed"}

@router.get("/status")
def get_pos_status():
    try:
        response = supabase.table("pos_settings").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching POS status: {e}")
        return []
