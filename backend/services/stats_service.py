from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database import supabase

class StatsService:
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        try:
            today_start = datetime.utcnow().date().isoformat()
            
            orders_resp = supabase.table("orders").select("*").gte("created_at", today_start).execute()
            orders = orders_resp.data
            
            calls_resp = supabase.table("call_logs").select("*", count="exact").gte("created_at", today_start).execute()
            calls_count = calls_resp.count or 0
            
            confirmed_orders = [o for o in orders if o["status"] == "confirmed"]
            revenue = sum(float(o["total"]) for o in confirmed_orders)
            
            return {
                "aiStatus": "online",
                "callsToday": calls_count, 
                "ordersToday": len(orders),
                "revenue": revenue,
                "avgOrderValue": revenue / len(confirmed_orders) if confirmed_orders else 0,
                "conversionRate": 0,
                "avgCallDuration": "0:00", 
                "fallbackRate": 0,
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {}

    @staticmethod
    def get_call_logs(restaurant_id: Optional[str] = None):
        try:
            return supabase.table("call_logs").select("*").order("created_at", desc=True).execute().data
        except:
            return []

    @staticmethod
    def get_faqs_list(restaurant_id: str):
        try:
            response = supabase.table("faqs").select("*").eq("restaurant_id", restaurant_id).execute()
            return response.data
        except Exception as e:
            return []
