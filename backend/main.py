from fastapi import FastAPI, HTTPException, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime, timedelta
import uuid
import io
import csv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
MENUS: Dict[str, List['MenuItem']] = {}
ORDERS: Dict[str, Dict[str, Any]] = {}
CALL_LOGS: List[Dict[str, Any]] = []

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

# Helper to seed menu
def get_or_seed_menu(restaurant_id: str) -> List[MenuItem]:
    if restaurant_id not in MENUS:
        MENUS[restaurant_id] = [
            MenuItem(
                item_id="b1",
                name="Classic Cheeseburger",
                category="Burgers",
                price=11.99,
                availability=True,
                modifiers=[
                    ModifierOption(name="Cheese", options=["American", "Cheddar", "Swiss", "No cheese"]),
                    ModifierOption(name="Cooking", options=["Medium", "Medium Rare", "Well Done"])
                ]
            ),
             MenuItem(
                item_id="p1",
                name="Margherita Pizza",
                category="Pizza",
                price=14.99,
                availability=True,
                modifiers=[]
            ),
            MenuItem(
                item_id="d1",
                name="Cola",
                category="Drinks",
                price=2.50,
                availability=True,
                modifiers=[]
            )
        ]
    return MENUS[restaurant_id]

@app.get("/health")
def health_check():
    return {"ok": True, "time": datetime.now().isoformat()}

@app.get("/tool/menu_search", response_model=MenuResponse)
def menu_search(restaurant_id: str = "rest_123", query: Optional[str] = None, limit: int = 20):
    menu = get_or_seed_menu(restaurant_id)
    matches = []
    
    if query:
        q = query.lower()
        for item in menu:
            if q in item.name.lower() or q in item.category.lower():
                matches.append(item)
        return {"matches": matches[:limit], "notes": f"Found {len(matches)} items for '{query}'"}
    else:
        # Return all items if no query
        return {"matches": menu[:limit], "notes": "Listing full menu"}

@app.post("/menu/upload")
async def upload_menu(file: UploadFile = File(...)):
    # Simple CSV parser for MVP
    # Expected columns: name, category, price
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    
    restaurant_id = "default_restaurant" # In MVP, we might assume a default or pass it as query param
    # For better UX, let's assume this upload updates the 'rest_123' or first restaurant we see,
    # or just a hardcoded default for now since the UI doesn't pass restaurant_id in upload usually without extra config.
    # Let's use a fixed ID for the demo if not provided.
    
    new_items = []
    for row in reader:
        # Generate a simple ID
        item_id = str(uuid.uuid4())[:8]
        new_items.append(MenuItem(
            item_id=item_id,
            name=row.get("name", "Unknown"),
            category=row.get("category", "General"),
            price=float(row.get("price", 0.0)),
            availability=True,
            modifiers=[] # CSV doesn't support complex modifiers easily, defaulting to empty
        ))
    
    # Update memory
    MENUS["default"] = new_items
    # Also update 'rest_123' for compatibility if that's what we use
    MENUS["rest_123"] = new_items
    
    return {"message": f"Uploaded {len(new_items)} items", "items_count": len(new_items)}

@app.get("/menu")
def get_menu():
    # Return default menu for dashboard
    return get_or_seed_menu("rest_123")

class AvailabilityUpdate(BaseModel):
    available: bool

@app.put("/menu/{item_id}/availability")
def update_item_availability(item_id: str, update: AvailabilityUpdate):
    # Search in all menus for simplicity in MVP, or default restaurant
    found = False
    for menu_list in MENUS.values():
        for item in menu_list:
            if item.item_id == item_id:
                item.availability = update.available
                found = True
    
    if not found:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"status": "success", "item_id": item_id, "available": update.available}

@app.get("/faqs")
def get_faqs():
    # Return empty list for now as we don't have FAQS storage in MVP yet
    return []

