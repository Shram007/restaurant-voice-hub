import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from backend.database import supabase
from backend.models import (
    OrderCreateRequest, OrderResponse, EtaResponse, 
    OrderConfirmRequest, OrderConfirmResponse, HandoffRequest, HandoffResponse
)
from backend.services.menu_service import MenuService
from backend.config import settings

class OrderService:
    @staticmethod
    def _calculate_eta_internal(restaurant_id: str) -> int:
        base_eta = settings.BASE_ETA_MINUTES
        try:
            one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
            response = supabase.table("orders") \
                .select("count", count="exact") \
                .eq("restaurant_id", restaurant_id) \
                .eq("status", "confirmed") \
                .gt("created_at", one_hour_ago) \
                .execute()
            
            count = response.count or 0
            adjustment = min(count * 2, 30)
            return base_eta + adjustment
        except:
            return base_eta

    @staticmethod
    def create_or_update_order(req: OrderCreateRequest) -> OrderResponse:
        # Fetch menu once
        menu = MenuService.get_menu(req.restaurant_id)
        menu_map = {item.item_id: item for item in menu}
        
        order_id = req.order_id or str(uuid.uuid4())
        validation_errors = []
        subtotal = 0.0
        valid_items = []
        
        for item in req.items:
            if item.item_id not in menu_map:
                print(f"Validation Error: Item {item.item_id} not found. Available IDs: {list(menu_map.keys())}")
                validation_errors.append(f"Item {item.item_id} not found")
                continue
                
            menu_item = menu_map[item.item_id]
            if not menu_item.availability:
                validation_errors.append(f"Item {menu_item.name} is unavailable")
                continue
                
            subtotal += menu_item.price * item.quantity
            
            # Flatten item for storage
            item_dict = item.dict()
            item_dict["name"] = menu_item.name
            item_dict["price"] = menu_item.price
            valid_items.append(item_dict)

        tax = subtotal * settings.TAX_RATE
        total = subtotal + tax
        status = "draft"
        
        # Preserve existing status if updating
        try:
            existing = supabase.table("orders").select("status").eq("order_id", order_id).execute()
            if existing.data:
                status = existing.data[0]["status"]
        except:
            pass
        
        # Identify missing fields
        missing = []
        if not req.customer_name: missing.append("customer_name")
        if not req.phone: missing.append("phone")
        if not req.items: missing.append("items")
        
        # Save to DB
        order_data = {
            "order_id": order_id,
            "restaurant_id": req.restaurant_id,
            "call_id": req.call_id,
            "fulfillment": req.fulfillment,
            "customer_name": req.customer_name,
            "phone": req.phone,
            "items": valid_items,
            "notes": req.notes,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "status": status
        }
        
        try:
            supabase.table("orders").upsert(order_data).execute()
        except Exception as e:
            print(f"Error saving order: {e}")
        
        return OrderResponse(
            order_id=order_id,
            status=status,
            subtotal=round(subtotal, 2),
            tax=round(tax, 2),
            total=round(total, 2),
            missing_fields=missing,
            validation_errors=validation_errors
        )

    @staticmethod
    def get_eta(restaurant_id: str) -> EtaResponse:
        eta = OrderService._calculate_eta_internal(restaurant_id)
        return EtaResponse(
            eta_minutes=eta,
            ready_time_iso=(datetime.now() + timedelta(minutes=eta)).isoformat(),
            reason="Based on current kitchen load"
        )

    @staticmethod
    def confirm_order(req: OrderConfirmRequest) -> OrderConfirmResponse:
        try:
            response = supabase.table("orders").select("*").eq("order_id", req.order_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Order not found")
            
            order = response.data[0]
            
            # Validate readiness
            if not order["customer_name"] or not order["phone"] or not order["items"]:
                raise HTTPException(status_code=400, detail="Missing required fields for confirmation")
                
            # Update status
            supabase.table("orders").update({"status": "confirmed"}).eq("order_id", req.order_id).execute()
            
            eta = OrderService._calculate_eta_internal(req.restaurant_id)
            payment_link = f"https://example.com/pay/{req.order_id}" if req.payment_mode == "payment_link" else None
                
            return OrderConfirmResponse(
                confirmed=True,
                order_id=req.order_id,
                total=round(float(order["total"]), 2),
                pickup_eta_minutes=eta,
                payment_link=payment_link,
                pos_provider="none",
                pos_order_id=None
            )
        except Exception as e:
            if isinstance(e, HTTPException): raise e
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def handoff_to_human(req: HandoffRequest) -> HandoffResponse:
        try:
            supabase.table("call_logs").insert({
                "type": "handoff",
                "data": req.dict()
            }).execute()
        except Exception as e:
            print(f"Error logging handoff: {e}")
            
        return HandoffResponse(
            transferred=False,
            message="Handoff requested; please call the restaurant directly."
        )

    @staticmethod
    def get_orders(restaurant_id: Optional[str] = None):
        try:
            query = supabase.table("orders").select("*").order("created_at", desc=True)
            if restaurant_id:
                query = query.eq("restaurant_id", restaurant_id)
            return query.execute().data
        except:
            return []
