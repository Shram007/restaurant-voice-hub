import requests
import json
import uuid

BASE_URL = "http://localhost:8001"
RESTAURANT_ID = "rest_123"
CALL_ID = "call_test_" + str(uuid.uuid4())[:8]

def print_response(name, response):
    print(f"\n--- {name} ---")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

# 1. Search Menu
print("1. Searching Menu...")
response = requests.get(f"{BASE_URL}/tool/menu_search", params={
    "restaurant_id": RESTAURANT_ID,
    "query": "Chicken"
})
print_response("Menu Search", response)
if response.status_code == 200 and response.json()["matches"]:
    burger_id = response.json()["matches"][0]["item_id"]
else:
    print("Error: Could not find item")
    burger_id = "unknown"

# 2. Create Order
print("\n2. Creating Order...")
# Note: The uploaded menu items don't have modifiers, so we'll send empty modifiers
order_payload = {
    "restaurant_id": RESTAURANT_ID,
    "call_id": CALL_ID,
    "items": [
        {
            "item_id": burger_id,
            "quantity": 2,
            "modifier_selections": [] 
        }
    ],
    "customer_name": "John Doe",
    "phone": "555-0123"
}
response = requests.post(f"{BASE_URL}/tool/order_create_or_update", json=order_payload)
print_response("Create Order", response)

if response.status_code == 200:
    order_id = response.json()["order_id"]
    
    # 3. Get ETA
    print("\n3. Getting ETA...")
    response = requests.post(f"{BASE_URL}/tool/get_eta", json={
        "restaurant_id": RESTAURANT_ID,
        "order_id": order_id
    })
    print_response("Get ETA", response)
    
    # 4. Confirm Order
    print("\n4. Confirming Order...")
    response = requests.post(f"{BASE_URL}/tool/order_confirm", json={
        "restaurant_id": RESTAURANT_ID,
        "order_id": order_id,
        "payment_mode": "pay_at_pickup"
    })
    print_response("Confirm Order", response)