@app.post("/tool/order_create_or_update", response_model=OrderResponse)
def order_create_or_update(req: OrderCreateRequest):
    menu = get_or_seed_menu(req.restaurant_id)
    menu_map = {item.item_id: item for item in menu}
    
    order_id = req.order_id or str(uuid.uuid4())
    
    # Validation
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
            
        # Validate modifiers
        for mod in item.modifier_selections:
            # Simple check if modifier name exists in item
            valid_mod = False
            for m_opt in menu_item.modifiers:
                if m_opt.name == mod.modifier_name:
                    if mod.option in m_opt.options:
                        valid_mod = True
                    break
            if not valid_mod:
                validation_errors.append(f"Invalid modifier {mod.modifier_name}: {mod.option} for {menu_item.name}")
        
        subtotal += menu_item.price * item.quantity
        valid_items.append({
            **item.dict(),
            "name": menu_item.name
        })

    tax = subtotal * 0.08875
    total = subtotal + tax
    
    status = "draft"
    if order_id in ORDERS:
        status = ORDERS[order_id]["status"]
    
    # Missing fields
    missing = []
    if not req.customer_name: missing.append("customer_name")
    if not req.phone: missing.append("phone")
    if not req.items: missing.append("items")
    
    # Save to memory
    ORDERS[order_id] = {
        "restaurant_id": req.restaurant_id,
        "call_id": req.call_id,
        "order_id": order_id,
        "fulfillment": req.fulfillment,
        "customer_name": req.customer_name,
        "phone": req.phone,
        "items": valid_items,
        "notes": req.notes,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "status": status,
        "created_at": datetime.now()
    }
    
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
    # Count confirmed orders in last 60 mins
    now = datetime.now()
    recent_orders = [
        o for o in ORDERS.values() 
        if o["restaurant_id"] == restaurant_id 
        and o["status"] == "confirmed"
        and o["created_at"] > now - timedelta(minutes=60)
    ]
    adjustment = min(len(recent_orders) * 2, 30) # Cap adjustment
    return base_eta + adjustment

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
    if req.order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = ORDERS[req.order_id]
    
    # Validate required fields
    if not order["customer_name"] or not order["phone"] or not order["items"]:
        raise HTTPException(status_code=400, detail="Missing required fields for confirmation")
        
    order["status"] = "confirmed"
    ORDERS[req.order_id] = order
    
    eta = calculate_eta(req.restaurant_id)
    
    payment_link = None
    if req.payment_mode == "payment_link":
        payment_link = f"https://example.com/pay/{req.order_id}"
        
    # POS Integration Placeholder:
    # 1. Initialize Square/Clover client
    # 2. Map internal order items to POS item IDs
    # 3. Create order in POS: pos_client.create_order(...)
    # 4. Save pos_order_id to order record
    
    return {
        "confirmed": True,
        "order_id": req.order_id,
        "total": round(order["total"], 2),
        "pickup_eta_minutes": eta,
        "payment_link": payment_link,
        "pos_provider": "none",
        "pos_order_id": None
    }

@app.post("/tool/handoff_to_human", response_model=HandoffResponse)
def handoff_to_human(req: HandoffRequest):
    CALL_LOGS.append({
        "type": "handoff",
        "timestamp": datetime.now(),
        "data": req.dict()
    })
    return {
        "transferred": False,
        "message": "Handoff requested; web MVP cannot transfer calls yet. Ask user to call restaurant directly."
    }

@app.get("/orders")
def get_orders_dashboard(restaurant_id: Optional[str] = None):
    if restaurant_id:
        return [o for o in ORDERS.values() if o["restaurant_id"] == restaurant_id]
    return list(ORDERS.values())

@app.get("/calls")
def get_calls_dashboard(restaurant_id: Optional[str] = None):
    # In MVP, just return handoff logs or empty
    return CALL_LOGS

# Keep existing stats endpoint for dashboard compatibility if needed, 
# or implement a simple one based on memory
@app.get("/stats")
def get_stats():
    # Simple stats for dashboard
    today = datetime.now().date()
    orders_today = [o for o in ORDERS.values() if o["created_at"].date() == today]
    revenue = sum(o["total"] for o in orders_today if o["status"] == "confirmed")
    
    return {
        "aiStatus": "online",
        "callsToday": len(CALL_LOGS) + 5, # Mock + real
        "ordersToday": len(orders_today),
        "revenue": revenue,
        "avgOrderValue": revenue / len(orders_today) if orders_today else 0,
        "conversionRate": 0,
        "avgCallDuration": "2:34", 
        "fallbackRate": 0,
    }

if __name__ == "__main__":
    import uvicorn
    # Using port 8001 as configured in environment
    uvicorn.run(app, host="0.0.0.0", port=8001)
