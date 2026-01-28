import io
import csv
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from backend.database import supabase
from backend.models import MenuItem, ModifierOption, MenuResponse

class MenuService:
    @staticmethod
    def get_menu(restaurant_id: str) -> List[MenuItem]:
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

    @staticmethod
    def search_menu(restaurant_id: str, query: Optional[str] = None, limit: int = 20) -> MenuResponse:
        all_items = MenuService.get_menu(restaurant_id)
        
        if not query:
            return MenuResponse(matches=all_items[:limit], notes="Listing full menu")

        matches = []
        q = query.lower()
        for item in all_items:
            if q in item.name.lower() or q in item.category.lower():
                matches.append(item)
            
        return MenuResponse(matches=matches[:limit], notes=f"Found {len(matches)} items for '{query}'")

    @staticmethod
    def update_availability(item_id: str, available: bool):
        try:
            response = supabase.table("menu_items").update({"availability": available}).eq("item_id", item_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Item not found")
            return {"status": "success", "item_id": item_id, "available": available}
        except Exception as e:
            if isinstance(e, HTTPException): raise e
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def upload_menu_csv(file: UploadFile, restaurant_id: str):
        content = await file.read()
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        
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
            # Replace mode: delete existing, insert new
            supabase.table("menu_items").delete().eq("restaurant_id", restaurant_id).execute()
            supabase.table("menu_items").insert(new_items).execute()
            return {"message": f"Uploaded {len(new_items)} items", "items_count": len(new_items)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
