from pydantic import BaseModel
from typing import List, Optional, Literal

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

class AvailabilityUpdate(BaseModel):
    available: bool
