from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from backend.database import supabase


class StatsService:
    @staticmethod
    def _resolve_time_window(
        time_range: str = "today",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        now = datetime.utcnow()

        def _parse_iso(value: Optional[str]) -> Optional[datetime]:
            if not value:
                return None
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
            except Exception:
                return None

        if time_range == "custom":
            start = _parse_iso(start_date)
            end = _parse_iso(end_date) or now
            if start:
                return start.isoformat(), end.isoformat()

        if time_range == "week":
            return (now - timedelta(days=7)).isoformat(), now.isoformat()
        if time_range == "month":
            return (now - timedelta(days=30)).isoformat(), now.isoformat()
        if time_range == "year":
            return (now - timedelta(days=365)).isoformat(), now.isoformat()

        start_of_day = datetime(now.year, now.month, now.day)
        return start_of_day.isoformat(), now.isoformat()

    @staticmethod
    def _flatten_call_log(record: Dict[str, Any]) -> Dict[str, Any]:
        payload = record.get("data") or {}
        if not isinstance(payload, dict):
            payload = {}

        raw_outcome = payload.get("outcome", record.get("type"))
        outcome = "transferred" if raw_outcome == "handoff" else raw_outcome

        return {
            **record,
            "phone": payload.get("phone", record.get("phone")),
            "duration": payload.get("duration", record.get("duration")),
            "outcome": outcome,
            "transfer_reason": payload.get("reason", record.get("transfer_reason")),
            "timestamp": record.get("created_at"),
        }

    @staticmethod
    def get_stats(restaurant_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            start_iso, _ = StatsService._resolve_time_window("today")

            orders_query = supabase.table("orders").select("*").gte("created_at", start_iso)
            if restaurant_id:
                orders_query = orders_query.eq("restaurant_id", restaurant_id)
            orders_resp = orders_query.execute()
            orders = orders_resp.data

            calls_query = supabase.table("call_logs").select("*", count="exact").gte("created_at", start_iso)
            if restaurant_id:
                calls_query = calls_query.eq("restaurant_id", restaurant_id)
            calls_resp = calls_query.execute()

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
    def get_call_logs(
        restaurant_id: Optional[str] = None,
        time_range: str = "today",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        try:
            start_iso, end_iso = StatsService._resolve_time_window(time_range, start_date, end_date)

            query = supabase.table("call_logs").select("*").order("created_at", desc=True)
            query = query.gte("created_at", start_iso).lte("created_at", end_iso)
            if restaurant_id:
                query = query.eq("restaurant_id", restaurant_id)

            response = query.execute()
            return [StatsService._flatten_call_log(record) for record in response.data]
        except:
            return []

    @staticmethod
    def get_call_detail(call_id: str, restaurant_id: Optional[str] = None):
        try:
            query = supabase.table("call_logs").select("*").eq("id", call_id)
            if restaurant_id:
                query = query.eq("restaurant_id", restaurant_id)

            response = query.single().execute()
            return StatsService._flatten_call_log(response.data) if response.data else None
        except:
            return None

    @staticmethod
    def get_faqs_list(restaurant_id: str):
        try:
            response = supabase.table("faqs").select("*").eq("restaurant_id", restaurant_id).execute()
            return response.data
        except Exception:
            return []

    @staticmethod
    def bulk_replace_faqs(restaurant_id: str, faqs: List[Dict[str, Any]]):
        try:
            sanitized = [
                {
                    "restaurant_id": restaurant_id,
                    "question": faq.get("question", "").strip(),
                    "answer": faq.get("answer", "").strip(),
                }
                for faq in faqs
                if faq.get("question") and faq.get("answer")
            ]

            supabase.table("faqs").delete().eq("restaurant_id", restaurant_id).execute()

            if sanitized:
                supabase.table("faqs").insert(sanitized).execute()

            return {"status": "success", "count": len(sanitized)}
        except Exception:
            raise
