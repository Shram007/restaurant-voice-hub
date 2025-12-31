from typing import List, Optional
try:
    from backend.database import supabase
    from backend.models import MenuItem, ModifierOption
except ImportError:
    from database import supabase
    from models import MenuItem, ModifierOption

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

def get_orders(restaurant_id: Optional[str] = None):
    try:
        query = supabase.table("orders").select("*").order("created_at", desc=True)
        if restaurant_id:
            query = query.eq("restaurant_id", restaurant_id)
        return query.execute().data
    except:
        return []

def get_call_logs(restaurant_id: Optional[str] = None):
    try:
        # Note: we might want to filter by restaurant_id here too if the table has it
        return supabase.table("call_logs").select("*").order("created_at", desc=True).execute().data
    except:
        return []

def get_faqs_list(restaurant_id: str):
    try:
        response = supabase.table("faqs").select("*").eq("restaurant_id", restaurant_id).execute()
        return response.data
    except Exception as e:
        return []
