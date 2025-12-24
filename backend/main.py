from fastapi import FastAPI, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, func
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime, timedelta
from database import engine, create_db_and_tables, get_session
from models import RestaurantConfig, MenuItem, Order, Call, CallEvent, FAQ
import uuid

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Seed data if empty
    with Session(engine) as session:
        if session.exec(select(MenuItem)).first() is None:
            seed_data(session)

def seed_data(session: Session):
    # Add initial items for demo
    items = [
        MenuItem(name="Margherita Pizza", category="Pizza", price=16.99),
        MenuItem(name="Pepperoni Pizza", category="Pizza", price=18.99),
        MenuItem(name="Pasta Carbonara", category="Pasta", price=14.99),
        MenuItem(name="Caesar Salad", category="Salads", price=11.99),
    ]
    for item in items:
        session.add(item)
    
    # Add some initial orders
    orders = [
        Order(id="ORD-001", customer_name="Sarah Johnson", phone="(555) 123-4567", items="2x Margherita Pizza", total=33.98, status="confirmed", eta="25 min"),
        Order(id="ORD-002", customer_name="Mike Chen", phone="(555) 234-5678", items="1x Pepperoni Pizza", total=18.99, status="in_progress", eta="15 min"),
    ]
    for order in orders:
        session.add(order)
        
    # Add some calls
    calls = [
        Call(id="CALL-001", duration="3:24", outcome="order", phone="(555) 123-4567"),
        Call(id="CALL-002", duration="1:15", outcome="faq", phone="(555) 234-5678"),
    ]
    for call in calls:
        session.add(call)
        
    # Add FAQs
    faqs = [
        FAQ(question="What are your hours?", answer="11 AM to 10 PM daily."),
        FAQ(question="Do you deliver?", answer="Yes, within 5 miles."),
    ]
    for faq in faqs:
        session.add(faq)

    session.commit()

@app.post("/restaurants/setup")
def setup_restaurant(config: RestaurantConfig, session: Session = Depends(get_session)):
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

@app.post("/menu/upload")
async def upload_menu(file: UploadFile = File(...), session: Session = Depends(get_session)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    # Expected columns: name, category, price, available
    for _, row in df.iterrows():
        item = MenuItem(
            name=row['name'],
            category=row['category'],
            price=float(row['price']),
            available=bool(row.get('available', True))
        )
        session.add(item)
    session.commit()
    return {"message": f"Uploaded {len(df)} items"}

@app.get("/menu", response_model=List[MenuItem])
def get_menu(session: Session = Depends(get_session)):
    return session.exec(select(MenuItem)).all()

@app.get("/faqs", response_model=List[FAQ])
def get_faqs(session: Session = Depends(get_session)):
    return session.exec(select(FAQ)).all()

@app.get("/orders", response_model=List[Order])
def get_orders(range: str = "today", session: Session = Depends(get_session)):
    statement = select(Order)
    if range == "today":
        today = datetime.utcnow().date()
        statement = statement.where(func.date(Order.timestamp) == today)
    # Add month/custom logic as needed
    return session.exec(statement).all()

@app.get("/calls", response_model=List[Call])
def get_calls(range: str = "today", session: Session = Depends(get_session)):
    statement = select(Call)
    if range == "today":
        today = datetime.utcnow().date()
        statement = statement.where(func.date(Call.timestamp) == today)
    return session.exec(statement).all()

@app.post("/orders", response_model=Order)
def create_order(order: Order, session: Session = Depends(get_session)):
    if not order.id:
        order.id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@app.post("/call-events")
def add_call_event(event: CallEvent, session: Session = Depends(get_session)):
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@app.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    # Simple stats for dashboard
    today = datetime.utcnow().date()
    calls_today = session.exec(select(func.count(Call.id)).where(func.date(Call.timestamp) == today)).one()
    orders_today = session.exec(select(func.count(Order.id)).where(func.date(Order.timestamp) == today)).one()
    revenue_today = session.exec(select(func.sum(Order.total)).where(func.date(Order.timestamp) == today)).one() or 0
    
    return {
        "aiStatus": "online",
        "callsToday": calls_today,
        "ordersToday": orders_today,
        "revenue": revenue_today,
        "avgOrderValue": revenue_today / orders_today if orders_today > 0 else 0,
        "conversionRate": (orders_today / calls_today * 100) if calls_today > 0 else 0,
        "avgCallDuration": "2:34", # Mocked for now
        "fallbackRate": 12, # Mocked for now
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
