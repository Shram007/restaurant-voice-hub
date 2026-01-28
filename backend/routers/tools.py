from fastapi import APIRouter
from backend.models import (
    MenuResponse, OrderCreateRequest, OrderResponse, 
    EtaRequest, EtaResponse, OrderConfirmRequest, OrderConfirmResponse,
    HandoffRequest, HandoffResponse
)
from backend.services.menu_service import MenuService
from backend.services.order_service import OrderService
from backend.config import settings

router = APIRouter(prefix="/tool", tags=["Tools"])

@router.get("/menu_search", response_model=MenuResponse)
def menu_search(restaurant_id: str = settings.DEFAULT_RESTAURANT_ID, query: str = None, limit: int = 20):
    return MenuService.search_menu(restaurant_id, query, limit)

@router.post("/order_create_or_update", response_model=OrderResponse)
def order_create_or_update(req: OrderCreateRequest):
    return OrderService.create_or_update_order(req)

@router.post("/get_eta", response_model=EtaResponse)
def get_eta(req: EtaRequest):
    return OrderService.get_eta(req.restaurant_id)

@router.post("/order_confirm", response_model=OrderConfirmResponse)
def order_confirm(req: OrderConfirmRequest):
    return OrderService.confirm_order(req)

@router.post("/handoff_to_human", response_model=HandoffResponse)
def handoff_to_human(req: HandoffRequest):
    return OrderService.handoff_to_human(req)
