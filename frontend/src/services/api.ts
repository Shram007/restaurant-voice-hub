const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

const getSelectedRestaurantId = () =>
  localStorage.getItem("selected_restaurant_id") || "demo_restaurant";

export const api = {
  getOrders: async (
    range: string = "today",
    restaurantId: string = getSelectedRestaurantId(),
    status?: string,
    startDate?: string,
    endDate?: string
  ) => {
    const params = new URLSearchParams({
      range,
      restaurant_id: restaurantId,
    });

    if (status && status !== "all") params.set("status", status);
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);

    const response = await fetch(`${API_URL}/orders?${params.toString()}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch orders");
    const data = await response.json();
    return data.map((order: any) => ({
      ...order,
      id: order.order_id,
      items: Array.isArray(order.items)
        ? order.items.map((i: any) => `${i.quantity}x ${i.name || i.item_id}`).join(", ")
        : order.items,
      eta: order.status === "confirmed" ? "30 min" : "N/A"
    }));
  },

  getCalls: async (
    range: string = "today",
    restaurantId: string = getSelectedRestaurantId(),
    startDate?: string,
    endDate?: string
  ) => {
    const params = new URLSearchParams({
      range,
      restaurant_id: restaurantId,
    });

    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);

    const response = await fetch(`${API_URL}/calls?${params.toString()}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch calls");
    return response.json();
  },

  getCallDetail: async (
    callId: string,
    restaurantId: string = getSelectedRestaurantId()
  ) => {
    const params = new URLSearchParams({ restaurant_id: restaurantId });
    const response = await fetch(`${API_URL}/calls/${callId}?${params.toString()}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch call details");
    return response.json();
  },

  getStats: async (restaurantId: string = getSelectedRestaurantId()) => {
    const params = new URLSearchParams({ restaurant_id: restaurantId });
    const response = await fetch(`${API_URL}/stats?${params.toString()}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch stats");
    return response.json();
  },

  getMenu: async (restaurantId: string = getSelectedRestaurantId()) => {
    const params = new URLSearchParams({ restaurant_id: restaurantId });
    const response = await fetch(`${API_URL}/menu?${params.toString()}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch menu");
    const data = await response.json();
    // Map backend item_id to frontend id
    return data.map((item: any) => ({
      ...item,
      id: item.item_id,
      available: item.availability // Map backend field to frontend expectation
    }));
  },

  getFaqs: async (restaurantId: string = getSelectedRestaurantId()) => {
    const params = new URLSearchParams({ restaurant_id: restaurantId });
    const response = await fetch(`${API_URL}/faqs?${params.toString()}`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to fetch faqs");
    return response.json();
  },

  saveFaqs: async (faqs: Array<{ id?: string; question: string; answer: string }>, restaurantId: string = getSelectedRestaurantId()) => {
    const params = new URLSearchParams({ restaurant_id: restaurantId });
    const response = await fetch(`${API_URL}/faqs/bulk?${params.toString()}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify(faqs),
    });
    if (!response.ok) throw new Error("Failed to save FAQs");
    return response.json();
  },

  setupRestaurant: async (config: any) => {
    const response = await fetch(`${API_URL}/restaurants/setup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error("Failed to setup restaurant");
    return response.json();
  },

  uploadMenu: async (file: File, restaurantId: string = getSelectedRestaurantId()) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("restaurant_id", restaurantId);
    const response = await fetch(`${API_URL}/menu/upload`, {
      method: "POST",
      body: formData,
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    });
    if (!response.ok) throw new Error("Failed to upload menu");
    return response.json();
  },

  updateItemAvailability: async (itemId: string, available: boolean) => {
    const response = await fetch(`${API_URL}/menu/${itemId}/availability`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify({ available }),
    });
    if (!response.ok) throw new Error("Failed to update availability");
    return response.json();
  },
};
