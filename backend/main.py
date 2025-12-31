from fastapi import FastAPI, HTTPException, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uuid
import io
import csv
import json

# Relative/Absolute Import Handling
try:
    from backend.database import supabase
    from backend.models import (
        MenuItem, MenuResponse, OrderCreateRequest, OrderResponse, 
        EtaRequest, EtaResponse, OrderConfirmRequest, OrderConfirmResponse, 
        HandoffRequest, HandoffResponse, AvailabilityUpdate
    )
    from backend.crud import get_menu_from_db, get_orders, get_call_logs, get_faqs_list
except ImportError:
    from database import supabase
    from models import (
        MenuItem, MenuResponse, OrderCreateRequest, OrderResponse, 
        EtaRequest, EtaResponse, OrderConfirmRequest, OrderConfirmResponse, 
        HandoffRequest, HandoffResponse, AvailabilityUpdate
    )
    from crud import get_menu_from_db, get_orders, get_call_logs, get_faqs_list

app = FastAPI()

# Configuration
DEFAULT_RESTAURANT_ID = "rest_123"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"ok": True, "time": datetime.now().isoformat()}

# --- Tools (ElevenLabs) ---

@app.get("/tool/menu_search", response_model=MenuResponse)
def menu_search(restaurant_id: str = DEFAULT_RESTAURANT_ID, query: str = None, limit: int = 20):
    try:
        # MVP: Client-side filtering in python since Supabase OR query is verbose
        all_items = get_menu_from_db(restaurant_id)
        
        if not query:
            return {"matches": all_items[:limit], "notes": "Listing full menu"}

        matches = []
        q = query.lower()
        for item in all_items:
            if q in item.name.lower() or q in item.category.lower():
                matches.append(item)
            
        return {"matches": matches[:limit], "notes": f"Found {len(matches)} items for '{query}'"}
    except Exception as e:
        print(f"Search error: {e}")
        return {"matches": [], "notes": "Error searching menu"}

@app.post("/tool/order_create_or_update", response_model=OrderResponse)
def order_create_or_update(req: OrderCreateRequest):
    # Fetch menu once
    menu = get_menu_from_db(req.restaurant_id)
    menu_map = {item.item_id: item for item in menu}
    
    order_id = req.order_id or str(uuid.uuid4())
    validation_errors = []
    subtotal = 0.0
    valid_items = []
    
    for item in req.items:
        if item.item_id not in menu_map:
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

    tax = subtotal * 0.08875
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
    
    return {
        "order_id": order_id,
        "status": status,
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
        "missing_fields": missing,
        "validation_errors": validation_errors
    }

def _calculate_eta_internal(restaurant_id: str) -> int:
    base_eta = 30
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

@app.post("/tool/get_eta", response_model=EtaResponse)
def get_eta(req: EtaRequest):
    eta = _calculate_eta_internal(req.restaurant_id)
    return {
        "eta_minutes": eta,
        "ready_time_iso": (datetime.now() + timedelta(minutes=eta)).isoformat(),
        "reason": "Based on current kitchen load"
    }

@app.post("/tool/order_confirm", response_model=OrderConfirmResponse)
def order_confirm(req: OrderConfirmRequest):
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
        
        eta = _calculate_eta_internal(req.restaurant_id)
        payment_link = f"https://example.com/pay/{req.order_id}" if req.payment_mode == "payment_link" else None
            
        return {
            "confirmed": True,
            "order_id": req.order_id,
            "total": round(float(order["total"]), 2),
            "pickup_eta_minutes": eta,
            "payment_link": payment_link,
            "pos_provider": "none",
            "pos_order_id": None
        }
    except Exception as e:
        # Rethrow HTTP exceptions, catch others
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tool/handoff_to_human", response_model=HandoffResponse)
def handoff_to_human(req: HandoffRequest):
    try:
        supabase.table("call_logs").insert({
            "type": "handoff",
            "data": req.dict()
        }).execute()
    except Exception as e:
        print(f"Error logging handoff: {e}")
        
    return {
        "transferred": False,
        "message": "Handoff requested; please call the restaurant directly."
    }

# --- Dashboard / Admin Endpoints ---

@app.get("/menu")
def get_menu():
    return get_menu_from_db(DEFAULT_RESTAURANT_ID)

@app.put("/menu/{item_id}/availability")
def update_item_availability(item_id: str, update: AvailabilityUpdate):
    try:
        response = supabase.table("menu_items").update({"availability": update.available}).eq("item_id", item_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"status": "success", "item_id": item_id, "available": update.available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/menu/upload")
async def upload_menu(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    
    new_items = []
    for row in reader:
        item_id = str(uuid.uuid4())[:8]
        new_items.append({
            "item_id": item_id,
            "restaurant_id": DEFAULT_RESTAURANT_ID,
            "name": row.get("name", "Unknown"),
            "category": row.get("category", "General"),
            "price": float(row.get("price", 0.0)),
            "availability": True,
            "modifiers": []
        })
    
    try:
        # Replace mode: delete existing, insert new
        supabase.table("menu_items").delete().eq("restaurant_id", DEFAULT_RESTAURANT_ID).execute()
        supabase.table("menu_items").insert(new_items).execute()
        return {"message": f"Uploaded {len(new_items)} items", "items_count": len(new_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
def get_orders_dashboard(restaurant_id: str = DEFAULT_RESTAURANT_ID):
    return get_orders(restaurant_id)

@app.get("/calls")
def get_calls_dashboard(restaurant_id: str = DEFAULT_RESTAURANT_ID):
    return get_call_logs(restaurant_id)

@app.get("/faqs")
def get_faqs():
    return get_faqs_list(DEFAULT_RESTAURANT_ID)

@app.get("/stats")
def get_stats():
    try:
        today_start = datetime.utcnow().date().isoformat()
        
        # Reuse CRUD logic or keep bespoke stats logic here
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
