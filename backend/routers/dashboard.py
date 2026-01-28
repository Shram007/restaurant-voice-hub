from fastapi import APIRouter, UploadFile, File, Query
from backend.models import AvailabilityUpdate
from backend.services.menu_service import MenuService
from backend.services.order_service import OrderService
from backend.services.stats_service import StatsService
from backend.config import settings

router = APIRouter(tags=["Dashboard"])

@router.get("/menu")
def get_menu():
    return MenuService.get_menu(settings.DEFAULT_RESTAURANT_ID)

@router.put("/menu/{item_id}/availability")
def update_item_availability(item_id: str, update: AvailabilityUpdate):
    return MenuService.update_availability(item_id, update.available)

@router.post("/menu/upload")
async def upload_menu(file: UploadFile = File(...)):
    return await MenuService.upload_menu_csv(file, settings.DEFAULT_RESTAURANT_ID)

@router.get("/orders")
def get_orders_dashboard(restaurant_id: str = settings.DEFAULT_RESTAURANT_ID, range: str = Query("today")):
    return OrderService.get_orders(restaurant_id)

@router.get("/calls")
def get_calls_dashboard(restaurant_id: str = settings.DEFAULT_RESTAURANT_ID, range: str = Query("today")):
    return StatsService.get_call_logs(restaurant_id)

@router.get("/faqs")
def get_faqs():
    return StatsService.get_faqs_list(settings.DEFAULT_RESTAURANT_ID)

@router.get("/stats")
def get_stats():
    return StatsService.get_stats()
