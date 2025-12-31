from fastapi import FastAPI, HTTPException, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timedelta
import uuid
import io
import csv
import json
from dateutil import parser
from database import supabase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ModifierOption(BaseModel):
    name: str
    options: List[str]

class MenuItem(BaseModel):
    item_id: str
    name: str
    category: str
    price: float
    availability: bool
    modifiers: List[ModifierOption] = []

class MenuResponse(BaseModel):
    matches: List[MenuItem]
    notes: Optional[str] = None

class ModifierSelection(BaseModel):
    modifier_name: str
    option: str

class OrderItem(BaseModel):
    item_id: str
    quantity: int
    modifier_selections: List[ModifierSelection] = []
    special_instructions: Optional[str] = None

class OrderCreateRequest(BaseModel):
    restaurant_id: str
    call_id: str
    order_id: Optional[str] = None
    fulfillment: Literal["pickup", "delivery"] = "pickup"
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    items: List[OrderItem] = []
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    status: Literal["draft", "confirmed", "cancelled"]
    subtotal: float
    tax: float
    total: float
    missing_fields: List[str]
    validation_errors: List[str]

class EtaRequest(BaseModel):
    restaurant_id: str
    order_id: str

class EtaResponse(BaseModel):
    eta_minutes: int
    ready_time_iso: Optional[str] = None
    reason: str

class OrderConfirmRequest(BaseModel):
    restaurant_id: str
    order_id: str
    payment_mode: Literal["pay_at_pickup", "payment_link"] = "pay_at_pickup"

class OrderConfirmResponse(BaseModel):
    confirmed: bool
    order_id: str
    total: float
    pickup_eta_minutes: int
    payment_link: Optional[str] = None
    pos_provider: str = "none"
    pos_order_id: Optional[str] = None

class HandoffRequest(BaseModel):
    restaurant_id: str
    call_id: str
    reason: str
    order_id: Optional[str] = None
    summary_for_human: Optional[str] = None

class HandoffResponse(BaseModel):
    transferred: bool
    message: str

# Helper Functions
def get_menu_from_db(restaurant_id: str) -> List[MenuItem]:
    try:
        response = supabase.table("menu_items").select("*").eq("restaurant_id", restaurant_id).execute()
        items = []
        for record in response.data:
            items.append(MenuItem(
                item_id=record["item_id"],
                name=record["name"],
                category=record["category"],
                price=record["price"],
                availability=record["availability"],
                modifiers=[ModifierOption(**m) for m in record["modifiers"]] if record["modifiers"] else []
            ))
        return items
    except Exception as e:
        print(f"Error fetching menu: {e}")
        return []

def seed_default_menu(restaurant_id: str):
    # Check if menu exists
    existing = get_menu_from_db(restaurant_id)
    if existing:
        return existing
    
    # Seed default items
    default_items = [
        {
            "item_id": "b1",
            "restaurant_id": restaurant_id,
            "name": "Classic Cheeseburger",
            "category": "Burgers",
            "price": 11.99,
            "availability": True,
            "modifiers": [
                {"name": "Cheese", "options": ["American", "Cheddar", "Swiss", "No cheese"]},
                {"name": "Cooking", "options": ["Medium", "Medium Rare", "Well Done"]}
            ]
        },
        {
            "item_id": "p1",
            "restaurant_id": restaurant_id,
            "name": "Margherita Pizza",
            "category": "Pizza",
            "price": 14.99,
            "availability": True,
            "modifiers": []
        },
        {
            "item_id": "d1",
            "restaurant_id": restaurant_id,
            "name": "Cola",
            "category": "Drinks",
            "price": 2.50,
            "availability": True,
            "modifiers": []
        }
    ]
    
    try:
        supabase.table("menu_items").insert(default_items).execute()
        return get_menu_from_db(restaurant_id)
    except Exception as e:
        print(f"Error seeding menu: {e}")
        return []

@app.get("/health")
def health_check():
    return {"ok": True, "time": datetime.now().isoformat()}

@app.get("/tool/menu_search", response_model=MenuResponse)
def menu_search(restaurant_id: str = "rest_123", query: Optional[str] = None, limit: int = 20):
    # Ensure menu exists
    seed_default_menu(restaurant_id)
    
    try:
        query_builder = supabase.table("menu_items").select("*").eq("restaurant_id", restaurant_id)
        
        if query:
            # Using ilike for simple search on name or category
            # Supabase doesn't support OR easily in python client builder for ilike across columns without raw filter
            # So we'll fetch all and filter in python for MVP simplicity or use 'or' filter string
            # query_builder = query_builder.or_(f"name.ilike.%{query}%,category.ilike.%{query}%") 
            # Note: client syntax varies, let's filter in python for reliability in MVP
            pass
            
        response = query_builder.execute()
        matches = []
        
        q = query.lower() if query else None
        for record in response.data:
            if q:
                if q not in record["name"].lower() and q not in record["category"].lower():
                    continue
            
            matches.append(MenuItem(
                item_id=record["item_id"],
                name=record["name"],
                category=record["category"],
                price=record["price"],
                availability=record["availability"],
                modifiers=[ModifierOption(**m) for m in record["modifiers"]] if record["modifiers"] else []
            ))
            
        return {"matches": matches[:limit], "notes": f"Found {len(matches)} items for '{query}'" if query else "Listing full menu"}
        
    except Exception as e:
        print(f"Search error: {e}")
        return {"matches": [], "notes": "Error searching menu"}

