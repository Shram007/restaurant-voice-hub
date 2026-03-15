from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Query, Form
from backend.models import AvailabilityUpdate, FAQItem
from backend.services.menu_service import MenuService
from backend.services.order_service import OrderService
from backend.services.stats_service import StatsService
from backend.config import settings

router = APIRouter(tags=["Dashboard"])


@router.get("/menu")
def get_menu(restaurant_id: str = settings.DEFAULT_RESTAURANT_ID):
    return MenuService.get_menu(restaurant_id)


@router.put("/menu/{item_id}/availability")
def update_item_availability(item_id: str, update: AvailabilityUpdate):
    return MenuService.update_availability(item_id, update.available)


@router.post("/menu/upload")
async def upload_menu(
    file: UploadFile = File(...),
    restaurant_id: str = Form(settings.DEFAULT_RESTAURANT_ID),
):
    return await MenuService.upload_menu_csv(file, restaurant_id)


@router.get("/orders")
def get_orders_dashboard(
    restaurant_id: str = settings.DEFAULT_RESTAURANT_ID,
    range: str = Query("today"),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    return OrderService.get_orders(restaurant_id, range, status, start_date, end_date)


@router.get("/calls")
def get_calls_dashboard(
    restaurant_id: str = settings.DEFAULT_RESTAURANT_ID,
    range: str = Query("today"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    return StatsService.get_call_logs(restaurant_id, range, start_date, end_date)


@router.get("/calls/{call_id}")
def get_call_detail(call_id: str, restaurant_id: str = settings.DEFAULT_RESTAURANT_ID):
    return StatsService.get_call_detail(call_id, restaurant_id)


@router.get("/faqs")
def get_faqs(restaurant_id: str = settings.DEFAULT_RESTAURANT_ID):
    return StatsService.get_faqs_list(restaurant_id)


@router.put("/faqs/bulk")
def bulk_update_faqs(
    faqs: List[FAQItem],
    restaurant_id: str = settings.DEFAULT_RESTAURANT_ID,
):
    return StatsService.bulk_replace_faqs(restaurant_id, [f.dict() for f in faqs])


@router.get("/stats")
def get_stats(restaurant_id: str = settings.DEFAULT_RESTAURANT_ID):
    return StatsService.get_stats(restaurant_id)
