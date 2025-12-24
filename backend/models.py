from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class RestaurantConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    business_rules: str  # JSON string or text

class MenuItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    price: float
    available: bool = True

class Order(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    customer_name: str
    phone: str
    items: str  # Description or JSON string
    total: float
    status: str
    eta: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Call(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    duration: str
    outcome: str
    transfer_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phone: str

class CallEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    call_id: str
    event_type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FAQ(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    answer: str