@app.post("/menu/upload")
async def upload_menu(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    
    restaurant_id = "rest_123" 
    
    new_items = []
    for row in reader:
        item_id = str(uuid.uuid4())[:8]
        new_items.append({
            "item_id": item_id,
            "restaurant_id": restaurant_id,
            "name": row.get("name", "Unknown"),
            "category": row.get("category", "General"),
            "price": float(row.get("price", 0.0)),
            "availability": True,
            "modifiers": []
        })
    
    try:
        # Delete existing items for this restaurant (replace mode)
        supabase.table("menu_items").delete().eq("restaurant_id", restaurant_id).execute()
        # Insert new
        supabase.table("menu_items").insert(new_items).execute()
        return {"message": f"Uploaded {len(new_items)} items", "items_count": len(new_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/menu")
def get_menu():
    return seed_default_menu("rest_123")

class AvailabilityUpdate(BaseModel):
    available: bool

@app.put("/menu/{item_id}/availability")
def update_item_availability(item_id: str, update: AvailabilityUpdate):
    try:
        response = supabase.table("menu_items").update({"availability": update.available}).eq("item_id", item_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"status": "success", "item_id": item_id, "available": update.available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/faqs")
def get_faqs():
    try:
        response = supabase.table("faqs").select("*").eq("restaurant_id", "rest_123").execute()
        return response.data
    except Exception as e:
        return []

@app.post("/tool/order_create_or_update", response_model=OrderResponse)
def order_create_or_update(req: OrderCreateRequest):
    menu = get_menu_from_db(req.restaurant_id)
    if not menu:
        menu = seed_default_menu(req.restaurant_id)
        
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
            
        # Modifier validation simplified for MVP
        
        subtotal += menu_item.price * item.quantity
        # Store items as dicts for JSONB
        item_dict = item.dict()
        item_dict["name"] = menu_item.name
        item_dict["price"] = menu_item.price
        valid_items.append(item_dict)

    tax = subtotal * 0.08875
    total = subtotal + tax
    
    status = "draft"
    
    # Check if order exists to preserve status
    try:
        existing = supabase.table("orders").select("status").eq("order_id", order_id).execute()
        if existing.data:
            status = existing.data[0]["status"]
    except:
        pass
    
    missing = []
    if not req.customer_name: missing.append("customer_name")
    if not req.phone: missing.append("phone")
    if not req.items: missing.append("items")
    
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
        # In a real app, handle this. For MVP, we might return error or proceed.
    
    return {
        "order_id": order_id,
        "status": status,
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
        "missing_fields": missing,
        "validation_errors": validation_errors
    }

def calculate_eta(restaurant_id: str) -> int:
    base_eta = 30
    try:
        # Get confirmed orders from last hour
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
    eta = calculate_eta(req.restaurant_id)
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
        
        if not order["customer_name"] or not order["phone"] or not order["items"]:
            raise HTTPException(status_code=400, detail="Missing required fields for confirmation")
            
        supabase.table("orders").update({"status": "confirmed"}).eq("order_id", req.order_id).execute()
        
        eta = calculate_eta(req.restaurant_id)
        payment_link = None
        if req.payment_mode == "payment_link":
            payment_link = f"https://example.com/pay/{req.order_id}"
            
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
        "message": "Handoff requested; web MVP cannot transfer calls yet. Ask user to call restaurant directly."
    }

@app.get("/orders")
def get_orders_dashboard(restaurant_id: Optional[str] = None):
    try:
        query = supabase.table("orders").select("*").order("created_at", desc=True)
        if restaurant_id:
            query = query.eq("restaurant_id", restaurant_id)
        return query.execute().data
    except:
        return []

@app.get("/calls")
def get_calls_dashboard(restaurant_id: Optional[str] = None):
    try:
        return supabase.table("call_logs").select("*").order("created_at", desc=True).execute().data
    except:
        return []

@app.get("/stats")
def get_stats():
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
            "callsToday": calls_count + 5, # Mock baseline
            "ordersToday": len(orders),
            "revenue": revenue,
            "avgOrderValue": revenue / len(confirmed_orders) if confirmed_orders else 0,
            "conversionRate": 0,
            "avgCallDuration": "2:34", 
            "fallbackRate": 0,
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {}

if __name__ == "__main__":
    import uvicorn
    # Using port 8001 as configured in environment
    uvicorn.run(app, host="0.0.0.0", port=8001)
